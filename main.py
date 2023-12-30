"""The central program that ties all the modules together."""

import time
from src.modules.bot import Bot
from src.modules.capture import Capture
from src.modules.detection_worker import DetectionWorker
from src.modules.notifier import Notifier
from src.modules.listener import Listener
from src.modules.gui import GUI
from src.modules.auto_pot import AutoPot

NUM_DETECTION_WORKERS = 5

bot = Bot()
capture = Capture()
detection_workers = []
notifier = Notifier()
listener = Listener()
auto_pot = AutoPot()

bot.start()
while not bot.ready:
    time.sleep(0.01)

capture.start()
while not capture.ready:
    time.sleep(0.01)

for i in range(NUM_DETECTION_WORKERS):
    detection_workers.append(DetectionWorker(i))
    detection_workers[i].start()
while NUM_DETECTION_WORKERS > 0 and not detection_workers[NUM_DETECTION_WORKERS - 1].ready:
    time.sleep(0.01)

notifier.start()
while not notifier.ready:
    time.sleep(0.01)

listener.start()
while not listener.ready:
    time.sleep(0.01)

auto_pot.start()
while not auto_pot.ready:
    time.sleep(0.01)

print('\n[~] Successfully initialized Auto Maple')

gui = GUI()
gui.start()
