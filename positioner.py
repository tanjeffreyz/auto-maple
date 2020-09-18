# from autokanna import Capture

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

                # for x in [25 * i for i in range(77)]:
                #     color = (0, 255, 0) if x % 100 else (255, 0, 0)
                #     cv2.circle(frame, (x, 540), 3, color, -1)
                
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
                # print(minimap.shape[1] / minimap.shape[0])
                # print(player_pos)

                # cv2.circle(minimap, tuple(round(a) for a in raw_player_pos), 3, (255, 0, 0), -1)
                # cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) * target[0]), round((mm_br[1] - mm_tl[1]) * target[1])), 3, (0, 255, 0), -1)
                # cv2.rectangle(frame, mm_tl, mm_br, (0, 0, 255), 1)
                # cv2.rectangle(frame, tl, br, (0, 0, 255), 3)
                # cv2.circle(frame, tuple(a - MINIMAP_BOTTOM_BORDER for a in br), 3, (0, 255, 0), -1)

                # for i in range(10):
                #     color = (0, 0, 255) if i == 5 else (0, 255, 255)
                #     cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) * (i + 1) / 10), round((mm_br[1] - mm_tl[1]) / 2)), 1, color, 1)
                #     cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) / 2), round((mm_br[1] - mm_tl[1]) * (i + 1) / 10)), 1, color, 1)

                # for element in sequence:
                #     cv2.circle(minimap, (round((mm_br[0] - mm_tl[0]) * element.location[0]), round((mm_br[1] - mm_tl[1]) * element.location[1])), 3, (0, 255, 0), -1)

                # cv2.imshow('mm', minimap)

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



pos_cap = Capture()
pos_cap.cap.start()

