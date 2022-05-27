"""A collection of all commands that a Blaster can use to interact with the game."""

import time
from src.common import settings
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up

#
# class Move(Command):
#     """Moves to a given position using the shortest path based on the current Layout."""
#
#     def __init__(self, x, y, max_steps=15):
#         super().__init__(locals())
#         self.target = (float(x), float(y))
#         self.max_steps = settings.validate_nonnegative_int(max_steps)
#
#     def main(self):
#         counter = self.max_steps
#         path = config.layout.shortest_path(config.player_pos, self.target)
#         # config.path = path.copy()
#         # config.path.insert(0, config.player_pos)
#         for point in path:
#             counter = self._step(point, counter)
#
#     @utils.run_if_enabled
#     def _step(self, target, counter):
#         toggle = True
#         local_error = utils.distance(config.player_pos, target)
#         global_error = utils.distance(config.player_pos, self.target)
#         while config.enabled and \
#                 counter > 0 and \
#                 local_error > settings.move_tolerance and \
#                 global_error > settings.move_tolerance:
#             if toggle:
#                 d_x = target[0] - config.player_pos[0]
#                 if abs(d_x) > settings.move_tolerance / math.sqrt(2):
#                     if d_x < 0:
#                         Jump('left').main()
#                     else:
#                         Jump('right').main()
#                     counter -= 1
#             else:
#                 d_y = target[1] - config.player_pos[1]
#                 if abs(d_y) > settings.move_tolerance / math.sqrt(2):
#                     if d_y < 0:
#                         Jump('up').main()
#                     else:
#                         Jump('down').main()
#                     counter -= 1
#             local_error = utils.distance(config.player_pos, target)
#             global_error = utils.distance(config.player_pos, self.target)
#             toggle = not toggle
#         return counter
#
#
# class Adjust(Command):
#     """Fine-tunes player position using small movements."""
#
#     def __init__(self, x, y, max_steps=5):
#         super().__init__(locals())
#         self.target = (float(x), float(y))
#         self.max_steps = settings.validate_nonnegative_int(max_steps)
#
#     def main(self):
#         counter = self.max_steps
#         toggle = True
#         error = utils.distance(config.player_pos, self.target)
#         while config.enabled and counter > 0 and error > settings.adjust_tolerance:
#             if toggle:
#                 d_x = self.target[0] - config.player_pos[0]
#                 threshold = settings.adjust_tolerance / math.sqrt(2)
#                 if abs(d_x) > threshold:
#                     walk_counter = 0
#                     if d_x < 0:
#                         key_down('left')
#                         while config.enabled and d_x < -1 * threshold and walk_counter < 60:
#                             time.sleep(0.05)
#                             walk_counter += 1
#                             d_x = self.target[0] - config.player_pos[0]
#                         key_up('left')
#                     else:
#                         key_down('right')
#                         while config.enabled and d_x > threshold and walk_counter < 60:
#                             time.sleep(0.05)
#                             walk_counter += 1
#                             d_x = self.target[0] - config.player_pos[0]
#                         key_up('right')
#                     counter -= 1
#             else:
#                 d_y = self.target[1] - config.player_pos[1]
#                 if abs(d_y) > settings.adjust_tolerance / math.sqrt(2):
#                     if d_y < 0:
#                         Jump('up').main()
#                     else:
#                         key_down('down')
#                         time.sleep(0.05)
#                         press('space', 3, down_time=0.1)
#                         key_up('down')
#                         time.sleep(0.05)
#                     counter -= 1
#             error = utils.distance(config.player_pos, self.target)
#             toggle = not toggle
#
#
# def step(direction, target):
#     print('blaster step test')


class Buff(Command):
    """Uses each of Blaster's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.booster_time = 0
        self.warrior_time = 0

    def main(self):
        now = time.time()
        if self.booster_time == 0 or now - self.booster_time > 190:
            press('f1', 2)
            self.booster_time = now
        if self.warrior_time == 0 or now - self.warrior_time > 890:
            press('f2', 2)
            self.warrior_time = now


class Jump(Command):
    """Performs a flash jump or 'Detonate' in the given direction."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        key_down(self.direction)
        time.sleep(0.1)
        press('space', 1)
        if self.direction == 'up':
            press('d', 1)
        else:
            press('space', 1)
        key_up(self.direction)
        time.sleep(0.5)


class MagnumPunch(Command):
    """Performs a 'No-Reload Magnum Punch' combo once."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        key_down(self.direction)
        time.sleep(0.05)
        key_down('q')
        time.sleep(0.1)
        for _ in range(3):
            key_down('r')
            time.sleep(0.05)
            key_down('e')
            time.sleep(0.05)
            key_up('r')
            key_up('e')
            time.sleep(0.05)
        key_up('q')
        time.sleep(0.025)
        press('space', 1)
        key_up(self.direction)
        time.sleep(0.05)
