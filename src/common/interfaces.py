import os
import pickle

SETTINGS_DIR = '.settings'


class Configurable:
    TARGET = 'default_configurable'
    DEFAULT_CONFIG = {
        'Default configuration': 'None'
    }

    def __init__(self, target):
        self.TARGET = target
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()

    def load_config(self):
        path = os.path.join(SETTINGS_DIR, self.TARGET)
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                self.config = pickle.load(file)
        else:
            self.save_config()

    def save_config(self):
        path = os.path.join(SETTINGS_DIR, self.TARGET)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, 'wb') as file:
            pickle.dump(self.config, file)
