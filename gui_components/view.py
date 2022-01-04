"""Displays the current minimap as well as various information regarding the current routine."""

import config
import cv2
import tkinter as tk
from gui_components.interfaces import LabelFrame, Page
from PIL import Image, ImageTk


class View(Page):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'View', **kwargs)

        self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.minimap = Minimap(self)
        self.minimap.grid(row=0, column=2, sticky=tk.NSEW, padx=10, pady=10)

        self.details = Details(self)
        self.details.grid(row=1, column=2, sticky=tk.NSEW, padx=10, pady=10)

        self.routine = Routine(self)
        self.routine.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW, padx=10, pady=10)

        #
        # self.text_var = tk.StringVar()
        # self.text_var.set('Initial String')
        # self.label = tk.Label(self, textvariable=self.text_var)
        #
        #
        # counter = 0
        #
        #
        # def func():
        #     nonlocal counter
        #     self.text_var.set(str(counter))
        #     counter += 1
        #
        # self.button = tk.Button(self, text="test", command=func)
        #
        # self.label.grid(row=0, column=1)
        # self.button.grid(row=2, column=1)


class Minimap(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Minimap', **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill='both', padx=5, pady=5)

    def display_minimap(self):
        """Updates the Main page with the current minimap."""

        if config.minimap:
            img = cv2.cvtColor(config.minimap['minimap'], cv2.COLOR_BGR2RGB)
            height, width, _ = img.shape
            c_height, c_width = self.canvas.winfo_height(), self.canvas.winfo_width()

            ratio = min(c_width / width, c_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            if new_height * new_width > 0:
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

            img = ImageTk.PhotoImage(Image.fromarray(img))
            self.canvas.create_image(c_width // 2,
                                     c_height // 2,
                                     image=img, anchor=tk.CENTER)
            self._img = img                 # Prevent garbage collection
        self.after(10, self.display_minimap)


class Details(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Details', **kwargs)

        self.canvas = tk.Canvas(self)
        self.canvas.pack()


class Routine(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Routine', **kwargs)

        self.arr = list(range(100))
        self.test = tk.StringVar(value=self.arr)
        self.listbox = tk.Listbox(self, width=25, listvariable=self.test)
        self.listbox.pack(expand=True, fill='both', padx=5, pady=5)

