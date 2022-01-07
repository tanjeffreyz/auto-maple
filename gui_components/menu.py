"""A menu for loading routines and command books."""

import config
import utils
import csv
import queue
import winsound
import tkinter as tk
from os.path import splitext, basename
from tkinter.filedialog import askopenfilename, asksaveasfilename
from bot import Bot
from routine import Routine, Command
from layout import Layout


class Menu(tk.Menu):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.file = tk.Menu(self, tearoff=0)
        self.queue = queue.Queue()

        self.file.add_command(label='New Routine')
        self.file.add_command(label='Save Routine', command=utils.async_callback(self, Menu._save_routine))
        self.file.add_separator()

        self.file.add_command(label='Load Command Book', command=utils.async_callback(self, Menu._load_commands))
        self.file.add_command(label='Load Routine', command=utils.async_callback(self, Menu._load_routine))       # TODO: move load funcs to here!

        self.add_cascade(label='File', menu=self.file)

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot save routines while Auto Maple is enabled.')
    def _save_routine():
        file_path = asksaveasfilename(initialdir='./routines/',
                                      title='Save routine',
                                      filetypes=[('*.csv', '*.csv')],
                                      defaultextension='*.csv')
        if file_path:
            config.routine.save(file_path)

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot load routines while Auto Maple is enabled.')
    def _load_routine():
        file_path = askopenfilename(initialdir='./routines/',
                                    title='Select a routine',
                                    filetypes=[('*.csv', '*.csv')])
        if file_path:
            config.routine.load(file_path)

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot load command books while Auto Maple is enabled.')
    def _load_commands():
        file_path = askopenfilename(initialdir='./command_books/',
                                    title='Select a command book',
                                    filetypes=[('*.py', '*.py')])
        if file_path:
            Bot.load_commands(file_path)





