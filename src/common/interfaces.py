import os
import pickle


class Configurable:
    TARGET = 'default_configurable'
    DIRECTORY = '.settings'
    DEFAULT_CONFIG = {
        'Default configuration': 'None'
    }

    def __init__(self, target, directory='.settings'):
        assert self.DEFAULT_CONFIG != Configurable.DEFAULT_CONFIG, 'Must override Configurable.DEFAULT_CONFIG'
        self.TARGET = target
        self.DIRECTORY = directory
        self.config = self.DEFAULT_CONFIG.copy()        # Shallow copy, should only contain primitives
        self.load_config()

    def load_config(self):
        path = os.path.join(self.DIRECTORY, self.TARGET)
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                loaded = pickle.load(file)
                self.config = {key: loaded.get(key, '') for key in self.DEFAULT_CONFIG}
        else:
            self.save_config()

    def save_config(self):
        path = os.path.join(self.DIRECTORY, self.TARGET)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, 'wb') as file:
            pickle.dump(self.config, file)
