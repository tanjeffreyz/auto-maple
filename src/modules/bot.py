"""
[機器人核心模組]
這是整個程式的總指揮。它負責：
1. 載入 AI 模型 (用來看懂輪的箭頭)。
2. 不斷檢查現在該做什麼動作。
3. 執行腳本裡的指令。
"""

import threading
import time
import git
import cv2
import inspect
import importlib
import traceback
from os.path import splitext, basename
from src.common import config, utils
from src.detection import detection
from src.routine import components
from src.routine.routine import Routine
from src.command_book.command_book import CommandBook
from src.routine.components import Point
from src.common.vkeys import press, click
from src.common.interfaces import Configurable


# 讀取「輪」解完後的 Buff 圖示，用來確認有沒有解成功
RUNE_BUFF_TEMPLATE = cv2.imread('assets/rune_buff_template.jpg', 0)


class Bot(Configurable):
    """
    Bot 類別：負責解釋並執行你寫好的腳本。
    """

    # 預設的按鍵設定 (如果沒有讀取到設定檔會用這個)
    DEFAULT_CONFIG = {
        'Interact': 'y',  # 採集/對話鍵 (解輪用)
        'Feed pet': '9'   # 餵寵物鍵
    }

    def __init__(self):
        """程式啟動時會執行這裡，進行初始化。"""
        super().__init__('keybindings')
        config.bot = self

        self.rune_active = False        # 現在是不是有輪出現？
        self.rune_pos = (0, 0)          # 輪在哪裡？
        self.rune_closest_pos = (0, 0)  # 離輪最近的腳本點位在哪？
        self.submodules = []
        self.command_book = None        # 目前載入的職業指令書
        
        config.routine = Routine()      # 初始化腳本管理器

        self.ready = False
        # 建立一個獨立的執行緒 (Thread) 來跑機器人，這樣才不會卡死介面
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """按下開始後，啟動機器人的主迴圈。"""
        self.update_submodules()
        print('\n[~] 已啟動機器人主迴圈')
        self.thread.start()

    def _main(self):
        """
        [核心迴圈]
        這就是機器人一直在做的事情，就像人的心跳一樣不會停。
        """
        print('\n[~] 正在載入 AI 偵測模型 (這可能需要一點時間)...\n')
        model = detection.load_model()
        print('\n[~] AI 模型載入完成！')

        self.ready = True
        config.listener.enabled = True
        last_fed = time.time()  # 紀錄上次餵寵物的時間

        while True:
            # 只有在「啟用中 (enabled)」且「腳本不為空」時才做事
            if config.enabled and len(config.routine) > 0:
                
                # 1. 執行自動放技能 (Buff)
                self.command_book.buff.main()
                
                # 2. 檢查寵物是不是餓了
                pet_settings = config.gui.settings.pets
                auto_feed = pet_settings.auto_feed.get()
                num_pets = pet_settings.num_pets.get()
                now = time.time()
                
                # 如果開啟自動餵食，且時間到了 (根據寵物數量計算間隔)
                if auto_feed and now - last_fed > 1200 / num_pets:
                    press(self.config['Feed pet'], 1)
                    last_fed = now

                # 3. 在介面上高亮顯示目前執行到的步驟
                config.gui.view.routine.select(config.routine.index)
                config.gui.view.details.display_info(config.routine.index)

                # 4. 取得這一步驟的動作 (Point)
                element = config.routine[config.routine.index]
                
                # 如果有輪出現，而且我們剛好走到了負責解輪的點位
                if self.rune_active and isinstance(element, Point) \
                        and element.location == self.rune_closest_pos:
                    self._solve_rune(model) # 去解輪！
                
                # 5. 執行這個點位的動作 (移動、跳躍、攻擊...)
                element.execute()
                
                # 6. 前往腳本的下一步
                config.routine.step()
            else:
                # 如果沒事做，休息 0.01 秒避免電腦太操勞
                time.sleep(0.01)

    # ... (後續的 _solve_rune 等函式暫時省略，先讓同事理解主迴圈即可) ...
    # 為了保持檔案完整性，若需要完整檔案請告訴我，這裡先展示核心邏輯中文化。
    # 建議同事在修改時，只需替換上述有中文註解的部分，保留原有的 auxiliary functions。

    @utils.run_if_enabled
    def _solve_rune(self, model):
        """
        Moves to the position of the rune and solves the arrow-key puzzle.
        :param model:   The TensorFlow model to classify with.
        :param sct:     The mss instance object with which to take screenshots.
        :return:        None
        """

        move = self.command_book['move']
        move(*self.rune_pos).execute()
        adjust = self.command_book['adjust']
        adjust(*self.rune_pos).execute()
        time.sleep(0.2)
        press(self.config['Interact'], 1, down_time=0.2)        # Inherited from Configurable

        print('\nSolving rune:')
        inferences = []
        for _ in range(15):
            frame = config.capture.frame
            solution = detection.merge_detection(model, frame)
            if solution:
                print(', '.join(solution))
                if solution in inferences:
                    print('Solution found, entering result')
                    for arrow in solution:
                        press(arrow, 1, down_time=0.1)
                    time.sleep(1)
                    for _ in range(3):
                        time.sleep(0.3)
                        frame = config.capture.frame
                        rune_buff = utils.multi_match(frame[:frame.shape[0] // 8, :],
                                                      RUNE_BUFF_TEMPLATE,
                                                      threshold=0.9)
                        if rune_buff:
                            rune_buff_pos = min(rune_buff, key=lambda p: p[0])
                            target = (
                                round(rune_buff_pos[0] + config.capture.window['left']),
                                round(rune_buff_pos[1] + config.capture.window['top'])
                            )
                            click(target, button='right')
                    self.rune_active = False
                    break
                elif len(solution) == 4:
                    inferences.append(solution)

    def load_commands(self, file):
        try:
            self.command_book = CommandBook(file)
            config.gui.settings.update_class_bindings()
        except ValueError:
            pass    # TODO: UI warning popup, say check cmd for errors
        #
        # utils.print_separator()
        # print(f"[~] Loading command book '{basename(file)}':")
        #
        # ext = splitext(file)[1]
        # if ext != '.py':
        #     print(f" !  '{ext}' is not a supported file extension.")
        #     return False
        #
        # new_step = components.step
        # new_cb = {}
        # for c in (components.Wait, components.Walk, components.Fall):
        #     new_cb[c.__name__.lower()] = c
        #
        # # Import the desired command book file
        # module_name = splitext(basename(file))[0]
        # target = '.'.join(['resources', 'command_books', module_name])
        # try:
        #     module = importlib.import_module(target)
        #     module = importlib.reload(module)
        # except ImportError:     # Display errors in the target Command Book
        #     print(' !  Errors during compilation:\n')
        #     for line in traceback.format_exc().split('\n'):
        #         line = line.rstrip()
        #         if line:
        #             print(' ' * 4 + line)
        #     print(f"\n !  Command book '{module_name}' was not loaded")
        #     return
        #
        # # Check if the 'step' function has been implemented
        # step_found = False
        # for name, func in inspect.getmembers(module, inspect.isfunction):
        #     if name.lower() == 'step':
        #         step_found = True
        #         new_step = func
        #
        # # Populate the new command book
        # for name, command in inspect.getmembers(module, inspect.isclass):
        #     new_cb[name.lower()] = command
        #
        # # Check if required commands have been implemented and overridden
        # required_found = True
        # for command in [components.Buff]:
        #     name = command.__name__.lower()
        #     if name not in new_cb:
        #         required_found = False
        #         new_cb[name] = command
        #         print(f" !  Error: Must implement required command '{name}'.")
        #
        # # Look for overridden movement commands
        # movement_found = True
        # for command in (components.Move, components.Adjust):
        #     name = command.__name__.lower()
        #     if name not in new_cb:
        #         movement_found = False
        #         new_cb[name] = command
        #
        # if not step_found and not movement_found:
        #     print(f" !  Error: Must either implement both 'Move' and 'Adjust' commands, "
        #           f"or the function 'step'")
        # if required_found and (step_found or movement_found):
        #     self.module_name = module_name
        #     self.command_book = new_cb
        #     self.buff = new_cb['buff']()
        #     components.step = new_step
        #     config.gui.menu.file.enable_routine_state()
        #     config.gui.view.status.set_cb(basename(file))
        #     config.routine.clear()
        #     print(f" ~  Successfully loaded command book '{module_name}'")
        # else:
        #     print(f" !  Command book '{module_name}' was not loaded")

    def update_submodules(self, force=False):
        """
        Pulls updates from the submodule repositories. If FORCE is True,
        rebuilds submodules by overwriting all local changes.
        """

        utils.print_separator()
        print('[~] Retrieving latest submodules:')
        self.submodules = []
        repo = git.Repo.init()
        with open('.gitmodules', 'r') as file:
            lines = file.readlines()
            i = 0
            while i < len(lines):
                if lines[i].startswith('[') and i < len(lines) - 2:
                    path = lines[i + 1].split('=')[1].strip()
                    url = lines[i + 2].split('=')[1].strip()
                    self.submodules.append(path)
                    try:
                        repo.git.clone(url, path)       # First time loading submodule
                        print(f" -  Initialized submodule '{path}'")
                    except git.exc.GitCommandError:
                        sub_repo = git.Repo(path)
                        if not force:
                            sub_repo.git.stash()        # Save modified content
                        sub_repo.git.fetch('origin', 'main')
                        sub_repo.git.reset('--hard', 'FETCH_HEAD')
                        if not force:
                            try:                # Restore modified content
                                sub_repo.git.checkout('stash', '--', '.')
                                print(f" -  Updated submodule '{path}', restored local changes")
                            except git.exc.GitCommandError:
                                print(f" -  Updated submodule '{path}'")
                        else:
                            print(f" -  Rebuilt submodule '{path}'")
                        sub_repo.git.stash('clear')
                    i += 3
                else:
                    i += 1
