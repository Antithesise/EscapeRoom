"""
Config file for specifying pins, modes, solutions, etc.

All pin numbers assume BCM, unless MODE is changed.

© 2023 Antithesise
"""

from RPIO import BCM, BOARD


# ---------------------------------------------------------------------------- #
#                             Application settings                             #
# ---------------------------------------------------------------------------- #

DEBUG = False

# ------------------------------- PWM settings ------------------------------- #

PWM0 = 12 # unassigned so far (piezo, buzzers, etc?)
PWM1 = 13

# ------------------------------ Servo settings ------------------------------ #

DOOR0PIN = 23
"The control pin of the first door servo"
DOOR1PIN = 24
"The control pin of the second door servo"

# --------------------------- Combination settings --------------------------- #

COMBOPINS = (17, 27, 22, 10)
"The pins of the buttons (order sensitive)"
COMBOSEQ = [3, 0, 2, 1, 0, 0, 3, 3]
"The correct sequence of buttons"


# ---------------------------------------------------------------------------- #
#                                Advanced config                               #
#                                                                              #
#                  ONLY TOUCH IF YOU KNOW WHAT YOU ARE DOING!                  #
# ---------------------------------------------------------------------------- #

MODE = BCM # BCM or BOARD
"Pin numbering mode"

DOOR0DEG = 180
"The range of the motion in deg"
DOOR0MIN = 1000
"The 0deg duty cycle in μs"
DOOR0MAX = 2000
"The max deg duty cycle in μs"

DOOR1DEG = 180
"The range of the motion in deg"
DOOR1MIN = 1000
"The 0deg duty cycle in μs"
DOOR1MAX = 2000
"The max deg duty cycle in μs"
