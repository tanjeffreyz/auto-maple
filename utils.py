"""A collection of functions used across multiple modules."""

import config
import math
import win32con
import win32api


def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def click(position, button='left'):
    """
    Simulate a mouse click with BUTTON at POSITION.
    :param pos:
    :param button:
    :return:
    """

    if button not in ['left', 'right']:
        print(f"'{button}' is not a valid mouse button.")
    else:
        if button == 'left':
            down_event = win32con.MOUSEEVENTF_LEFTDOWN
            up_event = win32con.MOUSEEVENTF_LEFTUP
        else:
            down_event = win32con.MOUSEEVENTF_RIGHTDOWN
            up_event = win32con.MOUSEEVENTF_RIGHTUP
        win32api.SetCursorPos(position)
        win32api.mouse_event(down_event, position[0], position[1], 0, 0)
        win32api.mouse_event(up_event, position[0], position[1], 0, 0)


def print_separator():
    print('\n\n')


def validate_type(string, other):
    """
    Checks whether STRING can be converted into type OTHER.
    :param string:      The string to check
    :param other:       The type to check against.
    :return:            Whether STRING can be of type OTHER.
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
    :return:        None
    """

    if isinstance(key, str):
        if key in ['up', 'down', 'left', 'right']:
            return
    raise ValueError


def validate_horizontal(key):
    """
    Checks whether string KEY is either a left or right arrow key.
    :param key:     The key to check.
    :return:        None
    """

    if isinstance(key, str):
        if key in ['left', 'right']:
            return
    raise ValueError


def validate_nonzero(value):
    """
    Checks whether string VALUE is a valid nonzero integer.
    :param value:   The string to check.
    :return:        None
    """

    if isinstance(value, str):
        if int(value) >= 1:
            return
    raise ValueError


def validate_position(position):
    """
    Checks whether string POSITION is a valid coordinate point.
    :param position:    The string to check.
    :return:            POSITION as a tuple if it is valid, otherwise None.
    """

    if isinstance(position, str):
        position.replace('(', '')
        position.replace(')', '')
        position = tuple(map(float, position.split(',')))
        if len(position) == 2:
            return position
    raise ValueError


def validate_boolean(boolean):
    """
    Checks whether string BOOLEAN is a valid bool.
    :param boolean:     The string to check.
    :return:            BOOLEAN as a bool if it is valid, otherwise None.
    """

    if isinstance(boolean, str):
        if boolean == 'True':
            return True
        elif boolean == 'False':
            return False
    raise ValueError


def run_if_enabled(function):
    """
    Decorator for functions that should only run if the bot is enabled.
    :param function:    The function to decorate.
    :return:            The decorated function.
    """

    def helper(*args):
        if config.enabled:
            function(*args)
    return helper
