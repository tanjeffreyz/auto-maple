"""Creates a desktop shortcut that can run Auto Maple from anywhere."""

import os
import win32com.client as client


# Create and save the shortcut using absolute paths
print('[~] Creating a desktop shortcut for Auto Maple...')
CWD = os.getcwd()
TARGET = os.path.join(os.environ['WINDIR'], 'System32', 'cmd.exe')
PATH = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'Auto Maple.lnk')

shell = client.Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(PATH)
shortcut.Targetpath = TARGET
shortcut.Arguments = f'/c \"cd {CWD} & python main.py\"'
shortcut.IconLocation = os.path.join(CWD, 'assets', 'icon.ico')
shortcut.save()

# Enable "run as administrator"
with open(PATH, 'rb') as lnk:
    arr = bytearray(lnk.read())

arr[0x15] = arr[0x15] | 0x20        # Set the 6th bit of 21st byte to 1

with open(PATH, 'wb') as lnk:
    lnk.write(arr)
    print(' ~  Enabled the "Run as Administrator" option.')

print('[~] Successfully created Auto Maple shortcut.')
