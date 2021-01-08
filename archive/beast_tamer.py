import time
import keyboard as kb
from vkeys import press

toggle = False
# three_point = 0
while True:
    if kb.is_pressed('insert'):
        toggle = not toggle
        time.sleep(1)
                # three_point += 1
        # if three_point % 10 == 0:
        #     press('f', 3, down_time=0.1)
        # else:
    if toggle:
        press('r', 2)
        press('e', 2)
    else:
        time.sleep(0.1)