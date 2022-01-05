"""A collection of functions and classes used across multiple modules."""

import config
import math
import queue
import cv2
import threading
import numpy as np
from random import random

import settings


def run_if_enabled(function):
    """
    Decorator for functions that should only run if the bot is enabled.
    :param function:    The function to decorate.
    :return:            The decorated function.
    """

    def helper(*args, **kwargs):
        if config.enabled:
            return function(*args, **kwargs)
    return helper


def run_if_disabled(message=''):
    """
    Decorator for functions that should only run while the bot is disabled. If MESSAGE
    is not empty, it will also print that message if its function attempts to run when
    it is not supposed to.
    """

    def decorator(function):
        def helper(*args, **kwargs):
            if not config.enabled:
                return function(*args, **kwargs)
            elif message:
                print(message)
        return helper
    return decorator


def reset_settings():
    """
    Resets all settings to their default values.
    :return:    None
    """

    settings.move_tolerance = 0.1
    settings.adjust_tolerance = 0.01
    settings.record_layout = False
    settings.buff_cooldown = 180


def distance(a, b):
    """
    Applies the distance formula to two points.
    :param a:   The first point.
    :param b:   The second point.
    :return:    The distance between the two points.
    """

    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def separate_args(arguments):
    """
    Separates a given array ARGUMENTS into an array of normal arguments and a
    dictionary of keyword arguments.
    :param arguments:    The array of arguments to separate.
    :return:             An array of normal arguments and a dictionary of keyword arguments.
    """

    arguments = [s.strip() for s in arguments]
    args = []
    kwargs = {}
    for a in arguments:
        index = a.find('=')
        if index > -1:
            key = a[:index].strip()
            value = a[index+1:].strip()
            kwargs[key] = value
        else:
            args.append(a)
    return args, kwargs


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


def convert_to_relative(point, frame):
    """
    Converts POINT into relative coordinates in the range [0, 1] based on FRAME.
    Normalizes the units of the vertical axis to equal those of the horizontal
    axis by using config.mm_ratio.
    :param point:   The point in absolute coordinates.
    :param frame:   The image to use as a reference.
    :return:        The given point in relative coordinates.
    """

    x = point[0] / frame.shape[1]
    y = point[1] / config.mm_ratio / frame.shape[0]
    return x, y


def convert_to_absolute(point, frame):
    """
    Converts POINT into absolute coordinates (in pixels) based on FRAME.
    Normalizes the units of the vertical axis to equal those of the horizontal
    axis by using config.mm_ratio.
    :param point:   The point in relative coordinates.
    :param frame:   The image to use as a reference.
    :return:        The given point in absolute coordinates.
    """

    x = int(round(point[0] * frame.shape[1]))
    y = int(round(point[1] * config.mm_ratio * frame.shape[0]))
    return x, y


def print_separator():
    """
    Prints a 3 blank lines for visual clarity.
    :return:    None
    """

    print('\n\n')


def closest_point(points, target):
    """
    Returns the point in POINTS that is closest to TARGET.
    :param points:      A list of points to check.
    :param target:      The point to check against.
    :return:            The point closest to TARGET, otherwise None if POINTS is empty.
    """

    if points:
        points.sort(key=lambda p: distance(p, target))
        return points[0]


def bernoulli(p):
    """
    Returns the value of a Bernoulli random variable with probability P.
    :param p:   The random variable's probability of being True.
    :return:    True or False.
    """

    return random() < p


##########################
#       Threading        #
##########################
class Async(threading.Thread):
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.queue = queue.Queue()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.function(*self.args, **self.kwargs)
        self.queue.put('x')

    def process_queue(self, root):
        def f():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                root.after(100, self.process_queue(root))
        return f


def async_callback(context, function, *args, **kwargs):
    def f():
        task = Async(function, *args, **kwargs)
        task.start()
        context.after(100, task.process_queue(context))
    return f


#################################
#      Validator Functions      #
#################################
def validate_type(string, other):
    """
    Checks whether STRING can be converted into type OTHER.
    :param string:      The string to check.
    :param other:       The type to check against.
    :return:            True if STRING can be of type OTHER, False otherwise.
    """

    try:
        other(string)
        return True
    except ValueError:
        return False


def validate_arrows(key):
    """
    Checks whether string KEY is an arrow key.
    :param key:     The key to check.
    :return:        KEY in lowercase if it is a valid arrow key.
    """

    if isinstance(key, str):
        key = key.lower()
        if key in ['up', 'down', 'left', 'right']:
            return key
    raise ValueError


def validate_horizontal_arrows(key):
    """
    Checks whether string KEY is either a left or right arrow key.
    :param key:     The key to check.
    :return:        KEY in lowercase if it is a valid horizontal arrow key.
    """

    if isinstance(key, str):
        key = key.lower()
        if key in ['left', 'right']:
            return key
    raise ValueError


def validate_nonzero_int(value):
    """
    Checks whether VALUE can be a valid nonzero integer.
    :param value:   The string to check.
    :return:        STRING as an integer.
    """

    if int(value) >= 1:
        return int(value)
    raise ValueError


def validate_boolean(boolean):
    """
    Checks whether string BOOLEAN is a valid bool.
    :param boolean:     The string to check.
    :return:            BOOLEAN as a bool if it is valid, otherwise None.
    """

    if isinstance(boolean, str):
        boolean = boolean.lower()
        if boolean == 'true':
            return True
        elif boolean == 'false':
            return False
    raise ValueError
