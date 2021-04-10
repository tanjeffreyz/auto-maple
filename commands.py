"""A collection of all commands used to interact with the game."""

import config
import time
import utils
from vkeys import press, key_down, key_up


class Command:
    name = 'Command Superclass'

    @utils.run_if_enabled
    def execute(self):
        """
        Prints this Command's string representation and executes its main function.
        :return:    None
        """

        print(self)
        self.main()

    def main(self):
        pass

    def __str__(self):
        """
        Returns a string representing this Command instance.
        :return:    This Command's string representation.
        """

        variables = self.__dict__
        result = '    ' + self.name + (':' if variables else '')
        for key, value in variables.items():
            if key != 'name':
                result += f'\n        {key}={value}'
        return result


class Teleport(Command):
    def __init__(self, direction, jump='False'):
        utils.validate_arrows(direction)
        self.name = 'Teleport'
        self.direction = direction
        self.jump = utils.validate_boolean(jump)

    def main(self):
        pass        # TODO: finish this


class Move(Command):
    def __init__(self, position, max_steps='15'):
        utils.validate_nonzero(max_steps)
        self.position = utils.validate_position(position)

    def main(self):
        pass        # TODO finish this


class Goto(Command):
    def __init__(self, label):
        self.name = 'Goto'
        self.label = label

    def main(self):
        try:
            config.seq_index = config.sequence.index(self.label)
        except ValueError:
            print(f"Label '{self.label}' does not exist.")


class Shikigami(Command):
    def __init__(self, direction, num_attacks=2, repetitions=1):
        utils.validate_horizontal(direction)
        self.name = 'Shikigami'
        self.direction = direction
        self.num_attacks = int(num_attacks)
        self.repetitions = int(repetitions)

    def main(self):
        key_down(self.direction)
        for _ in range(self.repetitions):
            press('r', self.num_attacks, up_time=0.05)
        key_up(self.direction)
        time.sleep(0.1)


command_book = {'teleport': Teleport,
                'move': Move,
                'goto': Goto,
                'shikigami': Shikigami}
