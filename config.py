"""A collection of variables shared across multiple modules."""

#################################
#           CONSTANTS           #
#################################
# Represents the dimensions of the monitor to screenshot
MONITOR = {'top': 0, 'left': 0, 'width': 1366, 'height': 768}


#################################
#       Global Variables        #
#################################
# The player's position relative to the minimap
player_pos = (0, 0)

# Describes whether the bot is currently running or not
enabled = False

# Describes whether the bot has been successfully initialized
ready = False

# Describes whether the video capture has calibrated the minimap
calibrated = False

# Describes whether the keyboard listener is currently running
listening = True

# The ratio of the minimap's width divided by its height (used for conversions)
mm_ratio = 1

# Describes whether a rune has appeared in the game
rune_active = False

# The position of the rune relative to the minimap
rune_pos = (0, 0)

# The location of the Point object that is closest to the rune
rune_index = (0, 0)

# Describes whether an Elite Boss has been detected
elite_active = False

# Stores all the Points and labels in the current user-defined routine
sequence = []

# Represents the index that the bot is currently at
seq_index = 0

# Represents the current shortest path that the bot is taking
path = []

# Stores a map of all available commands that can be used by routines
command_book = {}

# Stores the name of the current routine file
routine = None

# Stores the Layout object associated with the current routine
layout = None


#################################
#       Routine Settings        #
#################################
move_tolerance = 0.075
adjust_tolerance = 0.01
buff_cooldown = 220
