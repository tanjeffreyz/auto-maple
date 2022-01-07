"""User friendly GUI to interact with Auto Maple."""

import config
import tkinter as tk
from tkinter import ttk
import settings
from gui_components import Menu, View, Edit


class GUI:
    def __init__(self):
        config.gui = self

        self.root = tk.Tk()
        self.root.title('Auto Maple')
        self.root.geometry('800x700')

        # Initialize GUI variables
        self.routine_var = tk.StringVar()

        # Build the GUI
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        self.navigation = ttk.Notebook(self.root)

        self.view = View(self.navigation)
        self.edit = Edit(self.navigation)

        self.navigation.pack(expand=True, fill='both')

    def set_routine(self, arr):
        self.routine_var.set(arr)

    def start(self):
        """Starts the GUI as well as any scheduled functions."""

        self.view.minimap.display_minimap()
        self._save_layout()
        self.root.mainloop()

    def _save_layout(self):
        """Periodically saves the current Layout object."""

        if config.layout is not None and settings.record_layout:
            config.layout.save()
        self.root.after(5000, self._save_layout)


if __name__ == '__main__':
    gui = GUI()
    gui.start()
