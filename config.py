"""
Config file for specifying pins, modes, solutions, etc.

All pin numbers assume BCM, unless MODE is changed.
"""

from RPIO import BCM, BOARD

from typing import NamedTuple

# ---------------------------------------------------------------------------- #
#                               Classes and util                               #
#                                                                              #
#                                DO NOT MODIFY!                                #
# ---------------------------------------------------------------------------- #

class ServoType(NamedTuple):
    """
    An internal class representing a servo motor.
    """

    pin: int
    "The control pin number"
    mindc: int = 1000
    "The 0deg duty cycle in μs"
    maxdc: int = 2000
    "The 180deg duty cycle in μs"

class CombinationType(NamedTuple):
    """
    An internal class representing a combination lock.
    """

    pins: tuple[int, ...]
    "The pins of the buttons (order sensitive)"
    seq: list[int]
    "The correct sequence of button indexes"

# ---------------------------------------------------------------------------- #
#                             Application settings                             #
# ---------------------------------------------------------------------------- #

DEBUG = False

# ------------------------------- PWM settings ------------------------------- #

PWM0 = 12
PWM1 = 13

# ------------------------------ Servo settings ------------------------------ #

SERVO0PIN = 23
"The control pin of the first door servo"
SERVO1PIN = 24
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

SERVO0MIN = 1000
"The 0deg duty cycle in μs"
SERVO0MAX = 2000
"The 180deg duty cycle in μs"

SERVO1MIN = 1000
"The 0deg duty cycle in μs"
SERVO1MAX = 2000
"The 180deg duty cycle in μs"

# ---------------------------------------------------------------------------- #
#                                Initialisation                                #
#                                                                              #
#                                DO NOT MODIFY!                                #
# ---------------------------------------------------------------------------- #

SERVO0 = ServoType(SERVO0PIN, SERVO0MIN, SERVO0MAX)
SERVO1 = ServoType(SERVO1PIN, SERVO1MIN, SERVO1MAX)

COMBO = CombinationType(COMBOPINS, COMBOSEQ)