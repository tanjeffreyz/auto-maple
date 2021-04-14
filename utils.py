"""A collection of functions used across multiple modules."""

import config
import math
from random import random


def distance(a, b):
    """
    Applies the distance formula to two points.
    :param a:   The first point.
    :param b:   The second point.
    :return:    The distance between the two points.
    """

    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


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


def run_if_enabled(function):
    """
    Decorator for functions that should only run if the bot is enabled.
    :param function:    The function to decorate.
    :return:            The decorated function.
    """

    def helper(*args, **kwargs):
        if config.enabled:
            function(*args, **kwargs)
    return helper


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
