import mss, cv2, time, threading, vkeys, math, csv, winsound
import numpy as np
import keyboard as kb
from vkeys import key_down, key_up
from os import listdir
from os.path import isfile, join


#################################
#           CONSTANTS           #
#################################
DEFAULT_POSITION_TOLERANCE = 0.1
DEFAULT_BUFF_COOLDOWN = 200
DEFAULT_TENGU_ON = True


#################################
#       Global Variables        #
#################################
enabled = False
ready = False
calibrated = False

player_pos = (0, 0)
mm_ratio = 1.0

new_point = None
sequence = []
index = 0


#################################
#         Bot Settings          #
#################################
position_tolerance = DEFAULT_POSITION_TOLERANCE
buff_cooldown = DEFAULT_BUFF_COOLDOWN
tengu_on = DEFAULT_TENGU_ON


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

            global player_pos, mm_ratio, calibrated
            monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
            while True:
                if not calibrated:
                    frame = np.array(sct.grab(monitor))

                    # Get the bottom right point of the minimap
                    _, br = Capture._match_template(frame[:round(frame.shape[1] / 4),:round(frame.shape[0] / 4)], Capture.minimap_template)
                    mm_tl, mm_br = (Capture.MINIMAP_BOTTOM_BORDER, Capture.MINIMAP_TOP_BORDER), (tuple(a - Capture.MINIMAP_BOTTOM_BORDER for a in br))      # These are relative to the entire screenshot
                    calibrated = True
                else:
                    frame = np.array(sct.grab(monitor))

                    # Crop the frame to only show the minimap
                    minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    mm_ratio = minimap.shape[1] / minimap.shape[0]
                    p_tl, p_br = Capture._match_template(minimap, Capture.player_template)           
                    raw_player_pos = tuple((p_br[i] + p_tl[i]) / 2 for i in range(2))
                    player_pos = (raw_player_pos[0] / minimap.shape[1], raw_player_pos[1] / minimap.shape[0])       # player_pos is relative to the minimap's inner box
                    if not enabled:
                        print(player_pos)
                        color = (0, 0, 255)
                    else:
                        color = (0, 255, 0)
                    for element in sequence:
                        cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) * element.location[0]), round((mm_br[1] - mm_tl[1]) * element.location[1])), round(minimap.shape[1] * position_tolerance), color, 1)
                    if ready:
                        cv2.circle(minimap, tuple(round(a) for a in raw_player_pos), 3, (255, 0, 0), -1)
                    cv2.imshow('mm', minimap)
                if cv2.waitKey(1) & 0xFF == 27:     # 27 is ASCII for the Esc key
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
    def teleport(self, direction, jump=True):
        def act():
            if direction != 'up':
                key_down(direction)
                time.sleep(0.05)
            prev_y = round(player_pos[1], 2)
            if jump:
                press('space', 3, down_time=0.033, up_time=0.033)
                if direction in ['up', 'down']:
                    time.sleep(0.06)
            if direction == 'up':
                if round(player_pos[1], 2) >= prev_y:
                    time.sleep(0.05)
                    press('space', 1, up_time=0.15)
                    self.exo()
                key_down(direction)
                time.sleep(0.05)
            press('e', 3)
            key_up(direction)
            time.sleep(0.15)
        return act

    def shikigami(self, direction, n=1):
        def act():
            key_down(direction)
            time.sleep(0.05)
            for _ in range(n):
                if tengu_on:
                    press('q', 1, up_time=0.05)
                press('r', 5, up_time=0.075)
            key_up(direction)
            time.sleep(0.15)
        return act

    def tengu(self):
        press('q', 1)

    def kishin(self):
        time.sleep(0.05)
        press('lshift', 6, down_time=0.1)
    
    def boss(self, direction=None):     # Only Yaksha Boss takes an optional directional argument
        def act():
            if direction:
                press(direction, 1, down_time=0.1)
            else:
                if player_pos[0] > 0.5:     # Cast Yaksha Boss facing the center of the map
                    press('left', 1, down_time=0.1)
                else:
                    press('right', 1, down_time=0.1)
            press('2', 5, down_time=0.1, up_time=0.1)
        return act

    def fox(self):
        time.sleep(0.1)
        press('3', 3, down_time=0.1)
    
    def exo(self):
        press('w', 2, up_time=0.05)
    
    def charm(self, direction=None, delay=0.15):
        def act():
            time.sleep(0.05)
            if direction:
                key_down(direction)
                time.sleep(0.1)
            press('d', 2)
            if direction:
                key_up(direction)
            time.sleep(delay)
        return act
    
    def wait(self, delay):
        def act():
            time.sleep(delay)
        return act


class Point:
    def __init__(self, x, y, counter=0, frequency=1, attacks=1, extras=[]):
        self.location = (x, y)
        self.counter = counter
        self.frequency = frequency
        self.attacks = attacks
        self.extras = extras

    def execute(self):
        if self.counter == 0:
            move(self.location)
            if enabled:
                for e in self.extras:
                    exec(f'commands.{e}()')
                if self.attacks:
                    commands.shikigami('left', self.attacks)()
                    commands.shikigami('right', self.attacks)()
        if enabled:
            self.counter = (self.counter + 1) % self.frequency


#################################
#             Mains             #
#################################
def bot():
    global index
    print('started bot')
    
    b = buff(0)
    while True: 
        if enabled and len(sequence) > 0:
            b = b(time.time())
            if index >= len(sequence):      # Just in case I delete some Points from sequence while the bot is running
                index = len(sequence) - 1
            point = sequence[index]
            point.execute()
            if enabled:
                index = (index + 1) % len(sequence)
        if kb.is_pressed('insert'):
            toggle_enabled()
        elif kb.is_pressed('page up'):
            load()
            reset_index()
            time.sleep(1)
        elif kb.is_pressed('home'):
            recalibrate_mm()
            time.sleep(1)


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
    global position_tolerance, buff_cooldown, tengu_on
    position_tolerance = DEFAULT_POSITION_TOLERANCE
    buff_cooldown = DEFAULT_BUFF_COOLDOWN
    tengu_on = DEFAULT_TENGU_ON
    
    global sequence, new_point
    sequence = []
    path = './bots'
    csv_files = [f for f in listdir(path) if isfile(join(path, f)) and '.csv' in f]
    if not csv_files:
        print('Unable to find .csv bot file')
    else:
        with open(join(path, csv_files[0])) as f:
            csv_reader = csv.reader(f, delimiter=';')
            first_row = True
            for row in csv_reader:
                if first_row:
                    for a in row:
                        try:
                            exec(f'global position_tolerance, buff_cooldown, tengu_on; {a}')
                        except:
                            print(f"'{a}' is not a valid bot setting")
                            pass
                    first_row = False

                args = ''.join([row[i] + (', ' if i != len(row) - 1 else '') for i in range(len(row))])
                try:
                    exec(f'global new_point; new_point = Point({args})')
                except:
                    print(f"Error while creating point 'Point({args})'")
                    continue
                sequence.append(new_point)

def distance(a, b):
    return math.sqrt(sum([(a[i] - b[i]) ** 2 for i in range(2)]))

def move(target):
    prev_pos = [tuple(round(a, 2) for a in player_pos)]
    while enabled and distance(player_pos, target) > position_tolerance:
        d_x = abs(player_pos[0] - target[0])
        if d_x > position_tolerance / math.sqrt(2):
            jump = player_pos[1] > target[1] + 0.03 and abs(player_pos[1] - target[1]) < 0.2
            if player_pos[0] < target[0]:
                commands.teleport('right', jump=jump)()
            else:
                commands.teleport('left', jump=jump)()
        
        d_y = abs(player_pos[1] - target[1])
        if d_y > position_tolerance / math.sqrt(2):
            if player_pos[1] < target[1]:
                jump = d_y > 0.333
                commands.teleport('down', jump=jump)()
            else:
                commands.teleport('up')()
        
        rounded_pos = tuple(round(a, 2) for a in player_pos)
        print(f'new: {rounded_pos}, prev: {prev_pos}')
        if rounded_pos in prev_pos:
            print('stuck')
            time.sleep(0.1)
            press('e', 3)
        prev_pos.append(rounded_pos)
        if len(prev_pos) > 3:
            prev_pos.pop(0)
        
        if kb.is_pressed('insert'):
            toggle_enabled()
            break

def buff(time):
    def act(new_time):
        if time == 0 or new_time - time > buff_cooldown:
            press('ctrl', 2, up_time=0.2)
            press('end', 3, up_time=0.2)
            press('8', 3, up_time=0.3)
            press('9', 3, up_time=0.3)
            press('0', 3, up_time=0.3)
        else:
            new_time = time
        return buff(new_time)
    return act

def toggle_enabled():
    global enabled
    prev = enabled
    if not enabled:
        winsound.Beep(784, 333)     # G5
    else:
        winsound.Beep(523, 333)     # C5
    enabled = not enabled
    print(f"toggled: {'on' if prev else 'off'} --> {'ON' if enabled else 'OFF'}")
    time.sleep(1)

def reset_index():
    global index
    index = 0

def recalibrate_mm():
    global calibrated
    calibrated = False


if __name__ == '__main__':
    capture = Capture()
    capture.cap.start()

    commands = Commands()

    bt = threading.Thread(target=bot)
    bt.daemon = True
    bt.start()

    load()
    ready = True
    print('ready')
    while True:
        time.sleep(1)