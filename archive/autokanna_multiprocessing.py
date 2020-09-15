import mss, cv2, time, multiprocessing, vkeys, time, math
import numpy as np
import keyboard as kb
import tkinter as tk
from vkeys import key_down, key_up


#################################
#       Global Variables        #
#################################
POSITION_TOLERANCE = 0.1

player_pos = multiprocessing.Array('d', [0, 0])
# print(player_pos[0])
enabled = multiprocessing.Value('i', 0)
tengu_on = multiprocessing.Value('i', 0)
# print(enabled.value)
# if __name__ == '__main__':
#     ns = multiprocessing.Manager().Namespace()
#     ns.player_pos = (0, 0)
#     ns.enabled = False
# target = (0.35, 0.35)
# target = (0.5, 0.35)


#################################
#            Classes            #
#################################
class Capture:
    MINIMAP_TOP_BORDER = 20
    MINIMAP_BOTTOM_BORDER = 8

    minimap_template = cv2.imread('assets/minimap_template.jpg', 0)
    player_template = cv2.imread('assets/dot_template.png', 0)

    
    def __init__(self, player_pos):
        self.cap = multiprocessing.Process(target=self._capture)
        self.cap.daemon = True
        self.player_pos = player_pos

    def _capture(self):
        with mss.mss() as sct:
            print('started capture')

            # global player_pos
            # global cv2
            monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
            while True:
                # print('running capture')

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
                self.player_pos[:] = [raw_player_pos[0] / minimap.shape[1], raw_player_pos[1] / minimap.shape[0]]       # player_pos is relative to the minimap's inner box
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
capture = Capture(player_pos)

class Commands:
    # tengu_on = None


    def __init__(self, player_pos, enabled, tengu_on):
        self.tengu = multiprocessing.Process(target=self._tengu)         # Tengu thread continuously uses Tengu Strike unless tengu_on is set to False
        self.tengu.daemon = True     # Daemon threads end when the main thread ends
        self.player_pos = player_pos
        self.enabled = enabled
        self.tengu_on = tengu_on

    def _tengu(self):
        print('started tengu')
        while True:
            # if False:
            # enabled.acquire()
            if self.tengu_on and self.enabled.value:      # Commands.tengu_on.value and
                # enabled.release()
                print('running tengu')
                key_down('q')
                time.sleep(0.2)
                key_up('q')
                time.sleep(1.75)

    def teleport(self, direction):
        assert direction in ['left', 'up', 'right', 'down'], f"'{direction}' is not a recognized direction."

        key_down(direction)
        time.sleep(0.05)
        if direction in ['up', 'down']:
            key_down('space')
            time.sleep(0.05)
            key_up('space')
            if direction == 'up':
                time.sleep(0.1)
            else:
                time.sleep(0.25)        # Down jump needs more time to accelerate
        
        # for _ in range(4):      # Press the teleport key twice to ensure it registers in-game
        #     key_down('e')
        #     time.sleep(0.075)
        #     key_up('e')
        #     time.sleep(0.01)

        for _ in range(3):      # Press the teleport key twice to ensure it registers in-game
            key_down('e')
            time.sleep(0.1)
            key_up('e')
            time.sleep(0.01)

        key_up(direction)
        time.sleep(0.125)

    def shikigami(self, direction, n=1):
        assert direction in ['left', 'right'], 'Shikigami Haunting can only be used in the left and right directions.'

        key_down(direction)
        time.sleep(0.05)

        for _ in range(n):
            # print(i)
            for _ in range(6):
                key_down('r')
                time.sleep(0.075)
                key_up('r')
                time.sleep(0.075)
                # kb.send('r')
                # time.sleep(0.15)
            time.sleep(0.075)

        key_up(direction)
        time.sleep(0.1)

    def kishin(self):
        time.sleep(0.3)
        for _ in range(3):
            key_down('lshift')
            time.sleep(0.1)
            key_up('lshift')
            time.sleep(0.1)
    
    def boss(self):
        time.sleep(0.15)
        print(self.player_pos[0])
        if self.player_pos[0] > 0.5:     # Always cast Yaksha Boss facing the center of the map
            key_down('left')
            time.sleep(0.1)
            key_up('left')
            time.sleep(0.1)
        else:
            key_down('right')
            time.sleep(0.1)
            key_up('right')
            time.sleep(0.1)
        for _ in range(3):
            key_down('2')
            time.sleep(0.1)
            key_up('2')
            time.sleep(0.1)
commands = Commands(player_pos, enabled, tengu_on)

class Point:
    def __init__(self, location, attack=True, n=2, extras=[]):
        self.location = location
        self.attack = attack
        self.n = n
        self.extras = extras

    def execute(self, player_pos):
        move(self.location, player_pos)
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


#################################
#             Mains             #
#################################
def main():
    gui = tk.Tk()
    gui.geometry('300x50')

    b_start = tk.Button(gui, text='Start', command=start)
    b_start.pack()

    b_stop = tk.Button(gui, text='Stop', command=stop)
    b_stop.pack()

    gui.call('wm', 'attributes', '.', '-topmost', '1')
    gui.mainloop()

def bot(enabled, player_pos):
    print('started bot')
    # global ns
    # global enabled
    # enabled = True
    
    index = 0
    # print(player_pos)
    while True: 
        if enabled.value:
            # print('running bot')
            # global index
            point = sequence[index]
            # print(point.location)
            # move(target)
            # move_next()
            # commands.shikigami('left', 2)
            # commands.shikigami('right', 2)
            # if index == 3:
            #     time.sleep(0.5)
            #     commands.kishin()
            point.execute(player_pos)
            index = (index + 1) % len(sequence)


#################################
#           Functions           #
#################################
def distance(a, b):
    return math.sqrt(sum([(a[i] - b[i]) ** 2 for i in range(2)]))

def move(target, player_pos):
    Commands.tengu_on = False       # TODO: need to change this!!!
    while distance(tuple(i for i in player_pos), target) > POSITION_TOLERANCE:
        # print(player_pos[0], player_pos[1])
        # print(f'p: {player_pos}\nt:{target}')
        # Teleport horizontally before teleporting vertically
        if player_pos[0] < target[0]:
            commands.teleport('right')
        else:
            commands.teleport('left')

        if abs(player_pos[1] - target[1]) > POSITION_TOLERANCE:
            if player_pos[1] < target[1]:
                commands.teleport('down')
            else:
                commands.teleport('up')
        time.sleep(0.15)
    Commands.tengu_on = True

def start():
    global enabled, tengu_on
    enabled.value = 1
    tengu_on.value = 1
    print(enabled.value)
    # Commands.tengu_on = True
    # bot()

def stop():
    global enabled, tengu_on
    enabled.value = 0
    tengu_on.value = 0
    print(enabled.value)
    # Commands.tengu_on = False

# def toggle_enabled():
#     print('toggled')
#     global enabled
#     if enabled:
#         enabled = False
#     # else:
#     #     main()


if __name__ == '__main__':
    # ns = multiprocessing.Manager().Namespace()
    # ns.player_pos = (0, 0)
    # ns.enabled = False
    # manager = multiprocessing.Manager()
    
    # enabled.value = False
    # print(ns)

    
    capture.cap.start()

    
    commands.tengu.start()

    print('flag')

    bt = multiprocessing.Process(target=bot, args=(enabled, player_pos))
    bt.daemon = True
    bt.start()

    enabled.value = True
    while True:
        time.sleep(10)
    # main()