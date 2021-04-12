"""A collection of all commands used to interact with the game."""

import config
import time
import math
import utils
import sys
import inspect
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


class Move(Command):
    def __init__(self, x, y, max_steps=15):
        self.name = 'Move'
        self.target = (float(x), float(y))
        self.max_steps = utils.validate_nonzero_int(max_steps)

    def main(self):
        path = config.layout.shortest_path(config.player_pos, self.target)
        for point in path:
            self._step(point)

    @utils.run_if_enabled
    def _step(self, target):
        toggle = True
        error = utils.distance(config.player_pos, target)
        while config.enabled and self.max_steps > 0 and error > config.move_tolerance:
            if toggle:
                d_x = abs(target[0] - config.player_pos[0])
                if d_x > config.move_tolerance / math.sqrt(2):
                    jump = str(utils.bernoulli(0.1))
                    if config.player_pos[0] > target[0]:
                        Teleport('left', jump=jump).main()
                    else:
                        Teleport('right', jump=jump).main()
                    self.max_steps -= 1
            else:
                d_y = abs(target[1] - config.player_pos[1])
                if d_y > config.move_tolerance / math.sqrt(2):
                    jump = str(d_y > 1.5 * config.move_tolerance * config.mm_ratio)
                    if config.player_pos[1] > target[1]:
                        Teleport('up', jump=jump).main()
                    else:
                        Teleport('down', jump=jump).main()
                    self.max_steps -= 1

            error = utils.distance(config.player_pos, target)
            toggle = not toggle


class Goto(Command):
    def __init__(self, label):
        self.name = 'Goto'
        self.label = label

    def main(self):
        try:
            config.seq_index = config.sequence.index(self.label)
        except ValueError:
            print(f"Label '{self.label}' does not exist.")


class Wait(Command):
    def __init__(self, duration):
        self.name = 'Wait'
        self.duration = duration

    def main(self):
        time.sleep(self.duration)


class Teleport(Command):
    def __init__(self, direction, jump='False'):
        self.name = 'Teleport'
        self.direction = utils.validate_arrows(direction)
        self.jump = utils.validate_boolean(jump)

    def main(self):
        num_presses = 3
        time.sleep(0.05)
        if self.direction != 'up':
            key_down(self.direction)
            time.sleep(0.05)
        if self.jump:
            if self.direction == 'down':
                press('space', 3, down_time=0.1)
                num_presses = 2
            else:
                press('space', 2)
        if self.direction == 'up':
            key_down(self.direction)
            time.sleep(0.05)
        press('e', num_presses)
        key_up(self.direction)
        if num_presses < 3:
            time.sleep(0.1)


class Shikigami(Command):
    def __init__(self, direction, num_attacks=2, repetitions=1):
        self.name = 'Shikigami'
        self.direction = utils.validate_horizontal_arrows(direction)
        self.num_attacks = int(num_attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(0.05)
        key_down(self.direction)
        time.sleep(0.05)
        for _ in range(self.repetitions):
            press('r', self.num_attacks, up_time=0.05)
        key_up(self.direction)
        time.sleep(0.25)


class Tengu(Command):
    def __init__(self):
        self.name = 'Tengu'

    def main(self):
        press('q', 1, up_time=0.15)


class Kishin(Command):
    def __init__(self):
        self.name = 'Kishin'

    def main(self):
        press('lshift', 4, down_time=0.1, up_time=0.15)


class Yaksha(Command):
    def __init__(self, direction=None):
        self.name = 'Yaksha'
        if direction is None:
            self.direction = direction
        else:
            self.direction = utils.validate_horizontal_arrows(direction)

    def main(self):
        if self.direction:
            press(self.direction, 1, down_time=0.1)
        else:
            if config.player_pos[0] > 0.5:
                press('left', 1, down_time=0.1)
            else:
                press('right', 1, down_time=0.1)
        press('2', 3)


# Generate the command book to be used in other modules
command_book = {}
for name, command in inspect.getmembers(sys.modules[__name__]):
    name = name.lower()
    if inspect.isclass(command) and name != 'command':
        command_book[name] = command
