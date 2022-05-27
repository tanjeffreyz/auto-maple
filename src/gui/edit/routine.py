import tkinter as tk
from src.gui.edit.commands import Commands
from src.gui.edit.components import Components
from src.gui.edit.controls import Controls
from src.gui.interfaces import LabelFrame, Frame


class Routine(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Routine', **kwargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.list_frame = Frame(self)
        self.list_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.list_frame.rowconfigure(0, weight=1)

        self.components = Components(self.list_frame)
        self.components.grid(row=0, column=0, sticky=tk.NSEW)

        self.commands_var = tk.StringVar()

        self.commands = Commands(self.list_frame)
        self.commands.grid(row=0, column=1, sticky=tk.NSEW)

        self.controls = Controls(self)
        self.controls.grid(row=1, column=0)
