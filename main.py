"""The center of Auto Kanna that ties all the modules together."""

import config
import time
from capture import Capture
from listener import Listener
from bot import Bot


cap = Capture()
cap.start()

# Wait for the video capture to initialize
while not config.ready:
    time.sleep(0.01)

listener = Listener()
listener.start()

bot = Bot()
bot.start()

# Periodically save changes to the active Layout if it exists
while True:
    if config.layout:
        config.layout.save()
    time.sleep(5)
