"""A keyboard listener to track user inputs."""

import config
import time
import utils
import threading
import winsound
import pickle
import keyboard as kb
from os.path import isfile
from bot import Bot


class Listener:
    TARGET = '.settings'
    key_bindings = {
        'Start/stop': 'insert',
        'Reload routine': 'F6',
        'Record location': 'F7'
    }

    def __init__(self):
        """Initializes this Listener object's main thread."""

        config.listener = self

        self.load_keybindings()

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts listening to user inputs.
        :return:    None
        """

        print('\n[~] Started keyboard listener.')
        self.thread.start()

    def _main(self):
        """
        Constantly listens for user inputs and updates variables in config accordingly.
        :return:    None
        """

        self.ready = True
        while True:
            if config.listening:
                if kb.is_pressed('insert'):
                    Bot.toggle_enabled()
                    if config.enabled:
                        winsound.Beep(784, 333)     # G5
                    else:
                        winsound.Beep(523, 333)     # C5
                    time.sleep(0.267)
                elif kb.is_pressed('F6'):
                    config.calibrated = False
                    while not config.calibrated:
                        time.sleep(0.01)

                    config.routine.load(config.routine.path)

                    winsound.Beep(523, 200)     # C5
                    winsound.Beep(659, 200)     # E5
                    winsound.Beep(784, 200)     # G5
                elif kb.is_pressed('F7'):
                    pass            # TODO: update listener
                    # Bot.load_commands()
                    # Bot.load_routine()
                elif kb.is_pressed('F8'):
                    displayed_pos = tuple('{:.3f}'.format(round(i, 3)) for i in config.player_pos)
                    utils.print_separator()
                    print(f'Current position: ({displayed_pos[0]}, {displayed_pos[1]})')
                    time.sleep(1)
            time.sleep(0.01)

    def load_keybindings(self):
        if isfile(Listener.TARGET):
            with open(Listener.TARGET, 'rb') as file:
                self.key_bindings = pickle.load(file)
        else:
            self.save_keybindings()

    def save_keybindings(self):
        with open(Listener.TARGET, 'wb') as file:
            pickle.dump(self.key_bindings, file)
