"""A collection of variables shared across multiple modules."""

#################################
#           CONSTANTS           #
#################################
# Describes the dimensions of the screen to capture with mss
MONITOR = {'top': 0, 'left': 0, 'width': 1366, 'height': 768}


#################################
#       Global Variables        #
#################################
# The player's position relative to the minimap
player_pos = (0, 0)

# Describes whether the bot is currently running or not
enabled = False

# Describes whether the video capture has calibrated the minimap
calibrated = False

# Describes whether the keyboard listener is currently running
listening = False

# Various display information regarding the current minimap frame
minimap = {}

# The ratio of the minimap's width divided by its height
minimap_ratio = 1

# A frame of the minimap sampled from the latest calibration procedure
minimap_sample = None

# Describes whether a rune has appeared in the game
rune_active = False

# The position of the rune relative to the minimap
rune_pos = (0, 0)

# The location of the Point object that is closest to the rune
rune_closest_pos = (0, 0)

# Indicates whether a danger has been detected (Elite Boss, room change, etc)
alert_active = False

# Represents the current shortest path that the bot is taking
path = []


#############################
#       Shared Modules      #
#############################
# A Routine object that manages the 'machine code' of the current routine
routine = None

# Stores the Layout object associated with the current routine
layout = None

# Shares the main bot loop
bot = None

# Shares the keyboard listener
listener = None

# Shares the gui to all modules
gui = None
