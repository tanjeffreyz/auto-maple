"""User friendly GUI to interact with Auto Maple."""

import config
import cv2
import tkinter as tk
from tkinter import ttk
from gui_components import Menu, View, Edit
from PIL import Image, ImageTk


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Auto Maple')
        self.root.geometry('700x400')

        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        self.navigation = ttk.Notebook(self.root)

        self.main = View(self.navigation)
        self.edit = Edit(self.navigation)

        self.navigation.pack(expand=True, fill='both')

    def start(self):
        """Starts the GUI as well as any scheduled functions."""

        self.main.minimap.display_minimap()
        self._save_layout()
        self.root.mainloop()

    def _save_layout(self):
        """Periodically saves the current Layout object."""

        if config.layout is not None:
            config.layout.save()
        self.root.after(5000, self._save_layout)


if __name__ == '__main__':
    gui = GUI()
    gui.start()
