"""A menu for loading routines and command books."""

from src.common import config, utils
import queue
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno


class Menu(tk.Menu):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.file = tk.Menu(self, tearoff=0)
        self.queue = queue.Queue()

        self.file.add_command(label='New Routine', command=utils.async_callback(self, Menu._new_routine))
        self.file.add_command(label='Save Routine', command=utils.async_callback(self, Menu._save_routine))
        self.file.add_separator()

        self.file.add_command(label='Load Command Book', command=utils.async_callback(self, Menu._load_commands))
        self.file.add_command(label='Load Routine', command=utils.async_callback(self, Menu._load_routine))

        self.add_cascade(label='File', menu=self.file)

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot create a new routine while Auto Maple is enabled')
    def _new_routine():
        if config.routine.dirty:
            if not askyesno(title='New Routine',
                            message='The current routine has unsaved changes. '
                                    'Would you like to proceed anyways?',
                            icon='warning'):
                return

        config.routine.clear()

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot save routines while Auto Maple is enabled')
    def _save_routine():
        file_path = asksaveasfilename(initialdir='./routines/',
                                      title='Save routine',
                                      filetypes=[('*.csv', '*.csv')],
                                      defaultextension='*.csv')
        if file_path:
            config.routine.save(file_path)

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot load routines while Auto Maple is enabled')
    def _load_routine():
        if config.routine.dirty:
            if not askyesno(title='Load Routine',
                            message='The current routine has unsaved changes. '
                                    'Would you like to proceed anyways?',
                            icon='warning'):
                return

        file_path = askopenfilename(initialdir='./routines/',
                                    title='Select a routine',
                                    filetypes=[('*.csv', '*.csv')])
        if file_path:
            config.routine.load(file_path)

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot load command books while Auto Maple is enabled')
    def _load_commands():
        if config.routine.dirty:
            if not askyesno(title='Load Command Book',
                            message='Loading a new command book will discard the current routine, '
                                    'which has unsaved changes. Would you like to proceed anyways?',
                            icon='warning'):
                return

        file_path = askopenfilename(initialdir='./command_books/',
                                    title='Select a command book',
                                    filetypes=[('*.py', '*.py')])
        if file_path:
            config.bot.load_commands(file_path)
