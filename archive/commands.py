from vkeys import key_down, key_up
import threading, time
from capture import player_pos

#################################
#        State Variables        #
#################################
# ready = True
tengu_on = True


#################################
#       In-Game Commands        #
#################################
def _tengu():
    while True:
        if tengu_on:
            key_down('q')
            time.sleep(0.2)
            key_up('q')
            time.sleep(1.4)
        # print(player_pos)
tengu = threading.Thread(target=_tengu)         # Tengu thread continuously uses Tengu Strike unless tengu_on is set to False
tengu.daemon = True     # Daemon threads end when the main thread ends

def teleport(direction):
    # global tengu_on
    # tengu_on = False
    assert direction in ['left', 'up', 'right', 'down'], f"'{direction}' is not a recognized direction."
    key_down(direction)
    time.sleep(0.05)
    for _ in range(4):      # Press the teleport key twice to ensure it registers in-game
        key_down('e')
        time.sleep(0.075)
        key_up('e')
        time.sleep(0.01)
    key_up(direction)
    time.sleep(0.125)
    # tengu_on = True
    # ready = True
# teleport = threading.Thread(target=_teleport, args=('left',))
# teleport.daemon = True

def shikigami(direction, n=1):
    # global tengu_on
    # tengu_on = False
    assert direction in ['left', 'right'], 'Shikigami Haunting can only be used in the left and right directions.'
    key_down(direction)
    time.sleep(0.05)
    # key_down('r')
    # time.sleep(1.5)
    # key_up('r')
    for _ in range(n):
        # print(i)
        for _ in range(6):
            key_down('r')
            time.sleep(0.1)
        time.sleep(0.075)
    key_up(direction)
    time.sleep(0.1)
    # tengu_on = True