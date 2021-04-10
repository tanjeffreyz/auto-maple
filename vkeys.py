"""A module for simulating low-level keyboard key presses."""

import ctypes
import time
import utils
from ctypes import wintypes
from random import random


user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

MAPVK_VK_TO_VSC = 0

# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes?redirectedfrom=MSDN
key_map = {'tab': 0x09,  # Special Keys
           'alt': 0x12,
           'space': 0x20,
           'lshift': 0xA0,
           'ctrl': 0x11,
           'end': 0x23,
           'pgup': 0x21,
           'pgdown': 0x22,

           'left': 0x25,   # Arrow keys
           'up': 0x26,
           'right': 0x27,
           'down': 0x28,

           '0': 0x30,      # Numbers
           '1': 0x31,
           '2': 0x32,
           '3': 0x33,
           '4': 0x34,
           '5': 0x35,
           '6': 0x36,
           '7': 0x37,
           '8': 0x38,
           '9': 0x39,

           'f1': 0x70,     # Function keys
           'f2': 0x71,
           'f3': 0x72,
           'f4': 0x73,
           'f5': 0x74,
           'f6': 0x75,
           'f7': 0x76,
           'f8': 0x77,
           'f9': 0x78,
           'f10': 0x79,
           'f11': 0x7A,
           'f12': 0x7B,

           'a': 0x41,      # Letters
           'b': 0x42,
           'c': 0x43,
           'd': 0x44,
           'e': 0x45,
           'f': 0x46,
           'g': 0x47,
           'h': 0x48,
           'i': 0x49,
           'j': 0x4A,
           'k': 0x4B,
           'l': 0x4C,
           'm': 0x4D,
           'n': 0x4E,
           'o': 0x4F,
           'p': 0x50,
           'q': 0x51,
           'r': 0x52,
           's': 0x53,
           't': 0x54,
           'u': 0x55,
           'v': 0x56,
           'w': 0x57,
           'x': 0x58,
           'y': 0x59,
           'z': 0x5A}


#################################
#     C Struct Definitions      #
#################################
wintypes.ULONG_PTR = wintypes.WPARAM


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk, MAPVK_VK_TO_VSC, 0)


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg", wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))

    _anonymous_ = ("_input",)
    _fields_ = (("type", wintypes.DWORD),
                ("_input", _INPUT))


LPINPUT = ctypes.POINTER(INPUT)


def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args


user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, LPINPUT, ctypes.c_int)


#################################
#           Functions           #
#################################
@utils.run_if_enabled
def key_down(key):
    time.sleep(0.05)
    key = key.lower()
    if key not in key_map.keys():
        print(f"Invalid keyboard input: '{key}'.")
    else:
        x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=key_map[key]))
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
        time.sleep(0.05)


@utils.run_if_enabled
def key_up(key):
    time.sleep(0.05)
    key = key.lower()
    if key not in key_map.keys():
        print(f"Invalid keyboard input: '{key}'.")
    else:
        x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=key_map[key], dwFlags=KEYEVENTF_KEYUP))
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
        time.sleep(0.05)


@utils.run_if_enabled
def press(key, n, down_time=0.05, up_time=0.1):
    for _ in range(n):
        key_down(key)
        time.sleep(down_time * (0.8 + 0.4 * random()))
        key_up(key)
        time.sleep(up_time * (0.8 + 0.4 * random()))
