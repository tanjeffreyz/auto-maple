"""Displays Auto Maple's current settings and allows the user to edit them."""
from gui_components.settings.keybindings import KeyBindings
import tkinter as tk
from gui_components.interfaces import Tab


class Settings(Tab):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Settings', **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

        self.keybindings = KeyBindings(self)
        self.keybindings.grid(row=0, column=1, sticky=tk.NSEW)


