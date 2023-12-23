"""A module for acting on dangerous in-game events."""
import threading
import time

from src.common import config
from src.common.interfaces import Configurable
from src.common.vkeys import press


class AutoPot(Configurable):

    DEFAULT_CONFIG = {
        'HP Pot': 'end',
        'MP Pot': 'page down'
    }

    def __init__(self):
        """Initializes this AutoPot object's main thread."""
        super().__init__('pots')
        config.auto_pot = self

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """Starts this AutoPot's thread."""

        print('\n[~] Started auto-pot')
        self.thread.start()

    def _main(self):
        self.ready = True
        while True:
            if config.enabled and config.auto_pot_enabled:
                # Use HP/MP pots if low
                #print(config.capture.hp_mp_info)

                while config.capture.hp_mp_info['hp_low']:
                    #print("HP low!")
                    press(self.config['HP Pot'], 1)
                while config.capture.hp_mp_info['mp_low']:
                    #print("MP low!")
                    press(self.config['MP Pot'], 1)

            time.sleep(0.2)
