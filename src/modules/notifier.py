"""A module for detecting and notifying the user of dangerous in-game events."""

from src.common import config, utils
import time
import os
import cv2
import pygame
import threading
import numpy as np
import keyboard as kb
from src.routine.components import Point


# A rune's symbol on the minimap
RUNE_RANGES = (
    ((141, 148, 245), (146, 158, 255)),
)
rune_filtered = utils.filter_color(cv2.imread('assets/rune_template.png'), RUNE_RANGES)
RUNE_TEMPLATE = cv2.cvtColor(rune_filtered, cv2.COLOR_BGR2GRAY)

# Other players' symbols on the minimap
OTHER_RANGES = (
    ((0, 245, 215), (10, 255, 255)),
)
other_filtered = utils.filter_color(cv2.imread('assets/other_template.png'), OTHER_RANGES)
OTHER_TEMPLATE = cv2.cvtColor(other_filtered, cv2.COLOR_BGR2GRAY)

# The Elite Boss's warning sign
ELITE_TEMPLATE = cv2.imread('assets/elite_template.jpg', 0)


def get_alert_path(name):
    return os.path.join(Notifier.ALERTS_DIR, f'{name}.mp3')


class Notifier:
    ALERTS_DIR = os.path.join('assets', 'alerts')

    def __init__(self):
        """Initializes this Notifier object's main thread."""

        pygame.mixer.init()
        self.mixer = pygame.mixer.music

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

        self.room_change_threshold = 0.9
        self.rune_alert_delay = 270         # 4.5 minutes

    def start(self):
        """Starts this Notifier's thread."""

        print('\n[~] Started notifier')
        self.thread.start()

    def _main(self):
        self.ready = True
        prev_others = 0
        rune_start_time = time.time()
        while True:
            if config.enabled:
                frame = config.capture.frame
                height, width, _ = frame.shape
                minimap = config.capture.minimap['minimap']

                # Check for unexpected black screen
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if np.count_nonzero(gray < 15) / height / width > self.room_change_threshold:
                    self._alert('siren')

                # Check for elite warning
                elite_frame = frame[height // 4:3 * height // 4, width // 4:3 * width // 4]
                elite = utils.multi_match(elite_frame, ELITE_TEMPLATE, threshold=0.9)
                if len(elite) > 0:
                    self._alert('siren')

                # Check for other players entering the map
                filtered = utils.filter_color(minimap, OTHER_RANGES)
                others = len(utils.multi_match(filtered, OTHER_TEMPLATE, threshold=0.5))
                config.stage_fright = others > 0
                if others != prev_others:
                    if others > prev_others:
                        self._ping('ding')
                    prev_others = others

                # Check for rune
                now = time.time()
                if not config.bot.rune_active:
                    filtered = utils.filter_color(minimap, RUNE_RANGES)
                    matches = utils.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)
                    rune_start_time = now
                    if matches and config.routine.sequence:
                        abs_rune_pos = (matches[0][0], matches[0][1])
                        config.bot.rune_pos = utils.convert_to_relative(abs_rune_pos, minimap)
                        distances = list(map(distance_to_rune, config.routine.sequence))
                        index = np.argmin(distances)
                        config.bot.rune_closest_pos = config.routine[index].location
                        config.bot.rune_active = True
                        self._ping('rune_appeared', volume=0.75)
                elif now - rune_start_time > self.rune_alert_delay:     # Alert if rune hasn't been solved
                    config.bot.rune_active = False
                    self._alert('siren')
            time.sleep(0.05)

    def _alert(self, name, volume=0.75):
        """
        Plays an alert to notify user of a dangerous event. Stops the alert
        once the key bound to 'Start/stop' is pressed.
        """

        config.enabled = False
        config.listener.enabled = False
        self.mixer.load(get_alert_path(name))
        self.mixer.set_volume(volume)
        self.mixer.play(-1)
        while not kb.is_pressed(config.listener.config['Start/stop']):
            time.sleep(0.1)
        self.mixer.stop()
        time.sleep(2)
        config.listener.enabled = True

    def _ping(self, name, volume=0.5):
        """A quick notification for non-dangerous events."""

        self.mixer.load(get_alert_path(name))
        self.mixer.set_volume(volume)
        self.mixer.play()


#################################
#       Helper Functions        #
#################################
def distance_to_rune(point):
    """
    Calculates the distance from POINT to the rune.
    :param point:   The position to check.
    :return:        The distance from POINT to the rune, infinity if it is not a Point object.
    """

    if isinstance(point, Point):
        return utils.distance(config.bot.rune_pos, point.location)
    return float('inf')
