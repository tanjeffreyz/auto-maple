"""A module for tracking useful in-game information."""

import time
import cv2
import threading
import ctypes
import mss
import mss.windows
import numpy as np
from src.common import config, utils
from ctypes import wintypes
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()


# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 9

# Offset in pixels to adjust for windowed mode
WINDOWED_OFFSET_TOP = 36
WINDOWED_OFFSET_LEFT = 10

# The top-left and bottom-right corners of the minimap
MM_TL_TEMPLATE = cv2.imread('assets/minimap_tl_template.png', 0)
MM_BR_TEMPLATE = cv2.imread('assets/minimap_br_template.png', 0)

# HP/MP bars
HP_MP_TEMPLATE = cv2.imread('assets/hp.png', 0)
HP_MP_COLOR_X_POT_OFFSET = 160
HP_COLOR_Y_OFFSET = 13
MP_COLOR_Y_OFFSET = 28
COLOR_DIFF_THRESHOLD = 50

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
        self.hp_mp_info = {}
        self.minimap_ratio = 1
        self.minimap_sample = None
        self.sct = None
        self.window = {
            'left': 0,
            'top': 0,
            'width': 1366,
            'height': 768
        }

        self.ready = False
        self.calibrated = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """Starts this Capture's thread."""

        print('\n[~] Started video capture')
        self.thread.start()

    def _main(self):
        """Constantly monitors the player's position and in-game events."""

        mss.windows.CAPTUREBLT = 0
        while True:
            # Calibrate screen capture
            handle = user32.FindWindowW(None, 'MapleStory')
            rect = wintypes.RECT()
            user32.GetWindowRect(handle, ctypes.pointer(rect))
            rect = (rect.left, rect.top, rect.right, rect.bottom)
            rect = tuple(max(0, x) for x in rect)

            self.window['left'] = rect[0]
            self.window['top'] = rect[1]
            self.window['width'] = max(rect[2] - rect[0], MMT_WIDTH)
            self.window['height'] = max(rect[3] - rect[1], MMT_HEIGHT)

            # Calibrate by finding the top-left and bottom-right corners of the minimap
            with mss.mss() as self.sct:
                self.frame = self.screenshot()
            if self.frame is None:
                continue

            top_left, _ = utils.single_match(self.frame, MM_TL_TEMPLATE)
            _, bottom_right = utils.single_match(self.frame, MM_BR_TEMPLATE)
            minimap_top_left = (
                top_left[0] + MINIMAP_BOTTOM_BORDER,
                top_left[1] + MINIMAP_TOP_BORDER
            )
            minimap_bottom_right = (
                max(minimap_top_left[0] + PT_WIDTH, bottom_right[0] - MINIMAP_BOTTOM_BORDER),
                max(minimap_top_left[1] + PT_HEIGHT, bottom_right[1] - MINIMAP_BOTTOM_BORDER)
            )

            self.minimap_ratio = (minimap_bottom_right[0] - minimap_top_left[0]) / (minimap_bottom_right[1] - minimap_top_left[1])
            self.minimap_sample = self.frame[minimap_top_left[1]:minimap_bottom_right[1], minimap_top_left[0]:minimap_bottom_right[0]]

            # Calibrate HP/MP
            hp_top_left, hp_bottom_right = utils.single_match(self.frame, HP_MP_TEMPLATE)

            self.calibrated = True

            with mss.mss() as self.sct:
                while True:
                    if not self.calibrated:
                        break

                    # Take screenshot
                    self.frame = self.screenshot()
                    if self.frame is None:
                        continue

                    # Crop the frame to only show the minimap
                    minimap = self.frame[minimap_top_left[1]:minimap_bottom_right[1], minimap_top_left[0]:minimap_bottom_right[0]]
                    hp = self.frame[hp_top_left[1] + HP_COLOR_Y_OFFSET][hp_top_left[0] + HP_MP_COLOR_X_POT_OFFSET]
                    mp = self.frame[hp_top_left[1] + MP_COLOR_Y_OFFSET][hp_top_left[0] + HP_MP_COLOR_X_POT_OFFSET]

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

                    # Tells whether hp or mp are low
                    #print(f"HP: {hp} {int(hp[2])} -> {abs(int(hp[2]) - 255)} {abs(int(hp[2]) - 255) > COLOR_DIFF_THRESHOLD}")
                    #print(f"MP: {mp} {int(mp[0])} -> {abs(int(mp[0]) - 255)} {abs(int(mp[0]) - 255) > COLOR_DIFF_THRESHOLD}")
                    self.hp_mp_info = {
                        'hp_low': abs(int(hp[2]) - 255) > COLOR_DIFF_THRESHOLD,
                        'mp_low': abs(int(mp[0]) - 255) > COLOR_DIFF_THRESHOLD
                    }

                    if not self.ready:
                        self.ready = True
                    time.sleep(0.001)

    def screenshot(self, delay=1):
        try:
            return np.array(self.sct.grab(self.window))
        except mss.exception.ScreenShotError:
            print(f'\n[!] Error while taking screenshot, retrying in {delay} second'
                  + ('s' if delay != 1 else ''))
            time.sleep(delay)
