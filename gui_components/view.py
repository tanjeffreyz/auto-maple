"""Displays the current minimap as well as various information regarding the current routine."""

import tkinter as tk
from gui_components.interfaces import LabelFrame, Tab


class View(Tab):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'View', **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.minimap = Minimap(self)
        self.minimap.grid(row=0, column=2)

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
        self.button.grid(row=2, column=1)


class Minimap(LabelFrame):
    def __init__(self, parent, **kwargs):
        kwargs['text'] = 'Minimap'
        super().__init__(parent, **kwargs)

        self.canvas = tk.Canvas(self, width=400, height=200)
        self.canvas.pack()

