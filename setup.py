"""Creates a desktop shortcut that can run Auto Maple from anywhere."""

import os
import sys
import ctypes
import argparse
import win32com.client as client


def run_as_admin():
    print('\n[!] Insufficient privileges, re-running as administrator')
    ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, ' '.join(sys.argv), None, 1)
    print(' ~  Finished setting up Auto Maple')
    exit(0)


def create_desktop_shortcut():
    """Creates and saves a desktop shortcut using absolute paths"""
    print('\n[~] Creating desktop shortcut for Auto Maple:')
    CWD = os.getcwd()
    TARGET = os.path.join(os.environ['WINDIR'], 'System32', 'cmd.exe')

    flag = "/c"
    if args.stay:
        flag = "/k"
        print(" -  Leaving command prompt open after program finishes")

    shell = client.Dispatch('WScript.Shell')
    shortcut_path = os.path.join(shell.SpecialFolders('Desktop'), 'Auto Maple.lnk')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = TARGET
    shortcut.Arguments = flag + f' \"cd {CWD} & python main.py\"'
    shortcut.IconLocation = os.path.join(CWD, 'assets', 'icon.ico')
    try:
        shortcut.save()
    except:
        run_as_admin()

    # Enable "run as administrator"
    with open(shortcut_path, 'rb') as lnk:
        arr = bytearray(lnk.read())

    arr[0x15] = arr[0x15] | 0x20        # Set the 6th bit of 21st byte to 1

    with open(shortcut_path, 'wb') as lnk:
        lnk.write(arr)
        print(' -  Enabled the "Run as Administrator" option')
    print(' ~  Successfully created Auto Maple shortcut')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stay', action='store_true')
    args = parser.parse_args()

    create_desktop_shortcut()
