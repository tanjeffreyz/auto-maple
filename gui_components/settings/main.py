"""Displays Auto Maple's current settings and allows the user to edit them."""

import tkinter as tk
from gui_components.settings.keybindings import KeyBindings
from gui_components.interfaces import Tab
from src.common import config


class Settings(Tab):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Settings', **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, weight=1)

        self.controls = KeyBindings(self, 'Auto Maple Controls', config.listener)
        self.controls.grid(row=0, column=1, sticky=tk.N, padx=10, pady=10)

        self.key_bindings = KeyBindings(self, 'In-game Keybindings', config.bot)
        self.key_bindings.grid(row=0, column=2, sticky=tk.N, padx=10, pady=10)
