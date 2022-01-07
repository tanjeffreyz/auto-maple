"""An interpreter that reads and executes user-created routines."""

import config
import detection
import threading
import time
import mss
import utils
import pygame
import inspect
import commands
import keyboard as kb
import numpy as np
from os.path import splitext, basename
from routine import Point, Routine
from vkeys import press, click


class Bot:
    """A class that interprets and executes user-defined routines."""

    alert = None
    buff = commands.DefaultBuff()

    def __init__(self):
        """Loads a user-defined routine on start up and initializes this Bot's main thread."""

        pygame.mixer.init()
        Bot.alert = pygame.mixer.music
        Bot.alert.load('./assets/alert.mp3')

        config.command_book = {
            'wait': commands.Wait,
            'walk': commands.Walk,
            'fall': commands.Fall,
            'move': commands.DefaultMove,
            'adjust': commands.DefaultAdjust,
            'buff': commands.DefaultBuff
        }
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

        with mss.mss() as sct:
            self.ready = True
            config.listening = True
            while True:
                if config.alert_active:
                    Bot._alert()
                if config.enabled and len(config.routine) > 0:
                    Bot.buff.main()

                    # Highlight the current Point
                    config.view_listbox.selection_clear(0, len(config.routine))
                    config.view_listbox.selection_set(Routine.index)
                    config.view_listbox.activate(Routine.index)

                    # Execute next Point in the routine
                    element = config.routine[Routine.index]
                    element.execute()
                    if config.rune_active and isinstance(element, Point) \
                            and element.location == config.rune_closest_pos:      # TODO: rename rune index
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

        move = config.command_book.get('move')
        move(*config.rune_pos).execute()
        adjust = config.command_book.get('adjust')
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
        """
        Increments config.seq_index and wraps back to 0 at the end of config.sequence.
        :return:    None
        """

        Routine.index = (Routine.index + 1) % len(config.routine)

    @staticmethod
    def load_commands(file):
        """
        Prompts the user to select a command module to import. Updates config's command book.
        :return:    None
        """

        utils.print_separator()
        print(f"[~] Loading command book '{basename(file)}':")

        ext = splitext(file)[1]
        if ext != '.py':
            print(f" !  '{ext}' is not a supported file extension.")
            return

        # Generate a command book using the selected module
        module_name = splitext(basename(file))[0]
        module = __import__(f'command_books.{module_name}', fromlist=[''])
        new_cb = {
            'wait': commands.Wait,
            'walk': commands.Walk,
            'fall': commands.Fall
        }
        for name, command in inspect.getmembers(module, inspect.isclass):
            name = name.lower()
            new_cb[name] = command

        # Check if required commands have been implemented
        success = True
        for command in ['move', 'adjust', 'buff']:      # TODO: change move to step
            if command not in new_cb:
                success = False
                print(f" !  Error: Must implement '{command}' command.")

        if success:
            config.command_book = new_cb
            config.curr_cb.set(basename(file))
            Bot.buff = new_cb['buff']()

            # Clear the current routine and Layout because command book changed
            config.routine.set([])
            config.curr_routine.set('')
            config.layout = None

            print(f"[~] Successfully loaded command book '{module_name}'.")
        else:
            print(f"[!] Command book '{module_name}' was not loaded.")
        return success

    @staticmethod
    def toggle_enabled():
        """
        Resumes or pauses the current routine. Plays a sound and prints a message to notify
        the user.
        :return:    None
        """

        config.rune_active = False
        config.alert_active = False
        config.calibrated = False
        while not config.calibrated:
            time.sleep(0.01)

        config.enabled = not config.enabled
        utils.print_state()
