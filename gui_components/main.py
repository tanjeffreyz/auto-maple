"""Displays the current minimap as well as various information regarding the current routine."""

import tkinter as tk
from gui_components.interfaces import Frame, Tab


class Main(Tab):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Main', **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.img = None
        self.canvas = tk.Canvas(self, width=400, height=200)
        self.canvas.grid(row=0, column=2)

        self.text_var = tk.StringVar()
        self.text_var.set('Initial String')
        self.label = tk.Label(self, textvariable=self.text_var)


        counter = 0


        def func():
            nonlocal counter
            self.text_var.set(str(counter))
            counter += 1

        self.button = tk.Button(self, text="test", command=func)

        self.label.grid(row=0, column=1)
        self.button.grid(row=1, column=1)
