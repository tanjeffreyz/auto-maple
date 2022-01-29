"""A module for tracking useful in-game information."""

import config
import utils
import mss
import mss.windows
import time
import cv2
import threading
import numpy as np


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

    def __init__(self):
        """Initializes this Capture object's main thread."""

        config.capture = self

        self.frame = None
        self.minimap = {}
        self.minimap_ratio = 1
        self.minimap_sample = None

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

        mss.windows.CAPTUREBLT = 0
        with mss.mss() as sct:
            while True:
                self.frame = np.array(sct.grab(config.MONITOR))

                if not self.calibrated:
                    # Calibrate by finding the bottom right corner of the minimap
                    _, br = utils.single_match(self.frame[:round(self.frame.shape[0] / 4),
                                               :round(self.frame.shape[1] / 3)],
                                               MINIMAP_TEMPLATE)
                    mm_tl = (MINIMAP_BOTTOM_BORDER, MINIMAP_TOP_BORDER)
                    mm_br = tuple(max(75, a - MINIMAP_BOTTOM_BORDER) for a in br)
                    self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                    self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    self.calibrated = True

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
