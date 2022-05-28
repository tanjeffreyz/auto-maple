"""An interpreter that reads and executes user-created routines."""

import threading
import time
import git
import cv2
import inspect
from os.path import splitext, basename
from src.common import config, utils
from src.detection import detection
from src.routine import components
from src.routine.routine import Routine
from src.routine.components import Point
from src.common.vkeys import press, click
from src.common.interfaces import Configurable


# The rune's buff icon
RUNE_BUFF_TEMPLATE = cv2.imread('assets/rune_buff_template.jpg', 0)


class Bot(Configurable):
    """A class that interprets and executes user-defined routines."""

    DEFAULT_CONFIG = {
        'Interact': 'y',
        'Feed pet': '9'
    }

    def __init__(self):
        """Loads a user-defined routine on start up and initializes this Bot's main thread."""

        super().__init__('keybindings')
        config.bot = self

        self.rune_active = False
        self.rune_pos = (0, 0)
        self.rune_closest_pos = (0, 0)      # Location of the Point closest to rune
        self.submodules = {}
        self.module_name = None
        self.buff = components.Buff()

        self.command_book = {}
        for c in (components.Wait, components.Walk, components.Fall,
                  components.Move, components.Adjust, components.Buff):
            self.command_book[c.__name__.lower()] = c

        config.routine = Routine()

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts this Bot object's thread.
        :return:    None
        """

        self.update_submodules()
        print('\n[~] Started main bot loop')
        self.thread.start()

    def _main(self):
        """
        The main body of Bot that executes the user's routine.
        :return:    None
        """

        print('\n[~] Initializing detection algorithm:\n')
        model = detection.load_model()
        print('\n[~] Initialized detection algorithm')

        self.ready = True
        config.listener.enabled = True
        last_fed = time.time()
        while True:
            if config.enabled and len(config.routine) > 0:
                # Buff and feed pets
                self.buff.main()
                pet_settings = config.gui.settings.pets
                auto_feed = pet_settings.auto_feed.get()
                num_pets = pet_settings.num_pets.get()
                now = time.time()
                if auto_feed and now - last_fed > 1200 / num_pets:
                    press(self.config['Feed pet'], 1)
                    last_fed = now

                # Highlight the current Point
                config.gui.view.routine.select(config.routine.index)
                config.gui.view.details.display_info(config.routine.index)

                # Execute next Point in the routine
                element = config.routine[config.routine.index]
                if self.rune_active and isinstance(element, Point) \
                        and element.location == self.rune_closest_pos:
                    self._solve_rune(model)
                element.execute()
                config.routine.step()
            else:
                time.sleep(0.01)

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
            frame = config.capture.screenshot()
            if frame is None:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
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
                        frame = config.capture.screenshot()
                        if frame is None:
                            continue
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        rune_buff = utils.multi_match(frame[:frame.shape[0] // 8, :],
                                                      RUNE_BUFF_TEMPLATE,
                                                      threshold=0.9)
                        if rune_buff:
                            rune_buff_pos = min(rune_buff, key=lambda p: p[0])
                            target = tuple(round(rune_buff_pos[i] + config.capture.window[i])
                                           for i in range(2))
                            click(target, button='right')
                    self.rune_active = False
                    break
                elif len(solution) == 4:
                    inferences.append(solution)

    def load_commands(self, file):
        """Prompts the user to select a command module to import. Updates config's command book."""

        utils.print_separator()
        print(f"[~] Loading command book '{basename(file)}':")

        ext = splitext(file)[1]
        if ext != '.py':
            print(f" !  '{ext}' is not a supported file extension.")
            return False

        new_step = components.step
        new_cb = {}
        for c in (components.Wait, components.Walk, components.Fall):
            new_cb[c.__name__.lower()] = c

        # Import the desired command book file
        module_name = splitext(basename(file))[0]
        target = '.'.join(['resources', 'command_books', module_name])
        module = __import__(target, fromlist=[''])

        # Check if the 'step' function has been implemented
        step_found = False
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name.lower() == 'step':
                step_found = True
                new_step = func

        # Populate the new command book
        for name, command in inspect.getmembers(module, inspect.isclass):
            new_cb[name.lower()] = command

        # Check if required commands have been implemented and overridden
        required_found = True
        for command in [components.Buff]:
            name = command.__name__.lower()
            if name not in new_cb:
                required_found = False
                new_cb[name] = command
                print(f" !  Error: Must implement required command '{name}'.")

        # Look for overridden movement commands
        movement_found = True
        for command in (components.Move, components.Adjust):
            name = command.__name__.lower()
            if name not in new_cb:
                movement_found = False
                new_cb[name] = command

        if not step_found and not movement_found:
            print(f" !  Error: Must either implement both 'Move' and 'Adjust' commands, "
                  f"or the function 'step'.")
        if required_found and (step_found or movement_found):
            self.module_name = module_name
            self.command_book = new_cb
            self.buff = new_cb['buff']()
            components.step = new_step
            config.gui.menu.file.enable_routine_state()
            config.gui.view.status.set_cb(basename(file))
            config.routine.clear()
            print(f" ~  Successfully loaded command book '{module_name}'.")
            return True
        else:
            print(f" !  Command book '{module_name}' was not loaded.")
            return False

    def update_submodules(self, force=False):
        print('\n[~] Retrieving latest submodules:')
        repo = git.Repo.init()
        changed = False
        with open('.gitmodules', 'r') as file:
            lines = file.readlines()
            i = 0
            while i < len(lines):
                if lines[i].startswith('[') and i < len(lines) - 2:
                    path = lines[i + 1].split('=')[1].strip()
                    url = lines[i + 2].split('=')[1].strip()
                    self.submodules[path] = url
                    try:        # First time loading submodule
                        repo.git.clone(url, path)
                        changed = True
                        print(f" -  Initialized submodule '{path}'")
                    except git.exc.GitCommandError:
                        sub_repo = git.Repo(path)
                        if force:
                            sub_repo.git.fetch('origin', 'main')
                            sub_repo.git.reset('--hard', 'FETCH_HEAD')
                            changed = True
                            print(f" -  Force-updated submodule '{path}'")
                        else:
                            try:
                                sub_repo.git.pull('origin', 'main')
                                changed = True
                                print(f" -  Updated submodule '{path}'")
                            except git.exc.GitCommandError:
                                print(f" !  Uncommitted changes in submodule '{path}'")
                    i += 3
                else:
                    i += 1
        if not changed:
            print(' ~  All submodules are already up to date')
