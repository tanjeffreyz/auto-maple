"""A keyboard listener to track user inputs."""

import config
import time
import utils
import threading
import winsound
import pickle
import keyboard as kb
from os.path import isfile


class Listener:
    TARGET = '.keybinds'
    DEFAULT_KEYBINDS = {
        'Start/stop': 'insert',
        'Reload routine': 'f6',
        'Record location': 'f7'
    }

    def __init__(self):
        """Initializes this Listener object's main thread."""

        config.listener = self

        self.key_binds = Listener.DEFAULT_KEYBINDS.copy()
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
                if kb.is_pressed(self.key_binds['Start/stop']):
                    Listener.toggle_enabled()
                elif kb.is_pressed(self.key_binds['Reload routine']):
                    Listener.reload_routine()
                elif kb.is_pressed(self.key_binds['Record location']):      # TODO: add to recorded locations
                    displayed_pos = tuple('{:.3f}'.format(round(i, 3)) for i in config.player_pos)
                    utils.print_separator()
                    print(f'Current position: ({displayed_pos[0]}, {displayed_pos[1]})')
                    time.sleep(0.6)
            time.sleep(0.01)

    @staticmethod
    def toggle_enabled():
        """Resumes or pauses the current routine. Plays a sound to notify the user."""

        config.rune_active = False
        config.alert_active = False

        Listener.recalibrate_minimap()

        config.enabled = not config.enabled
        utils.print_state()

        if config.enabled:
            winsound.Beep(784, 333)     # G5
        else:
            winsound.Beep(523, 333)     # C5
        time.sleep(0.267)

    @staticmethod
    def reload_routine():
        Listener.recalibrate_minimap()

        config.routine.load(config.routine.path)

        winsound.Beep(523, 200)     # C5
        winsound.Beep(659, 200)     # E5
        winsound.Beep(784, 200)     # G5

    @staticmethod
    def recalibrate_minimap():
        config.calibrated = False
        while not config.calibrated:
            time.sleep(0.01)
        config.gui.edit.minimap.redraw()

    def load_keybindings(self):
        if isfile(Listener.TARGET):
            with open(Listener.TARGET, 'rb') as file:
                self.key_binds = pickle.load(file)
        else:
            self.save_keybindings()

    def save_keybindings(self):
        with open(Listener.TARGET, 'wb') as file:
            pickle.dump(self.key_binds, file)
