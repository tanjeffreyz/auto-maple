"""The center of Auto Kanna that ties all the modules together."""

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
    config.layout.add(*config.player_pos)
    time.sleep(1)
