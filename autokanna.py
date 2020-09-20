import mss, cv2, time, threading, vkeys, time, math, csv
import numpy as np
import keyboard as kb
import tkinter as tk
from vkeys import key_down, key_up
from os import listdir
from os.path import isfile, join


#################################
#       Global Variables        #
#################################
POSITION_TOLERANCE = 0.1

player_pos = (0, 0)
mm_ratio = 1.0
enabled = False
print_pos = True

new_point = None
sequence = []


#################################
#            Classes            #
#################################
class Capture:
    MINIMAP_TOP_BORDER = 20
    MINIMAP_BOTTOM_BORDER = 8

    minimap_template = cv2.imread('assets/minimap_template.jpg', 0)
    player_template = cv2.imread('assets/dot_template.png', 0)

    
    def __init__(self):
        self.cap = threading.Thread(target=self._capture)
        self.cap.daemon = True

    def _capture(self):
        with mss.mss() as sct:
            print('started capture')

            global player_pos, mm_ratio
            monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
            while True:
                frame = np.array(sct.grab(monitor))

                # Get the bottom right point of the minimap
                _, br = Capture._match_template(frame, Capture.minimap_template)
                mm_tl, mm_br = (Capture.MINIMAP_BOTTOM_BORDER, Capture.MINIMAP_TOP_BORDER), (tuple(a - Capture.MINIMAP_BOTTOM_BORDER for a in br))      # These are relative to entire screenshot

                # Make sure the minimap is larger than player_template
                if mm_br[0] - mm_tl[0] < Capture.player_template.shape[1] or mm_br[1] - mm_tl[1] < Capture.player_template.shape[0]:
                    mm_br = (mm_tl[0] + Capture.player_template.shape[1], mm_tl[1] + Capture.player_template.shape[0])
                
                # Crop the frame to only show the minimap
                minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                mm_ratio = minimap.shape[1] / minimap.shape[0]
                p_tl, p_br = Capture._match_template(minimap, Capture.player_template)           
                raw_player_pos = tuple((p_br[i] + p_tl[i]) / 2 for i in range(2))
                player_pos = (raw_player_pos[0] / minimap.shape[1], raw_player_pos[1] / minimap.shape[0])       # player_pos is relative to the minimap's inner box
                if print_pos:
                    print(player_pos)

                for element in sequence:
                    cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) * element.location[0]), round((mm_br[1] - mm_tl[1]) * element.location[1])), 3, (0, 255, 0), -1)

                cv2.imshow('mm', minimap)

                if cv2.waitKey(1) & 0xFF == 27:     # 27 is ASCII for the Esc key on a keyboard
                    break

    def _rescale_frame(frame, percent=100):
        width = int(frame.shape[1] * percent / 100)
        height = int(frame.shape[0] * percent / 100)
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

    def _match_template(frame, template):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        top_left = max_loc
        w, h = template.shape[::-1]
        bottom_right = (top_left[0] + w, top_left[1] + h)

        return top_left, bottom_right


class Commands:
    tengu_on = True


    def __init__(self):
        self.tengu = threading.Thread(target=self._tengu)         # Tengu thread continuously uses Tengu Strike unless tengu_on is set to False
        self.tengu.daemon = True     # Daemon threads end when the main thread ends
       
    def _tengu(self):
        print('started tengu')
        while True:
            if Commands.tengu_on and enabled:
                key_down('q')
                time.sleep(0.2)
                key_up('q')
                time.sleep(1.75)

    def teleport(self, direction, jump=True):
        assert direction in ['left', 'up', 'right', 'down'], f"'{direction}' is not a recognized direction."

        if direction != 'up':
            key_down(direction)
            time.sleep(0.05)
        if jump:
            press('space', 2, up_time=0.05)
            if direction in ['up', 'down']:
                time.sleep(0.06)
        if direction == 'up':
            key_down(direction)
            time.sleep(0.05)
        press('e', 3)
        key_up(direction)
        time.sleep(0.15)

    def shikigami(self, direction, n=1):
        assert direction in ['left', 'right'], 'Shikigami Haunting can only be used in the left and right directions.'

        key_down(direction)
        time.sleep(0.05)
        for _ in range(n):
            if Commands.tengu_on:
                press('q', 1, up_time=0.05)
            press('r', 4, down_time=0.1)
        key_up(direction)
        time.sleep(0.1)

    def kishin(self):
        time.sleep(0.2)
        press('lshift', 4, down_time=0.1)
    
    def boss(self, direction=None):     # Only Yaksha Boss takes an optional directional argument
        def act():
            time.sleep(0.15)
            if direction:
                press(direction, 1, down_time=0.1)
            else:
                if player_pos[0] > 0.5:     # Cast Yaksha Boss facing the center of the map
                    press('left', 1, down_time=0.1)
                else:
                    press('right', 1, down_time=0.1)
            press('2', 2, down_time=0.1, up_time=0.2)
        return act

    def fox(self):
        time.sleep(0.1)
        press('3', 3, down_time=0.1)
    
    def exo(self):
        time.sleep(0.1)
        press('space', 1, up_time=0.15)
        press('w', 2)


class Point:
    def __init__(self, x, y, frequency=1, attack=True, n=1, extras=[]):
        self.location = (x, y)
        self.frequency = frequency
        self.counter = 0
        self.attack = attack
        self.n = n
        self.extras = extras

    def execute(self):
        if self.counter == 0:
            move(self.location)
            for e in self.extras:
                exec(f'commands.{e}()')
            if self.attack:
                commands.shikigami('left', self.n)
                commands.shikigami('right', self.n)
        self.counter = (self.counter + 1) % self.frequency
        

#################################
#        Initialization         #
#################################
# sequence = [Point((0.37, 0.82)),
#             Point((0.33, 0.58)),
#             Point((0.3, 0.24)),
#             Point((0.5, 0.35), attack=False, extras=['kishin']),
#             Point((0.71, 0.25)),
#             Point((0.70, 0.58), attack=False, extras=['boss']),
#             Point((0.65, 0.82))]

# sequence = [Point((0.49, 0.44), attack=False, extras=['kishin']),
#             Point((0.44, 0.77)),
#             Point((0.82, 0.77), attack=False, extras=['boss']),
#             Point((0.77, 0.28)),
#             Point((0.65, 0.77)),
#             Point((0.44, 0.77))]

# sequence = [Point((0.515, 0.64)),
#             Point((0.85, 0.75), attack=False, extras=['boss()']),
#             Point((0.7, 0.25), attack=False, extras=['kishin']),
#             Point((0.85, 0.25), attack=False),
#             Point((0.515, 0.64)),
#             Point((0.2, 0.75)),
#             Point((0.3, 0.25)),
#             Point((0.2, 0.25), attack=False)]

# sequence = [Point((0.515, 0.66)),
#             Point((0.85, 0.75), frequency=2, attack=False, extras=['boss()']),
#             Point((0.7, 0.25), attack=False, extras=['kishin']),
#             Point((0.515, 0.66)),
#             Point((0.2, 0.75)),
#             Point((0.3, 0.25))]

# sequence = [Point((0.86, 0.16), attack=False, extras=['kishin']),
#             Point((0.76, 0.53)),
#             # Point((0.5, 0.53)),
#             Point((0.33, 0.53), frequency=2, extras=["boss('left')"]),
#             Point((0.64, 0.36)),
#             Point((0.63, 0.53))]

sequence = [Point(0.85, 0.16, frequency=2, attack=False, extras=['kishin']),
            Point(0.69, 0.53),
            Point(0.51, 0.53),
            Point(0.31, 0.53, frequency=2, attack=False, extras=["boss('left')"]),
            Point(0.16, 0.14, frequency=2),
            Point(0.61, 0.36, frequency=2, extras=['fox'])]


#################################
#             Mains             #
#################################
def bot():
    print('started bot')
    
    index = 0
    b = buff(0)
    while True: 
        if enabled and len(sequence) > 0:
            b = b(time.time())
            point = sequence[index]
            point.execute()
            index = (index + 1) % len(sequence)


#################################
#           Functions           #
#################################
def press(key, n, down_time=0.05, up_time=0.1):
    for _ in range(n):
        key_down(key)
        time.sleep(down_time)
        key_up(key)
        time.sleep(up_time)

def load():
    global sequence, new_point
    sequence = []

    path = './bots'
    csv_files = [f for f in listdir(path) if isfile(join(path, f)) and '.csv' in f]
    if not csv_files:
        print('Unable to find .csv bot file.')
    else:
        with open(join(path, csv_files[0])) as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                assert len(row) > 1, 'A Point must at least have an x and y position'
                args = ''.join([row[i] + (', ' if i != len(row) - 1 else '') for i in range(len(row))])
                exec(f'global new_point; new_point = Point({args})')
                sequence.append(new_point)

def distance(a, b):
    return math.sqrt(sum([(a[i] - b[i]) ** 2 for i in range(2)]))

def move(target):
    prev_pos = player_pos
    while enabled and distance(player_pos, target) > POSITION_TOLERANCE:
        if abs(player_pos[0] - target[0]) > POSITION_TOLERANCE / math.sqrt(2):
            jump = True if player_pos[1] > target[1] + 0.03 else False   
            if player_pos[0] < target[0]:
                commands.teleport('right', jump=jump)
            else:
                commands.teleport('left', jump=jump)
        # else:
        #     time.sleep(0.2)
        # else:
        #     time.sleep(0.5)

        if abs(player_pos[1] - target[1]) > POSITION_TOLERANCE / math.sqrt(2):
            if player_pos[1] < target[1]:
                commands.teleport('down')
            else:
                commands.teleport('up')
        # else:
        #     time.sleep(0.2)

        # counter = counter + 1 if player_pos == prev_pos else 0
        if player_pos == prev_pos:
            press('w', 2)
            press('e', 3)

        prev_pos = player_pos

def buff(time):
    def act(new_time):
        if time == 0 or new_time - time > 180:
            press('ctrl', 2, up_time=0.2)
            press('end', 4, up_time=0.3)
            press('9', 4, up_time=0.3)
            press('0', 4, up_time=0.3)
        else:
            new_time = time
        return buff(new_time)
    return act

def toggle_enabled():
    global enabled, print_pos
    prev = enabled
    if not enabled:     # If bot is going to be enabled, reload the bot file
        load()
        enabled, print_pos = True, False
    else:
        enabled, print_pos = False, True
    # enabled = not enabled
    print(f"toggled: {'on' if prev else 'off'} --> {'ON' if enabled else 'OFF'}")
    time.sleep(1)



if __name__ == '__main__':
    # load()

    capture = Capture()
    capture.cap.start()

    commands = Commands()

    bt = threading.Thread(target=bot)
    bt.daemon = True
    bt.start()

    kb.add_hotkey('insert', toggle_enabled)
    # kb.add_hotkey('alt', prompt)
    print('ready')
    while True:
        time.sleep(1)