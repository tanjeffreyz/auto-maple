"""A list of user-defined settings that can be changed by routines."""

import utils

# A dictionary that maps each setting to its validator function
SETTING_VALIDATORS = {
    'move_tolerance': float,
    'adjust_tolerance': float,
    'record_layout': utils.validate_boolean,
    'buff_cooldown': utils.validate_nonnegative_int
}

# The allowed error from the destination when moving towards a Point
move_tolerance = 0.1

# The allowed error from a specific location while adjusting to that location
adjust_tolerance = 0.01

# Whether the bot should save new player positions to the current layout
record_layout = False

# The amount of time (in seconds) to wait between each call to the 'buff' command
buff_cooldown = 180
