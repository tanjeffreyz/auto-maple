"""User friendly GUI to interact with Auto Maple."""

import config
import cv2
import tkinter as tk
from tkinter import ttk
from gui_components import Main, Edit
from PIL import Image, ImageTk


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Auto Maple')
        self.root.geometry('700x400')

        self.navigation = ttk.Notebook(self.root)

        self.main = Main(self.navigation)
        self.edit = Edit(self.navigation)

        self.navigation.pack(expand=1, fill='both')

    def start(self):
        """Starts the GUI as well as any scheduled functions."""

        self._display_minimap()
        self._save_layout()
        self.root.mainloop()

    def _display_minimap(self):
        """Updates the Main page with the current minimap."""

        if config.minimap is not None:
            img = cv2.cvtColor(config.minimap, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(img))
            self.main.canvas.create_image(0, 0, image=img, anchor=tk.NW)
            self.main.img = img
        self.root.after(10, self._display_minimap)

    def _save_layout(self):
        """Periodically saves the current Layout object."""

        if config.layout is not None:
            config.layout.save()
        self.root.after(5000, self._save_layout)


if __name__ == '__main__':
    gui = GUI()
    gui.start()
