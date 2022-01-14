"""An interpreter that reads and executes user-created routines."""

import config
import detection
import threading
import time
import mss
import mss.windows
import utils
import pygame
import inspect
import components
import keyboard as kb
import numpy as np
from os.path import splitext, basename
from routine import Routine
from components import Point
from vkeys import press, click


class Bot:
    """A class that interprets and executes user-defined routines."""

    alert = None
    buff = components.DefaultBuff()

    def __init__(self):
        """Loads a user-defined routine on start up and initializes this Bot's main thread."""

        pygame.mixer.init()
        Bot.alert = pygame.mixer.music
        Bot.alert.load('./assets/alert.mp3')

        config.command_book = {}
        for c in (components.Wait, components.Walk, components.Fall,
                  components.DefaultStep, components.DefaultAdjust, components.DefaultBuff):
            config.command_book[c.__name__.lower()] = c

        config.routine = Routine()

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts this Bot object's thread.
        :return:    None
        """

        print('\n[~] Started main bot loop.')
        self.thread.start()

    def _main(self):
        """
        The main body of Bot that executes the user's routine.
        :return:    None
        """

        print('\n[~] Initializing detection algorithm...\n')
        model = detection.load_model()
        print('\n[~] Initialized detection algorithm.')

        mss.windows.CAPTUREBLT = 0
        with mss.mss() as sct:
            self.ready = True
            config.listening = True
            while True:
                if config.alert_active:
                    Bot._alert()
                if config.enabled and len(config.routine) > 0:
                    Bot.buff.main()

                    # Highlight the current Point
                    config.gui.view.routine.select(config.routine.index)
                    config.gui.view.details.display_info(config.routine.index)

                    # Execute next Point in the routine
                    element = config.routine[config.routine.index]
                    element.execute()
                    if config.rune_active and isinstance(element, Point) \
                            and element.location == config.rune_closest_pos:
                        Bot._solve_rune(model, sct)
                    Bot._step()
                else:
                    time.sleep(0.01)

    @staticmethod
    @utils.run_if_enabled
    def _solve_rune(model, sct):
        """
        Moves to the position of the rune and solves the arrow-key puzzle.
        :param model:   The TensorFlow model to classify with.
        :param sct:     The mss instance object with which to take screenshots.
        :return:        None
        """

        move = config.command_book['move']
        move(*config.rune_pos).execute()
        adjust = config.command_book['adjust']
        adjust(*config.rune_pos).execute()
        time.sleep(0.2)
        press('y', 1, down_time=0.2)        # Press 'y' to interact with rune in-game
        print('\nSolving rune:')
        inferences = []
        for _ in range(15):
            frame = np.array(sct.grab(config.MONITOR))
            solution = detection.merge_detection(model, frame)
            if solution:
                print(', '.join(solution))
                if solution in inferences:
                    print('Solution found, entering result.')
                    for arrow in solution:
                        press(arrow, 1, down_time=0.1)
                    time.sleep(1)
                    for _ in range(3):
                        time.sleep(0.3)
                        frame = np.array(sct.grab(config.MONITOR))
                        rune_buff = utils.multi_match(frame[:frame.shape[0]//8, :],
                                                      config.RUNE_BUFF_TEMPLATE,
                                                      threshold=0.9)
                        if rune_buff:
                            rune_buff_pos = min(rune_buff, key=lambda p: p[0])
                            click(rune_buff_pos, button='right')
                    break
                elif len(solution) == 4:
                    inferences.append(solution)
        config.rune_active = False

    @staticmethod
    def _alert():
        """
        Plays an alert to notify user of a dangerous event. Stops the alert
        once 'insert' is pressed.
        :return:    None
        """

        config.listening = False
        Bot.alert.play(-1)
        while not kb.is_pressed('insert'):
            time.sleep(0.1)
        Bot.alert.stop()
        config.alert_active = False
        time.sleep(1)
        config.listening = True

    @staticmethod
    @utils.run_if_enabled
    def _step():
        """Increments config.seq_index and wraps back to 0 at the end of config.sequence."""

        config.routine.index = (config.routine.index + 1) % len(config.routine)

    @staticmethod
    def load_commands(file):
        """Prompts the user to select a command module to import. Updates config's command book."""

        utils.print_separator()
        print(f"[~] Loading command book '{basename(file)}':")

        ext = splitext(file)[1]
        if ext != '.py':
            print(f" !  '{ext}' is not a supported file extension.")
            return

        # Generate a command book using the selected module
        module_name = splitext(basename(file))[0]
        module = __import__(f'command_books.{module_name}', fromlist=[''])
        new_cb = {}
        for c in (components.Wait, components.Walk, components.Fall):
            new_cb[c.__name__.lower()] = c

        for name, command in inspect.getmembers(module, inspect.isclass):
            name = name.lower()
            new_cb[name] = command

        # Check if required commands have been implemented
        success = True
        for command in ['step', 'adjust', 'buff']:      # TODO: change move to step
            if command not in new_cb:
                success = False
                print(f" !  Error: Must implement '{command}' command.")

        if success:
            config.command_book = new_cb
            config.gui.view.status.set_cb(basename(file))
            Bot.buff = new_cb['buff']()

            # Clear the current routine and Layout because command book changed
            config.routine.clear()

            print(f"[~] Successfully loaded command book '{module_name}'.")
        else:
            print(f"[!] Command book '{module_name}' was not loaded.")
        return success
