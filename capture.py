"""A module for tracking useful in-game information."""

import config
import mss
import mss.windows
import time
import cv2
import threading
import numpy as np
import utils
from components import Point


class Capture:
    """
    A class that tracks player position and various in-game events. It constantly updates
    the config module with information regarding these events. It also annotates and
    displays the minimap in a pop-up window.
    """

    def __init__(self):
        """Initializes this Capture object's main thread."""

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts this Capture's thread.
        :return:    None
        """

        print('\n[~] Started video capture.')
        self.thread.start()

    def _main(self):
        """
        Constantly monitors the player's position and in-game events.
        :return:    None
        """

        mss.windows.CAPTUREBLT = 0
        with mss.mss() as sct:
            while True:
                frame = np.array(sct.grab(config.MONITOR))

                if not config.calibrated:
                    # Calibrate by finding the bottom right corner of the minimap
                    _, br = utils.single_match(frame[:round(frame.shape[0] / 4),
                                                     :round(frame.shape[1] / 3)],
                                               config.MINIMAP_TEMPLATE)
                    mm_tl = (config.MINIMAP_BOTTOM_BORDER, config.MINIMAP_TOP_BORDER)
                    mm_br = tuple(max(75, a - config.MINIMAP_BOTTOM_BORDER) for a in br)
                    config.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                    config.minimap_sample = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    config.calibrated = True

                # frame = np.array(sct.grab(config.MONITOR))
                height, width, _ = frame.shape

                # Check for unexpected black screen regardless of whether bot is enabled
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if config.enabled and not config.alert_active \
                        and np.count_nonzero(gray < 15) / height / width > 0.95:
                    config.alert_active = True
                    config.enabled = False

                # Check for elite warning
                elite_frame = frame[height//4:3*height//4, width//4:3*width//4]
                elite = utils.multi_match(elite_frame, config.ELITE_TEMPLATE, threshold=0.9)
                if config.enabled and not config.alert_active and elite:
                    config.alert_active = True
                    config.enabled = False

                # Crop the frame to only show the minimap
                minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]

                # Determine the player's position
                player = utils.multi_match(minimap, config.PLAYER_TEMPLATE, threshold=0.8)
                if player:
                    config.player_pos = utils.convert_to_relative(player[0], minimap)

                # Check for a rune
                if not config.rune_active:
                    rune = utils.multi_match(minimap, config.RUNE_TEMPLATE, threshold=0.9)
                    if rune and config.routine.sequence:
                        abs_rune_pos = (rune[0][0] - 1, rune[0][1])
                        config.rune_pos = utils.convert_to_relative(abs_rune_pos, minimap)
                        distances = list(map(Capture._distance_to_rune, config.routine.sequence))
                        index = np.argmin(distances)
                        config.rune_closest_pos = config.routine[index].location
                        config.rune_active = True

                # Package display information to be polled by GUI
                config.minimap = {
                    'minimap': minimap,
                    'rune_active': config.rune_active,
                    'rune_pos': config.rune_pos,
                    'path': config.path,
                    'player_pos': config.player_pos
                }

                if not self.ready:
                    self.ready = True
                time.sleep(0.001)

    @staticmethod
    def _count(frame, threshold):
        """
        Counts the number of pixels in FRAME that are less than or equal to THRESHOLD.
        Two pixels are compared by their corresponding tuple elements in order.
        :param frame:       The image in which to search.
        :param threshold:   The pixel value to compare to.
        :return:            The number of pixels in FRAME that are below THRESHOLD.
        """

        count = 0
        for row in frame:
            for col in row:
                pixel = frame[row][col]
                if len(pixel) == len(threshold):
                    valid = True
                    for i in range(len(pixel)):
                        valid = valid and frame[i] <= threshold[i]
                    if valid:
                        count += 1
        return count

    @staticmethod
    def _distance_to_rune(point):
        """
        Calculates the distance from POINT to the rune.
        :param point:   The position to check.
        :return:        The distance from POINT to the rune, infinity if it is not a Point object.
        """

        if isinstance(point, Point):
            return utils.distance(config.rune_pos, point.location)
        return float('inf')
