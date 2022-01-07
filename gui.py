"""User friendly GUI to interact with Auto Maple."""

import config
import tkinter as tk
from tkinter import ttk
import settings
from gui_components import Menu, View, Edit


class GUI:
    RESOLUTIONS = {
        'DEFAULT': '700x700',
        'View': '700x700',
        'Edit': '1200x700'
    }

    def __init__(self):
        config.gui = self

        self.root = tk.Tk()
        self.root.title('Auto Maple')
        self.root.geometry(GUI.RESOLUTIONS['DEFAULT'])

        # Initialize GUI variables
        self.routine_var = tk.StringVar()

        # Build the GUI
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        self.navigation = ttk.Notebook(self.root)

        self.view = View(self.navigation)
        self.edit = Edit(self.navigation)

        self.navigation.pack(expand=True, fill='both')
        self.navigation.bind('<<NotebookTabChanged>>', self._resize_window)

    def set_routine(self, arr):
        self.routine_var.set(arr)

    def _resize_window(self, e):
        """Callback to resize entire Tkinter window every time a new Page is selected."""

        nav = e.widget
        page = nav.tab(nav.select(), 'text')
        if self.root.state() != 'zoomed' and page in GUI.RESOLUTIONS:
            self.root.geometry(GUI.RESOLUTIONS[page])

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
