import tkinter as tk
from src.common import config
from src.gui.interfaces import LabelFrame


class Status(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Status', **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.cb_label = tk.Label(self, text='Command Book:')
        self.cb_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
        self.cb_entry = tk.Entry(self, textvariable=config.gui.view.status.curr_cb, state=tk.DISABLED)
        self.cb_entry.grid(row=0, column=2, padx=(0, 5), pady=5, sticky=tk.EW)
