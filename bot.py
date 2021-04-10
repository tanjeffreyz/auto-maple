"""An interpreter that reads and executes user-created routines."""

import config
import threading
import winsound
import time
import csv
import mss
import utils
from os import listdir
from os.path import isfile, join
from commands import Command, command_book


class Point:
    def __init__(self, x, y, counter=0, frequency=1, attacks=0):
        utils.validate_nonzero(frequency)
        self.location = (float(x), float(y))
        self.counter = int(counter)
        self.frequency = int(frequency)
        self.attacks = int(attacks)
        self.commands = []

    def execute(self):
        """
        Executes the set of actions associated with this Point.
        :return:    None
        """

        if self.counter == 0:
            if config.enabled:
                print(f'Point at {self.location}' + (':' if self.commands else ''))
                move = command_book.get('move')
                move(str(self.location)).execute()

    def __str__(self):
        """
        Returns a string representation of this Point object.
        :return:    This Point's string representation.
        """

        result = f'Point at {self.location}' + (':' if self.commands else '')
        for command in self.commands:
            result = result + '\n' + str(command)
        return result


class Bot:
    def __init__(self):
        Bot.load()
        self.thread = threading.Thread(target=Bot._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts this Bot object's thread.
        :return:    None
        """

        self.thread.start()

    @staticmethod
    def _main():
        """
        The main body of Bot that executes the user's routine.
        :return:    None
        """

        with mss.mss() as sct:
            while True:
                if config.elite_active:
                    config.enabled = False
                    # TODO: take care of elite here
                    config.elite_active = False
                if config.enabled:
                    pass
                else:
                    time.sleep(0.1)
                    # TODO: run bot here

    @staticmethod
    def load(file=None):
        """
        Attempts to load FILE into a sequence of Points. Prompts user input if no file is given.
        :param file:    The file's path.
        :return:        None
        """

        routines_dir = './routines'
        if not file:
            file = Bot._select_file(routines_dir)
        if file:
            utils.print_separator()
            print(f"Loading routine '{file}'...")
            config.sequence = []
            with open(join(routines_dir, file), newline='') as f:
                csv_reader = csv.reader(f)
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
            config.prev_routine = file
            print(f"Finished loading routine '{file}'.")
            winsound.Beep(523, 200)
            winsound.Beep(659, 200)
            winsound.Beep(784, 200)

    @staticmethod
    def _eval(expr, n):
        """
        Evaluates the given expression EXPR in the context of Auto Kanna.
        :param expr:    A list of strings to evaluate.
        :param n:       The line number of EXPR in the routine file.
        :return:        An object that represents EXPR.
        """

        if expr and isinstance(expr, list):
            first, rest = expr[0], expr[1:]
            rest = list(map(str.strip, rest))
            line = f'Line {n}: '

            if first == '@':        # Check for labels
                if len(rest) != 1:
                    print(line + f'Incorrect number of arguments for a label.')
                else:
                    return rest[0]
            elif first == '*':      # Check for Points
                try:
                    return Point(*rest)
                except ValueError:
                    print(line + f'Invalid arguments for a Point: {rest}')
                except TypeError:
                    print(line + f'Incorrect number of arguments for a Point.')
            else:                   # Otherwise might be a Command
                if first not in command_book.keys():
                    print(line + f"Command '{first}' does not exist.")
                else:
                    try:
                        return command_book.get(first)(*rest)
                    except ValueError:
                        print(line + f"Invalid arguments for command '{first}': {rest}")
                    except TypeError:
                        print(line + f"Incorrect number of arguments for command '{first}'.")

    @staticmethod
    def _select_file(directory):
        """
        Prompts the user to select a file from the .csv files within DIRECTORY.
        :param directory:   The directory in which to search.
        :return:            The path of the selected file.
        """

        index = float('inf')
        csv_files = [f for f in listdir(directory) if isfile(join(directory, f)) and '.csv' in f]
        num_files = len(csv_files)
        if not csv_files:
            print(f"Unable to find any routines in '{directory}'.")
        else:
            utils.print_separator()
            print('~~~ Loading Routine ~~~')
            print('Please select from the following routines:\n')
            for i in range(num_files):
                print(f'{i:02} -- {csv_files[i]}')
            print()
            while index not in range(num_files):
                try:
                    selection = input('>>> ')
                except KeyboardInterrupt:
                    exit()

                if not utils.validate_type(selection, int):
                    print('Selection must be an integer.')
                else:
                    index = int(selection)
                    if index not in range(num_files):
                        print('Invalid selection. Please enter an integer between ' +
                              f'0 and {max(0, num_files - 1)}.')
            return csv_files[index]

    @staticmethod
    def toggle_enabled():
        """
        Resumes or pauses the current routine. Plays a sound and prints a message to notify
        the user.
        :return:    None
        """

        config.rune_active = False
        config.elite_active = False
        utils.print_separator()
        print(f"Toggled: {'OFF' if config.enabled else 'ON'}")
        config.enabled = not config.enabled
        if config.enabled:
            winsound.Beep(784, 333)     # G5
        else:
            winsound.Beep(523, 333)     # C5
