import mss, cv2, time, threading, vkeys, time, math
import numpy as np
# import keyboard as kb
import tkinter as tk
from vkeys import key_down, key_up


#################################
#       Global Variables        #
#################################
POSITION_TOLERANCE = 0.12

player_pos = (0, 0)
enabled = False


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

            global player_pos
            monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
            while True:
                frame = np.array(sct.grab(monitor))
                # cv2.imshow('screenshot', Capture._rescale_frame(frame, percent=50))
                for x in [25 * i for i in range(77)]:
                    color = (0, 255, 0) if x % 100 else (255, 0, 0)
                    cv2.circle(frame, (x, 540), 3, color, -1)
                
                # Get the bottom right point of the minimap
                _, br = Capture._match_template(frame, Capture.minimap_template)
                mm_tl, mm_br = (Capture.MINIMAP_BOTTOM_BORDER, Capture.MINIMAP_TOP_BORDER), (tuple(a - Capture.MINIMAP_BOTTOM_BORDER for a in br))      # These are relative to entire screenshot

                # Make sure the minimap is larger than player_template
                if mm_br[0] - mm_tl[0] < Capture.player_template.shape[1] or mm_br[1] - mm_tl[1] < Capture.player_template.shape[0]:
                    mm_br = (mm_tl[0] + Capture.player_template.shape[1], mm_tl[1] + Capture.player_template.shape[0])
                
                # Crop the frame to only show the minimap
                minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                tl, br = Capture._match_template(minimap, Capture.player_template)           
                raw_player_pos = tuple((br[i] + tl[i]) / 2 for i in range(2))
                player_pos = (raw_player_pos[0] / minimap.shape[1], raw_player_pos[1] / minimap.shape[0])       # player_pos is relative to the minimap's inner box
                print(player_pos)
                # print(player_pos[0], player_pos[1])
                # print(enabled.value)
                # print(self.player_pos[0], self.player_pos[1])

                cv2.circle(minimap, tuple(round(a) for a in raw_player_pos), 3, (255, 0, 0), -1)
                # cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) * target[0]), round((mm_br[1] - mm_tl[1]) * target[1])), 3, (0, 255, 0), -1)
                # cv2.rectangle(frame, mm_tl, mm_br, (0, 0, 255), 1)
                # cv2.rectangle(frame, tl, br, (0, 0, 255), 3)
                # cv2.circle(frame, tuple(a - MINIMAP_BOTTOM_BORDER for a in br), 3, (0, 255, 0), -1)
                for i in range(10):
                    color = (0, 0, 255) if i == 5 else (0, 255, 255)
                    cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) * (i + 1) / 10), round((mm_br[1] - mm_tl[1]) / 2)), 1, color, 1)
                    cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) / 2), round((mm_br[1] - mm_tl[1]) * (i + 1) / 10)), 1, color, 1)

                for element in sequence:
                    cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) * element.location[0]), round((mm_br[1] - mm_tl[1]) * element.location[1])), 3, (0, 255, 0), -1)

                # cv2.imshow('test', _rescale_frame(frame, percent=75))
                cv2.imshow('mm', minimap)
                # cv2.imshow('mm', Capture._rescale_frame(minimap, percent=300))

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

    def teleport(self, direction):
        assert direction in ['left', 'up', 'right', 'down'], f"'{direction}' is not a recognized direction."

        key_down(direction)
        time.sleep(0.05)
        press('space', 1, up_time=0.05)
        if direction == 'up':
            time.sleep(0.1)
        else:
            time.sleep(0.2)        # Down jump needs more time to accelerate
        press('e', 2)
        key_up(direction)
        time.sleep(0.1)

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
        time.sleep(0.3)
        press('lshift', 3, down_time=0.1)
    
    def boss(self):
        time.sleep(0.15)
        if player_pos[0] > 0.5:     # Always cast Yaksha Boss facing the center of the map
            press('left', 1, down_time=0.1)
        else:
            press('right', 1, down_time=0.1)
        press('2', 2, down_time=0.1, up_time=0.2)


class Point:
    def __init__(self, location, attack=True, n=2, extras=[]):
        self.location = location
        self.attack = attack
        self.n = n
        self.extras = extras

    def execute(self):
        move(self.location)
        for e in self.extras:
            exec(f'commands.{e}()')
        if self.attack:
            commands.shikigami('left', self.n)
            commands.shikigami('right', self.n)
        

#################################
#        Initialization         #
#################################
sequence = [Point((0.37, 0.82)),
            Point((0.33, 0.58)),
            Point((0.3, 0.24)),
            Point((0.5, 0.35), attack=False, extras=['kishin']),
            Point((0.71, 0.25)),
            Point((0.70, 0.58), attack=False, extras=['boss']),
            Point((0.65, 0.82))]

sequence = [Point((0.49, 0.44), attack=False, extras=['kishin']),
            Point((0.44, 0.77)),
            Point((0.82, 0.77), attack=False, extras=['boss']),
            Point((0.77, 0.28)),
            Point((0.65, 0.77)),
            Point((0.44, 0.77))]

sequence = [Point((0.515, 0.64)),
            Point((0.85, 0.75), attack=False, extras=['boss']),
            Point((0.75, 0.25), attack=False, extras=['kishin']),
            Point((0.515, 0.64)),
            Point((0.242, 0.75)),
            Point((0.258, 0.25))]


#################################
#             Mains             #
#################################
def main():
    gui = tk.Tk()
    gui.geometry('300x50')      # +0-1080

    b_start = tk.Button(gui, text='Start', command=start)
    b_start.pack()

    b_stop = tk.Button(gui, text='Stop', command=stop)
    b_stop.pack()

    gui.call('wm', 'attributes', '.', '-topmost', '1')
    gui.mainloop()

def bot():
    print('started bot')
    
    index = 0
    b = buff(0)
    while True: 
        if enabled:
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

def distance(a, b):
    return math.sqrt(sum([(a[i] - b[i]) ** 2 for i in range(2)]))

def move(target):     
    while distance(player_pos, target) > POSITION_TOLERANCE:
        if player_pos[0] < target[0]:
            commands.teleport('right')
        else:
            commands.teleport('left')

        if abs(player_pos[1] - target[1]) > POSITION_TOLERANCE:
            if player_pos[1] < target[1]:
                commands.teleport('down')
            else:
                commands.teleport('up')

def buff(time):
    def act(new_time):
        if time == 0 or new_time - time > 180:
            press('ctrl', 2, up_time=0.2)
            press('end', 3, up_time=0.3)
            press('9', 4, up_time=0.3)
            press('0', 4, up_time=0.3)
        else:
            new_time = time
        return buff(new_time)
    return act

def start():
    time.sleep(10)
    global enabled
    enabled = True

def stop():
    global enabled
    enabled = False

# def toggle_enabled():
#     print('toggled')
#     global enabled
#     if enabled:
#         enabled = False
#     # else:
#     #     main()


if __name__ == '__main__':
    capture = Capture()
    capture.cap.start()

    commands = Commands()
    # commands.tengu.start()

    bt = threading.Thread(target=bot)
    bt.daemon = True
    bt.start()

    # enabled = True
    # while True:
    #     time.sleep(10)
    main()