import tkinter as tk
from src.gui.interfaces import LabelFrame, Frame
from src.common.interfaces import Configurable


class Pets(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Pets', **kwargs)

        self.pet_settings = PetSettings('pets')
        self.auto_feed = tk.BooleanVar(value=self.pet_settings.get('Auto-feed'))
        self.num_pets = tk.IntVar(value=self.pet_settings.get('Num pets'))

        feed_row = Frame(self)
        feed_row.pack(side=tk.TOP, fill='x', expand=True, pady=5, padx=5)
        check = tk.Checkbutton(
            feed_row,
            variable=self.auto_feed,
            text='Auto-feed',
            command=self._on_change
        )
        check.pack()

        num_row = Frame(self)
        num_row.pack(side=tk.TOP, fill='x', expand=True, pady=(0, 5), padx=5)
        label = tk.Label(num_row, text='Number of pets to feed:')
        label.pack(side=tk.LEFT, padx=(0, 15))
        radio_group = Frame(num_row)
        radio_group.pack(side=tk.LEFT)
        for i in range(1, 4):
            radio = tk.Radiobutton(
                radio_group,
                text=str(i),
                variable=self.num_pets,
                value=i,
                command=self._on_change
            )
            radio.pack(side=tk.LEFT, padx=(0, 10))

    def _on_change(self):
        self.pet_settings.set('Auto-feed', self.auto_feed.get())
        self.pet_settings.set('Num pets', self.num_pets.get())
        self.pet_settings.save_config()


class PetSettings(Configurable):
    DEFAULT_CONFIG = {
        'Auto-feed': False,
        'Num pets': 1
    }

    def get(self, key):
        return self.config[key]

    def set(self, key, value):
        assert key in self.config
        self.config[key] = value
