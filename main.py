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


# TODO: remove this thingy below
import utils
@utils.run_if_enabled
def test_print(thingy):
    print(thingy)


while True:
    test_print(config.player_pos)
    time.sleep(0.1)
