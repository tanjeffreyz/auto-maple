"""The central program that ties all the modules together."""

import time
from capture import Capture
from listener import Listener
from bot import Bot
from gui import GUI


gui = GUI()

cap = Capture()
cap.start()
while not cap.ready:
    time.sleep(0.01)

bot = Bot()
bot.start()
while not bot.ready:
    time.sleep(0.01)

listener = Listener()
listener.start()
while not listener.ready:
    time.sleep(0.01)

print('\n[~] Successfully initialized Auto Maple.')

gui.start()
