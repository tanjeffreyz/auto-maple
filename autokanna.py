import detection
import mss, cv2, time, threading, math, csv, winsound, win32api, win32con
import numpy as np
import keyboard as kb
from vkeys import key_down, key_up, press
from os import listdir
from os.path import isfile, join
from playsound import playsound


#################################
#           CONSTANTS           #
#################################
MONITOR = {'top': 0, 'left': 0, 'width': 1366, 'height': 768}

DEFAULT_MOVE_TOLERANCE = 0.1
DEFAULT_ADJUST_TOLERANCE = 0.01


#################################
#       Global Variables        #
#################################
enabled = False
ready = False
calibrated = False

rune_active = False
rune_pos = (0, 0)
rune_index = 0

eboss_active = False

player_pos = (0, 0)

new_point = None
sequence = []
seq_index = 0
file_index = 0


#################################
#         Bot Settings          #
#################################
move_tolerance = DEFAULT_MOVE_TOLERANCE
adjust_tolerance = DEFAULT_ADJUST_TOLERANCE
use_haku = True


#################################
#            Classes            #
#################################
class Capture:
    MINIMAP_TOP_BORDER = 20
    MINIMAP_BOTTOM_BORDER = 8

    minimap_template = cv2.imread('assets/minimap_template.jpg', 0)
    player_template = cv2.imread('assets/player_template.png', 0)
    rune_template = cv2.imread('assets/rune_template.png', 0)
    rune_buff_template = cv2.imread('assets/rune_buff_template.jpg', 0)
    eboss_template = cv2.imread('assets/eboss_template.jpg', 0)
    
    def __init__(self):
        self.cap = threading.Thread(target=self.capture)
        self.cap.daemon = True

    def capture(self):
        with mss.mss() as sct:
            print('Started capture')

            global player_pos, calibrated, rune_active, rune_pos, rune_index, eboss_active
            while True:
                if not calibrated:
                    frame = np.array(sct.grab(MONITOR))

                    # Get the bottom right point of the minimap
                    _, br = Capture.single_match(frame[:round(frame.shape[0] / 4),:round(frame.shape[1] / 4)], Capture.minimap_template)
                    mm_tl, mm_br = (Capture.MINIMAP_BOTTOM_BORDER, Capture.MINIMAP_TOP_BORDER), (tuple(max(75, a - Capture.MINIMAP_BOTTOM_BORDER) for a in br))      # These are relative to the entire screenshot
                    calibrated = True
                else:
                    frame = np.array(sct.grab(MONITOR))
                    height, width, _ = frame.shape

                    # Check for eboss warning
                    eboss_frame = frame[height//4:3*height//4, width//4:3*width//4]
                    if not eboss_active and Capture.multi_match(eboss_frame, Capture.eboss_template, threshold=0.9):
                        eboss_active = True

                    # Crop the frame to only show the minimap
                    minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                    player = Capture.multi_match(minimap, Capture.player_template, threshold=0.9)
                    if player:
                        player_pos = Capture.convert_to_relative(player[0], minimap)
                    
                    # Check for a rune
                    if not rune_active:
                        rune = Capture.multi_match(minimap, Capture.rune_template, threshold=0.9)
                        if rune and sequence:
                            rune_pos = Capture.convert_to_relative((rune[0][0] - 1, rune[0][1]), minimap)
                            distances = list(map(lambda p: distance(rune_pos, p.location) if isinstance(p, Point) else float('inf'), sequence))
                            rune_index = np.argmin(distances)
                            rune_active = True

                    # Mark the minimap with useful information
                    if rune_active:
                        cv2.circle(minimap, Capture.convert_to_absolute(rune_pos, minimap), 3, (255, 0, 255), -1)
                    if not enabled:
                        color = (0, 0, 255)
                    else:
                        color = (0, 255, 0)
                    for element in sequence:
                        if isinstance(element, Point):
                            cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) * element.location[0]), round((mm_br[1] - mm_tl[1]) * element.location[1])), round(minimap.shape[1] * move_tolerance), color, 1)
                    if ready:
                        cv2.circle(minimap, Capture.convert_to_absolute(player_pos, minimap), 3, (255, 0, 0), -1)
                    cv2.imshow('mm', minimap)
                if cv2.waitKey(1) & 0xFF == 27:     # 27 is ASCII for the Esc key
                    break

    def convert_to_relative(point, frame):
        return (point[0] / frame.shape[1], point[1] / frame.shape[0])
        
    def convert_to_absolute(point, frame):
        return tuple(int(round(point[i] * frame.shape[1 - i])) for i in range(2))

    def rescale_frame(frame, percent=100):
        width = int(frame.shape[1] * percent / 100)
        height = int(frame.shape[0] * percent / 100)
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

    def single_match(frame, template):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        w, h = template.shape[::-1]
        bottom_right = (max_loc[0] + w, max_loc[1] + h)
        return max_loc, bottom_right

    def multi_match(frame, template, threshold=0.63):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        return [tuple(int(round(p[i] + template.shape[1 - i] / 2))
                      for i in range(2))
                for p in locations]


class Commands:
    def goto(self, label):
        def act():
            global seq_index
            try:
                seq_index = sequence.index(label)
            except:
                print(f"Label '{label}' does not exist")
        return act

    def teleport(self, direction, jump=False):
        def act():
            num_presses = 3
            prev_y = round(player_pos[1], 2)
            if direction != 'up':
                key_down(direction)
                time.sleep(0.05)
            if jump:
                if direction == 'down':
                    press('space', 3, down_time=0.1)
                    num_presses = 2
                else:
                    press('space', 2, up_time=0.1)
            if direction == 'up':           # Catch special case for up-teleport
                if round(player_pos[1], 2) >= prev_y:
                    time.sleep(0.05)
                    press('space', 1, up_time=0.15)
                    self.exo()
                key_down(direction)
                time.sleep(0.05)
            press('e', num_presses)
            key_up(direction)
            if num_presses < 3:
                time.sleep(0.1)
        return act

    def shikigami(self, direction, n=1, num_attacks=3):
        def act():
            time.sleep(0.05)
            key_down(direction)
            time.sleep(0.05)
            for _ in range(n):
                press('r', num_attacks, up_time=0.05)
            key_up(direction)
            time.sleep(0.1)
        return act

    def tengu(self):
        press('q', 1)
        time.sleep(0.05)

    def kishin(self):
        time.sleep(0.05)
        press('lshift', 6, down_time=0.1)
    
    def boss(self, direction=None):
        def act():
            if direction:
                press(direction, 1, down_time=0.1)
            else:
                if player_pos[0] > 0.5:     # Cast Yaksha Boss facing the center of the map
                    press('left', 1, down_time=0.1)
                else:
                    press('right', 1, down_time=0.1)
            press('2', 3)
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
    
    def fall(self):
        starting_pos = player_pos
        n, exit_threshold = 0, 6
        key_down('down')
        time.sleep(0.05)
        while distance(starting_pos, player_pos) < 0.1 and n < exit_threshold:
            press('space', 1, down_time=0.1, up_time=0.1)
            n += 1
        key_up('down')
        time.sleep(0.1)
    
    def wait(self, delay):
        def act():
            time.sleep(delay)
        return act

    def walk(self, direction, duration):
        def act():
            press(direction, 1, down_time=duration, up_time=0.05)
        return act


class Point:
    def __init__(self, x, y, counter=0, frequency=1, attacks=1, extras=[]):
        self.location = (x, y)
        self.counter = counter
        self.frequency = frequency
        self.attacks = attacks
        self.extras = extras

    def execute(self):
        executed = False
        if self.counter == 0:
            move(self.location)
            if enabled:
                for e in self.extras:
                    exec(f'commands.{e}()')
                if self.attacks:
                    commands.shikigami('left', self.attacks)()
                    commands.shikigami('right', self.attacks)()
            executed = True
        if enabled:
            self.counter = (self.counter + 1) % self.frequency
        return executed

    def __str__(self):
        result = 'Point:'
        result += f'\n  location: {self.location}'
        result += f'\n  counter: {self.counter}'
        result += f'\n  extras: {self.extras}'
        return result


#################################
#             Mains             #
#################################
def bot():
    global seq_index, enabled, eboss_active
    print('Started bot')

    haku = buff(480, buffs=['ctrl'])
    decents = buff(200, buffs=['f1','f2','f4'])

    with mss.mss() as sct:
        while True:
            # Check for Elite Boss
            if eboss_active:
                enabled = False
                while not kb.is_pressed('insert'):
                    playsound('./assets/alert.mp3')
                    time.sleep(0.1)
                eboss_active = False
                time.sleep(1)

            # Check for user input
            if kb.is_pressed('insert'):
                toggle_enabled()
            elif kb.is_pressed('F6'):
                recalibrate_mm()
                load(index=file_index)
            elif kb.is_pressed('F7'):
                recalibrate_mm()
                load()
            elif kb.is_pressed('F8'):
                displayed_pos = tuple('{:.3f}'.format(round(i, 3)) for i in player_pos)
                print('\n\n\nCurrent position: ({}, {})'.format(displayed_pos[0], displayed_pos[1]))
                time.sleep(1)
            
            # Run bot sequence
            if enabled and len(sequence) > 0:
                curr_index = seq_index
                curr_time = time.time()

                # Use buffs
                if use_haku:
                    haku = haku(curr_time)
                decents = decents(curr_time)
                
                element = sequence[curr_index]
                if isinstance(element, Point):
                    print('')
                    print(element)
                    executed = element.execute()
                    if enabled:
                        if rune_active and curr_index == rune_index and executed:
                            success = move(rune_pos, max_steps=5)
                            if success:
                                adjust(rune_pos, tolerance=0.006)
                                time.sleep(0.1)
                                press('y', 1, down_time=0.3, up_time=0.7)
                                inferences = []
                                for _ in range(15):
                                    frame = np.array(sct.grab(MONITOR))
                                    arrows = detection.merge_detection(frame)
                                    print('\n', f'current: {arrows}')
                                    print(f'previous: {inferences}')
                                    if arrows in inferences:
                                        # Solve the rune
                                        for arrow in arrows:
                                            press(arrow, 1, up_time=0.15)

                                        # Right-click to disable the rune's special effect
                                        time.sleep(1)
                                        for _ in range(3):
                                            time.sleep(0.3)
                                            frame = np.array(sct.grab(MONITOR))
                                            rune_buff = Capture.multi_match(frame[:frame.shape[0]//8, :], Capture.rune_buff_template, threshold=0.9)
                                            if rune_buff:
                                                rune_buff_pos = min(rune_buff, key=lambda p: p[0])
                                                click(rune_buff_pos, button='right')
                                        break
                                    elif len(arrows) == 4:
                                        inferences.append(arrows)
                            reset_rune()
                        seq_index = (seq_index + 1) % len(sequence)
                else:
                    seq_index = (seq_index + 1) % len(sequence)
            else:
                time.sleep(0.1)


#################################
#           Functions           #
#################################
def load(index=float('inf')):
    global file_index, sequence, new_point, use_haku
    reset_index()
    reset_rune()
    
    sequence = []
    path = './routines'
    csv_files = [f for f in listdir(path) if isfile(join(path, f)) and '.csv' in f]
    if not csv_files:
        print('Unable to find a .csv routine')
    else:
        print('\n\n\n~~~ Loading File ~~~')
        print('Select from the following routines:')
        for i in range(len(csv_files)):
            print(f'{i}  {csv_files[i]}')
        print('')
        while index not in range(len(csv_files)):
            selection = input('>>> ')
            if selection in ['^C', '^Z']:
                break
            try:
                index = int(selection)
            except:
                print('Selection must be an integer')
        file_index = index

        # Load the file specified by the user.
        with open(join(path, csv_files[index])) as f:
            first_row = True
            csv_reader = csv.reader(f, delimiter=';')
            for row in csv_reader:
                if first_row:
                    first_row = False
                    try:
                        for setting in row:
                            exec('global use_haku; ' + setting)
                        continue
                    except:
                        print(f"Skipped loading first row due to invalid bot settings: '{row}'")

                if len(row) == 1:
                    # If there is only one element in the row, it must be a label
                    sequence.append(row[0])
                else:
                    args = ''.join([row[i] + (', ' if i != len(row) - 1 else '') for i in range(len(row))])
                    try:
                        exec(f'global new_point; new_point = Point({args})')
                    except:
                        print(f"Error while creating point 'Point({args})'")
                        continue
                    sequence.append(new_point)
        print(f'Finished loading file at index {index}')
        winsound.Beep(523, 200)
        winsound.Beep(659, 200)
        winsound.Beep(784, 200)
        time.sleep(0.15)
        

def distance(a, b):
    return math.sqrt(sum([(a[i] - b[i]) ** 2 for i in range(2)]))


def move(target, tolerance=move_tolerance, max_steps=15):
    toggle = False
    prev_pos = [tuple(round(a, 2) for a in player_pos)]
    while enabled and max_steps > 0 and distance(player_pos, target) > tolerance:
        toggle = not toggle

        if kb.is_pressed('insert'):
            toggle_enabled()
            break

        if toggle:
            d_x = abs(player_pos[0] - target[0])
            if d_x > tolerance / math.sqrt(2):
                jump = player_pos[1] > target[1] + 0.03 and abs(player_pos[1] - target[1]) < 0.2
                if player_pos[0] < target[0]:
                    commands.teleport('right', jump=jump)()
                else:
                    commands.teleport('left', jump=jump)()
                max_steps -= 1
            else:
                continue
        else:
            d_y = abs(player_pos[1] - target[1])
            if d_y > tolerance / math.sqrt(2):
                if player_pos[1] < target[1]:
                    jump = d_y > 0.333
                    commands.teleport('down', jump=jump)()
                else:
                    commands.teleport('up', jump=True)()
                max_steps -= 1
            else:
                continue
        
        rounded_pos = tuple(round(a, 2) for a in player_pos)
        num_previous = prev_pos.count(rounded_pos)
        if num_previous > 0 and num_previous % 2 == 0:
            print('stuck')
            for _ in range(10):
                press('left', 1, up_time=0.05)
                press('right', 1, up_time=0.05)
        prev_pos.append(rounded_pos)
        if len(prev_pos) > 3:
            prev_pos.pop(0)
    return max_steps


def adjust(target, tolerance=adjust_tolerance):
    while enabled and abs(player_pos[0] - target[0]) > tolerance:
        if player_pos[0] > target[0]:
            press('left', 1, down_time=0.06, up_time=0.001)
        else:
            press('right', 1, down_time=0.06, up_time=0.001)


def buff(period, buffs=['0'], t=0, mode=0):
    if len(buffs) == 0:
        return print("Function 'main_buff' requires at least one buff")
    def act(new_t):
        nonlocal buffs
        if mode == 0:
            if t == 0 or new_t - t > period:
                for b in buffs:
                    press(b, 3, up_time=0.3)
            else:
                new_t = t
        elif mode == 1:
            if t == 0 or new_t - t > period / len(buffs):
                press(buffs[0], 3, up_time=0.05)
                time.sleep(0.05)
                commands.tengu()
                buffs = buffs[1:] + buffs[:1]
            else:
                new_t = t
        return buff(period, buffs=buffs, t=new_t, mode=mode)
    return act


def click(pos, button='left'):
    if button in ['left', 'right']:
        if button == 'left':
            down_event = win32con.MOUSEEVENTF_LEFTDOWN
            up_event = win32con.MOUSEEVENTF_LEFTUP
        else:
            down_event = win32con.MOUSEEVENTF_RIGHTDOWN
            up_event = win32con.MOUSEEVENTF_RIGHTUP
        win32api.SetCursorPos(pos)
        win32api.mouse_event(down_event, pos[0], pos[1], 0, 0)
        win32api.mouse_event(up_event, pos[0], pos[1], 0, 0)


def toggle_enabled():
    global enabled
    reset_rune()
    reset_eboss()
    prev = enabled
    if not enabled:
        winsound.Beep(784, 333)     # G5
    else:
        winsound.Beep(523, 333)     # C5
    enabled = not enabled
    print(f"\n\n\ntoggled: {'on' if prev else 'off'} --> {'ON' if enabled else 'OFF'}")
    time.sleep(0.667)


def reset_index():
    global seq_index
    seq_index = 0


def reset_rune():
    global rune_active
    rune_active = False


def reset_eboss():
    global eboss_active
    eboss_active = False


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

    time.sleep(1)   # TODO: use while loop and global state variable to check whether capture has started
    ready = True
    load()

    sct = mss.mss()
    while True:
        time.sleep(1)