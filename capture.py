"""A module for tracking useful in-game information."""

import config
import utils
import time
import cv2
import threading
import ctypes
import numpy as np
from ctypes import wintypes
from PIL import ImageGrab
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()


# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 21

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 8

# The bottom right corner of the minimap
MINIMAP_TEMPLATE = cv2.imread('assets/minimap_template.jpg', 0)

# The player's symbol on the minimap
PLAYER_TEMPLATE = cv2.imread('assets/player_template.png', 0)


class Capture:
    """
    A class that tracks player position and various in-game events. It constantly updates
    the config module with information regarding these events. It also annotates and
    displays the minimap in a pop-up window.
    """

    WINDOWED_OFFSET_TOP = 31
    WINDOWED_OFFSET_BOTTOM = 8

    def __init__(self):
        """Initializes this Capture object's main thread."""

        config.capture = self

        self.frame = None
        self.minimap = {}
        self.minimap_ratio = 1
        self.minimap_sample = None
        self.window = (0, 0, 1366, 768)

        self.ready = False
        self.calibrated = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """Starts this Capture's thread."""

        print('\n[~] Started video capture.')
        self.thread.start()

    def _main(self):
        """Constantly monitors the player's position and in-game events."""

        while True:
            if not self.calibrated:
                full_dim = (0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
                handle = user32.FindWindowW(None, 'MapleStory')
                rect = wintypes.RECT()
                user32.GetWindowRect(handle, ctypes.pointer(rect))
                self.window = (rect.left, rect.top, rect.right, rect.bottom)
                full_screen = self.window == full_dim

                # Calibrate by finding the bottom right corner of the minimap
                self.frame = np.array(ImageGrab.grab(self.window))
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
                _, br = utils.single_match(self.frame[:round(self.frame.shape[0] / 4),
                                           :round(self.frame.shape[1] / 3)],
                                           MINIMAP_TEMPLATE)
                if full_screen:
                    mm_tl = (MINIMAP_BOTTOM_BORDER, MINIMAP_TOP_BORDER)
                else:
                    mm_tl = (
                        MINIMAP_BOTTOM_BORDER + Capture.WINDOWED_OFFSET_BOTTOM,
                        MINIMAP_TOP_BORDER + Capture.WINDOWED_OFFSET_TOP
                    )
                mm_br = tuple(max(75, a - MINIMAP_BOTTOM_BORDER) for a in br)
                self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                self.calibrated = True
            else:
                self.frame = np.array(ImageGrab.grab(self.window))
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)

            # Crop the frame to only show the minimap
            minimap = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]

            # Determine the player's position
            player = utils.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)
            if player:
                config.player_pos = utils.convert_to_relative(player[0], minimap)

            # Package display information to be polled by GUI
            self.minimap = {
                'minimap': minimap,
                'rune_active': config.bot.rune_active,
                'rune_pos': config.bot.rune_pos,
                'path': config.path,
                'player_pos': config.player_pos
            }

            if not self.ready:
                self.ready = True
            time.sleep(0.001)
