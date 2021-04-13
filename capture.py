"""A module for tracking useful in-game information."""

import config
import mss
import cv2
import threading
import numpy as np
from utils import distance
from bot import Point


class Capture:
    """
    A class that tracks player position and various in-game events. It constantly updates
    the config module with information regarding these events. It also annotates and
    displays the minimap in a pop-up window.
    """

    MINIMAP_TOP_BORDER = 21
    MINIMAP_BOTTOM_BORDER = 8
    MINIMAP_TEMPLATE = cv2.imread('assets/minimap_template.jpg', 0)
    PLAYER_TEMPLATE = cv2.imread('assets/player_template.png', 0)
    RUNE_TEMPLATE = cv2.imread('assets/rune_template.png', 0)
    RUNE_BUFF_TEMPLATE = cv2.imread('assets/rune_buff_template.jpg', 0)
    ELITE_TEMPLATE = cv2.imread('assets/elite_template.jpg', 0)

    def __init__(self):
        """Initializes this Capture object's main thread."""

        self.thread = threading.Thread(target=Capture._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts this Capture's thread.
        :return:    None
        """

        print('\nStarted video capture.')
        self.thread.start()

    @staticmethod
    def _main():
        """
        Constantly monitors the player's position and in-game events.
        :return:    None
        """

        with mss.mss() as sct:
            config.ready = True
            while True:
                if not config.calibrated:
                    frame = np.array(sct.grab(config.MONITOR))

                    # Get the bottom right point of the minimap
                    _, br = Capture.single_match(frame[:round(frame.shape[0] / 4),
                                                       :round(frame.shape[1] / 3)],
                                                 Capture.MINIMAP_TEMPLATE)
                    mm_tl = (Capture.MINIMAP_BOTTOM_BORDER, Capture.MINIMAP_TOP_BORDER)
                    mm_br = tuple(max(75, a - Capture.MINIMAP_BOTTOM_BORDER) for a in br)
                    config.mm_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                    config.calibrated = True
                else:
                    frame = np.array(sct.grab(config.MONITOR))
                    height, width, _ = frame.shape

                    # Check for elite warning
                    elite_frame = frame[height//4:3*height//4, width//4:3*width//4]
                    elite = Capture.multi_match(elite_frame, Capture.ELITE_TEMPLATE, threshold=0.9)
                    if config.enabled and not config.elite_active and elite:
                        config.elite_active = True
                        config.enabled = False

                    # Crop the frame to only show the minimap
                    minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    player = Capture.multi_match(minimap, Capture.PLAYER_TEMPLATE, threshold=0.8)
                    if player:
                        config.player_pos = Capture._convert_to_relative(player[0], minimap)

                    # Check for a rune
                    if not config.rune_active:
                        rune = Capture.multi_match(minimap, Capture.RUNE_TEMPLATE, threshold=0.9)
                        if rune and config.sequence:
                            abs_rune_pos = (rune[0][0] - 1, rune[0][1])
                            config.rune_pos = Capture._convert_to_relative(abs_rune_pos, minimap)
                            distances = list(map(Capture._distance_to_rune, config.sequence))
                            config.rune_index = np.argmin(distances)
                            config.rune_active = True

                    # Mark the position of a rune
                    if config.rune_active:
                        cv2.circle(minimap,
                                   Capture._convert_to_absolute(config.rune_pos, minimap),
                                   3,
                                   (219, 112, 147),
                                   -1)

                    # Draw the current path that the program is taking
                    if config.enabled and config.path:
                        for i in range(len(config.path) - 1):
                            start = Capture._convert_to_absolute(config.path[i], minimap)
                            end = Capture._convert_to_absolute(config.path[i + 1], minimap)
                            cv2.line(minimap, start, end, (255, 255, 0), 1)

                    # Draw each Point in the routine as a circle
                    for p in config.sequence:
                        Capture._draw_point(minimap,
                                            p,
                                            (0, 255, 0) if config.enabled else (0, 0, 255))

                    # Display the current Layout
                    if config.layout:
                        config.layout.draw(minimap)

                    # Draw the player's position on top of everything
                    cv2.circle(minimap,
                               Capture._convert_to_absolute(config.player_pos, minimap),
                               3,
                               (255, 0, 0),
                               -1)
                    cv2.imshow('minimap', minimap)
                if cv2.waitKey(1) & 0xFF == 27:     # 27 is ASCII for the Esc key
                    break

    @staticmethod
    def _distance_to_rune(point):
        """
        Calculates the distance from POINT to the rune.
        :param point:   The position to check.
        :return:        The distance from POINT to the rune, infinity if it is not a Point object.
        """

        if isinstance(point, Point):
            return distance(config.rune_pos, point.location)
        return float('inf')

    @staticmethod
    def _draw_point(minimap, point, color):
        """
        Draws a visual representation of POINT onto MINIMAP. The radius of the circle represents
        the allowed error when moving towards POINT.
        :param minimap:     The image on which to draw.
        :param point:       The location of the Point object to depict.
        :param color:       The color of the circle.
        :return:            None
        """

        if isinstance(point, Point):
            height, width, _ = minimap.shape
            loc = (round(width * point.location[0]), round(height * point.location[1]))
            cv2.circle(minimap,
                       loc,
                       round(minimap.shape[1] * config.move_tolerance),
                       color,
                       1)

    @staticmethod
    def _convert_to_relative(point, frame):
        """
        Converts POINT into relative coordinates in the range [0, 1] based on FRAME.
        :param point:   The point in absolute coordinates.
        :param frame:   The image to use as a reference.
        :return:        The given point in relative coordinates.
        """

        return point[0] / frame.shape[1], point[1] / frame.shape[0]

    @staticmethod
    def _convert_to_absolute(point, frame):
        """
        Converts POINT into absolute coordinates (in pixels) based on FRAME.
        :param point:   The point in relative coordinates.
        :param frame:   The image to use as a reference.
        :return:        The given point in absolute coordinates.
        """

        x = int(round(point[0] * frame.shape[1]))
        y = int(round(point[1] * frame.shape[0]))
        return x, y

    @staticmethod
    def rescale_frame(frame, percent=100):
        """
        Proportionally rescales the width and height of FRAME by PERCENT.
        :param frame:       The image to rescale.
        :param percent:     The percentage by which to rescale.
        :return:            The resized image.
        """

        width = int(frame.shape[1] * percent / 100)
        height = int(frame.shape[0] * percent / 100)
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

    @staticmethod
    def single_match(frame, template):
        """
        Finds the best match within FRAME.
        :param frame:       The image in which to search for TEMPLATE.
        :param template:    The template to match with.
        :return:            The top-left and bottom-right positions of the best match.
        """

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF)
        _, _, _, top_left = cv2.minMaxLoc(result)
        w, h = template.shape[::-1]
        bottom_right = (top_left[0] + w, top_left[1] + h)
        return top_left, bottom_right

    @staticmethod
    def multi_match(frame, template, threshold=0.95):
        """
        Finds all matches in FRAME that are similar to TEMPLATE by at least THRESHOLD.
        :param frame:       The image in which to search.
        :param template:    The template to match with.
        :param threshold:   The minimum percentage of TEMPLATE that each result must match.
        :return:            An array of matches that exceed THRESHOLD.
        """

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        results = []
        for p in locations:
            x = int(round(p[0] + template.shape[1] / 2))
            y = int(round(p[1] + template.shape[0] / 2))
            results.append((x, y))
        return results
