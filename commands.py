"""A collection of Commands shared across all command books."""

import config
import settings
import utils
import time
from routine import Command
from vkeys import key_down, key_up, press


#############################
#       Shared Commands     #
#############################
class Wait(Command):
    """Waits for a set amount of time."""

    def __init__(self, duration):
        super().__init__(locals())
        self.duration = float(duration)

    def main(self):
        time.sleep(self.duration)


class Walk(Command):
    """Walks in the given direction for a set amount of time."""

    def __init__(self, direction, duration):
        super().__init__(locals())
        self.direction = utils.validate_horizontal_arrows(direction)
        self.duration = float(duration)

    def main(self):
        key_down(self.direction)
        time.sleep(self.duration)
        key_up(self.direction)
        time.sleep(0.05)


class Fall(Command):
    """
    Performs a down-jump and then free-falls until the player exceeds a given distance
    from their starting position.
    """

    def __init__(self, distance=settings.move_tolerance / 2):
        super().__init__(locals())
        self.distance = float(distance)

    def main(self):
        start = config.player_pos
        key_down('down')
        time.sleep(0.05)
        counter = 6
        while config.enabled and \
                counter > 0 and \
                utils.distance(start, config.player_pos) < self.distance:
            press('space', 1, down_time=0.1)
            counter -= 1
        key_up('down')
        time.sleep(0.1)


#################################
#       Default Commands        #
#################################
class DefaultMove(Command):
    """Undefined 'move' command for the default command book."""

    def __init__(self, *args, **kwargs):
        super().__init__(locals())

    def main(self):
        print("\n[!] 'Move' command not implemented in current command book, aborting process.")
        config.enabled = False


class DefaultAdjust(Command):
    """Undefined 'adjust' command for the default command book."""

    def __init__(self, *args, **kwargs):
        super().__init__(locals())

    def main(self):
        print("\n[!] 'Adjust' command not implemented in current command book, aborting process.")
        config.enabled = False


class DefaultBuff(Command):
    """Undefined 'buff' command for the default command book."""

    def main(self):
        print("\n[!] 'Buff' command not implemented in current command book, aborting process.")
        config.enabled = False
