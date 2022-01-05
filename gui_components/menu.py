"""A menu for loading routines and command books."""

import config
import utils
import csv
import queue
import winsound
import tkinter as tk
from tkinter.filedialog import askopenfilename
from bot import Bot, Point
from layout import Layout
from commands import Command


class Menu(tk.Menu):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.file = tk.Menu(self, tearoff=0)
        self.queue = queue.Queue()

        self.file.add_command(label='New Routine')
        self.file.add_separator()

        self.file.add_command(label='Load Routine', command=utils.async_callback(self, Menu._load_routine))       # TODO: move load funcs to here!
        self.file.add_command(label='Load Command Book', command=utils.async_callback(self, Bot.load_commands))

        self.add_cascade(label='File', menu=self.file)

    @staticmethod
    def _load_routine():
        file_name = askopenfilename()
        print(file_name)
        # routines_dir = './routines'
        # if not file:
        #     utils.print_separator()
        #     print('~~~ Import Routine ~~~')
        #     file = Bot._select_file(routines_dir, '.csv')
        # if file:
        # config.calibrated = False
        config.sequence = []
        config.seq_index = 0
        utils.reset_settings()
        utils.print_separator()
        print(f"Loading routine at '{file_name}'...")
        with open(file_name, newline='') as f:
            csv_reader = csv.reader(f, skipinitialspace=True)
            curr_point = None
            line = 1
            for row in csv_reader:
                result = Bot._eval(row, line)
                if result:
                    if isinstance(result, Command):
                        if curr_point:
                            curr_point.commands.append(result)
                    else:
                        config.sequence.append(result)
                        if isinstance(result, Point):
                            curr_point = result
                line += 1
        config.routine = file_name
        # config.layout = Layout.load(file)
        print(f"Finished loading routine '{file_name}'.")
        winsound.Beep(523, 200)     # C5
        winsound.Beep(659, 200)     # E5
        winsound.Beep(784, 200)     # G5



