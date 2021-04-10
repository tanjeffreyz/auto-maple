"""The control center of Auto Kanna."""

import config
import time
from capture import Capture
from bot import Bot
from listener import Listener


cap = Capture()
cap.start()

# Wait for the video capture to initialize
while not config.ready:
    pass

listener = Listener()
listener.start()

bot = Bot()
bot.start()

while True:
    time.sleep(1)
