"""A module for tracking useful in-game information."""

import time
import cv2
import threading
import ctypes
import numpy as np
from src.common import config, utils
from ctypes import wintypes
from PIL import ImageGrab
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()


# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 8

# Offset in pixels to adjust for windowed mode
WINDOWED_OFFSET_TOP = 36
WINDOWED_OFFSET_LEFT = 10

# The top-left and bottom-right corners of the minimap
MM_TL_TEMPLATE = cv2.imread('assets/minimap_tl_template.png', 0)
MM_BR_TEMPLATE = cv2.imread('assets/minimap_br_template.png', 0)

MMT_HEIGHT = max(MM_TL_TEMPLATE.shape[0], MM_BR_TEMPLATE.shape[0])
MMT_WIDTH = max(MM_TL_TEMPLATE.shape[1], MM_BR_TEMPLATE.shape[1])

# The player's symbol on the minimap
PLAYER_TEMPLATE = cv2.imread('assets/player_template.png', 0)
PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape


class Capture:
    """
    A class that tracks player position and various in-game events. It constantly updates
    the config module with information regarding these events. It also annotates and
    displays the minimap in a pop-up window.
    """

    def __init__(self):
        """Initializes this Capture object's main thread."""

        config.capture = self

        self.frame = None
        self.minimap = {}
        self.minimap_ratio = 1
        self.minimap_sample = None
        self.window = (0, 0, 1366, 768)
        self.scale = 1.0

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
                handle = user32.FindWindowW(None, 'MapleStory')
                rect = wintypes.RECT()
                user32.GetWindowRect(handle, ctypes.pointer(rect))
                rect = (rect.left, rect.top, rect.right, rect.bottom)
                rect = tuple(max(0, x) for x in rect)

                # Preliminary window to template match minimap
                self.scale = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
                self.window = (
                    rect[0],
                    rect[1],
                    max(rect[2], rect[0] + MMT_WIDTH),     # Make room for minimap templates
                    max(rect[3], rect[1] + MMT_HEIGHT)
                )

                # Calibrate by finding the bottom right corner of the minimap
                self.frame = np.array(ImageGrab.grab(self.window))
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
                tl, _ = utils.single_match(self.frame, MM_TL_TEMPLATE)
                _, br = utils.single_match(self.frame, MM_BR_TEMPLATE)
                mm_tl = (
                    tl[0] + MINIMAP_BOTTOM_BORDER,
                    tl[1] + MINIMAP_TOP_BORDER
                )
                mm_br = (
                    max(mm_tl[0] + PT_WIDTH, br[0] - MINIMAP_BOTTOM_BORDER),
                    max(mm_tl[1] + PT_HEIGHT, br[1] - MINIMAP_BOTTOM_BORDER - 1)
                )

                # Resize window to encompass minimap if needed
                self.window = (
                    rect[0],
                    rect[1],
                    max(rect[2], mm_br[0]),
                    max(rect[3], mm_br[1])
                )
                self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                self.calibrated = True

            # Take screenshot
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
