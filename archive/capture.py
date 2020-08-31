import mss, cv2, time, threading, vkeys
import numpy as np
# from vkeys import key_down, key_up
# import commands as c
# from autokanna import target    # just for testing, remove later

#################################
#       Global Variables        #
#################################
MINIMAP_TOP_BORDER = 20
MINIMAP_BOTTOM_BORDER = 8

minimap_template = cv2.imread('assets/minimap_template.jpg', 0)
player_template = cv2.imread('assets/dot_template.png', 0)

player_pos = (0, 0)
# cv2.imshow('gray?', template)
# cv2.waitKey(0)
target = (0.5, 0.35)

#################################
#              Main             #
#################################
def _capture():
    global player_pos
    
    # c.tengu.start()
    # c.teleport.start()
    # count = 0

    with mss.mss() as sct:
        monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
        while True:
            # key_down('e')

            frame = np.array(sct.grab(monitor))
            for x in [25 * i for i in range(77)]:
                color = (0, 255, 0) if x % 100 else (255, 0, 0)
                cv2.circle(frame, (x, 540), 3, color, -1)
            
            # Get the bottom right point of the minimap
            _, br = _match_template(frame, minimap_template)
            mm_tl, mm_br = (MINIMAP_BOTTOM_BORDER, MINIMAP_TOP_BORDER), (tuple(a - MINIMAP_BOTTOM_BORDER for a in br))      # These are relative to entire screenshot

            # Make sure the minimap is larger than player_template
            if mm_br[0] - mm_tl[0] < player_template.shape[1] or mm_br[1] - mm_tl[1] < player_template.shape[0]:
                mm_br = (mm_tl[0] + player_template.shape[1], mm_tl[1] + player_template.shape[0])
            
            # Crop the frame to only show the minimap
            minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
            tl, br = _match_template(minimap, player_template)           
            raw_player_pos = tuple((br[i] + tl[i]) / 2 for i in range(2))
            player_pos = (raw_player_pos[0] / minimap.shape[1], raw_player_pos[1] / minimap.shape[0])       # player_pos is relative to the minimap's inner box
            # print(count, player_pos[0], player_pos[1])
            # count += 1
            # print(player_pos[0], player_pos[1])
            # print(minimap.shape[1])

            cv2.circle(minimap, tuple(round(a) for a in raw_player_pos), 3, (255, 0, 0), -1)
            cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) * target[0]), round((mm_br[1] - mm_tl[1]) * target[1])), 3, (0, 255, 0), -1)
            # cv2.rectangle(frame, mm_tl, mm_br, (0, 0, 255), 1)
            # cv2.rectangle(frame, tl, br, (0, 0, 255), 3)
            # cv2.circle(frame, tuple(a - MINIMAP_BOTTOM_BORDER for a in br), 3, (0, 255, 0), -1)

            # cv2.imshow('test', _rescale_frame(frame, percent=75))
            cv2.imshow('mm', minimap)

            # print(c.ready)eeqqqqqqqqqeeqqqqqqqqqqeeqqqqqqqqq
            # print(c.teleport.is_alive())
            # if c.ready and not c.teleport.is_alive():
            #     c.teleport.start()
            # for thread in threading.enumerate():
            #     print(thread.name, c.ready)


            if cv2.waitKey(1) & 0xFF == 27:     # 27 is ASCII for the Esc key on a keyboard
                break
            
            # key_up('e')
cap = threading.Thread(target=_capture)
cap.daemon = True

#################################
#          Functions            #
#################################
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