"""A menu for loading routines and command books."""

import tkinter as tk


class Menu(tk.Menu):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.file = tk.Menu(self, tearoff=0)
        self.file.add_command(label='New Routine')
        self.file.add_separator()
        self.file.add_command(label='Load Routine')
        self.file.add_command(label='Load Command Book')

        self.add_cascade(label='File', menu=self.file)


