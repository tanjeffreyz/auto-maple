"""A collection of variables shared across multiple modules."""

#################################
#           CONSTANTS           #
#################################
MONITOR = {'top': 0, 'left': 0, 'width': 1366, 'height': 768}


#################################
#       Global Variables        #
#################################
player_pos = (0, 0)
enabled = False
ready = False
calibrated = False
listening = True

mm_ratio = 1

rune_active = False
rune_pos = (0, 0)
rune_index = 0

elite_active = False

sequence = []
seq_index = 0

path = []

routine = None
layout = None


#################################
#       Routine Settings        #
#################################
move_tolerance = 0.075
adjust_tolerance = 0.01
use_haku = True
