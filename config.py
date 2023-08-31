"""
Config file for specifying pins, modes, solutions, etc.

All pin numbers assume BCM, unless MODE is changed.

© 2023 Antithesise
"""

from RPIO import BCM, BOARD


# ---------------------------------------------------------------------------- #
#                             Application settings                             #
# ---------------------------------------------------------------------------- #

DEBUG = True # True or False
"Is the application in debugging mode?"

TIMEOUT = 600.0 # 600s = 10min
"The duration after which the user will automatically fail"

BLOCKAFTER = True # True or False
"Whether or not to wait for ^D before starting next attempt"

# ------------------------------- PWM settings ------------------------------- #

PWM0 = 12 # unassigned so far (piezo, buzzers, etc?)
PWM1 = 13

# ------------------------------ Servo settings ------------------------------ #

DOOR0PIN = 23
"The control pin of the first door servo"

DOOR1PIN = 24
"The control pin of the second door servo"

SERVODELAY = 100
"The time to wait to ensure a servo has moved in ms"

# ------------------------------ Input settings ------------------------------ #

COMBOPINS = (17, 27, 22, 10)
"The pins of the buttons (order sensitive)"

COMBOSEQ = [3, 0, 2, 1, 0, 0, 3, 3] # Change me!
"The correct sequence of buttons"

DISARMPIN = 9
"The pin of the disarm switch"

CTRLRODPIN = 11
"The pin of the control rod detector"

# ---------------------------------------------------------------------------- #
#                                Advanced config                               #
#                                                                              #
#                  ONLY TOUCH IF YOU KNOW WHAT YOU ARE DOING!                  #
# ---------------------------------------------------------------------------- #

MODE = BCM # BCM or BOARD
"Pin numbering mode"

DOOR0DEG = 180.0
"The range of the motion in deg"
DOOR0MIN = 1000
"The 0deg duty cycle in μs"
DOOR0MAX = 2000
"The max deg duty cycle in μs"

DOOR1DEG = 180.0
"The range of the motion in deg"
DOOR1MIN = 1000
"The 0deg duty cycle in μs"
DOOR1MAX = 2000
"The max deg duty cycle in μs"
