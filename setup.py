"""Creates a desktop shortcut that can run Auto Maple from anywhere."""

import os
import sys
import ctypes
import argparse
import win32com.client as client


MAX_DEPTH = 1       # Run at most MAX_DEPTH additional times


def run_as_admin():
    if args.depth < MAX_DEPTH:
        print('\n[!] Insufficient privileges, re-running as administrator')
        ctypes.windll.shell32.ShellExecuteW(
            None,
            'runas',
            sys.executable,
            ' '.join(sys.argv + [f'--depth {args.depth + 1}']),
            None,
            1
        )
        print(' ~  Finished setting up Auto Maple')
    exit(0)


def create_desktop_shortcut():
    """Creates and saves a desktop shortcut using absolute paths"""
    print('\n[~] Creating desktop shortcut for Auto Maple:')
    cwd = os.getcwd()
    target = os.path.join(os.environ['WINDIR'], 'System32', 'cmd.exe')

    flag = "/c"
    if args.stay:
        flag = "/k"
        print(" -  Leaving command prompt open after program finishes")

    # https://www.tensorflow.org/install/pip#windows-native_1
    #   NEED python 3.10
    #   conda create --name tf python=3.9
    #   conda activate tf
    #   conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0
    #   conda install -c conda-forge cudatoolkit-dev
    #   pip install --upgrade pip
    #   pip install "tensorflow<2.11"
    #   pip install numpy==1.26.4
    #   conda env config vars set LD_LIBRARY_PATH="C:\ProgramData\miniconda3;C:\ProgramData\miniconda3\Library\mingw-w64\bin;C:\ProgramData\miniconda3\Library\usr\bin;C:\ProgramData\miniconda3\Library\bin;C:\ProgramData\miniconda3\Scripts"
    gpu_cmd = ""
    if args.gpu:
        home_dir = os.path.expanduser( '~' )
        gpu_cmd = f"{home_dir}\\miniconda3\\Scripts\\activate.bat {home_dir}\\miniconda3 & conda activate tf & "

    shell = client.Dispatch('WScript.Shell')
    shortcut_path = os.path.join(shell.SpecialFolders('Desktop'), 'Auto Maple.lnk')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target
    shortcut.Arguments = flag + f' \"{gpu_cmd}cd {cwd} & python main.py\"'
    shortcut.IconLocation = os.path.join(cwd, 'assets', 'icon.ico')
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
    parser.add_argument('--depth', type=int, default=0)
    parser.add_argument('--stay', action='store_true')
    parser.add_argument('--gpu', action='store_true', default=False)
    args = parser.parse_args()

    create_desktop_shortcut()
