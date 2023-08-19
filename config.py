"""
Config file for specifying pins, modes, solutions, etc.

All pin numbers assume BCM, unless MODE is changed.
"""

from dataclasses import dataclass, field
from RPIO import BCM, BOARD
from RPIO import PWM

from typing import NamedTuple

# ---------------------------------------------------------------------------- #
#                               Classes and util                               #
#                                                                              #
#                                DO NOT MODIFY!                                #
# ---------------------------------------------------------------------------- #

defctl = PWM.Servo()
piezoctl = PWM.Servo()
servoctl = PWM.Servo()

@dataclass # I see no reason why these dataclasses should be immutable
class PWMType:
    """
    An internal class representing a pwm pin.
    """

    pin: int
    "The pin number"
    ctl: PWM.Servo = defctl
    "The RPIO controller class"

    dc: int = field(default=0, init=False)
    "The current duty cycle of the pin"

@dataclass
class ServoType: # not inherited from PWMType due to arg ordering (kw_only doesn't fix this)
    """
    An internal class representing a servo motor.
    """

    pin: int
    "The control pin number"
    deg: int = 180
    "The range of motion in deg"
    mindc: int = 1000
    "The 0deg duty cycle in μs"
    maxdc: int = 2000
    "The 180deg duty cycle in μs"
    ctl: PWM.Servo = defctl
    "The RPIO controller class"

    dc: int = field(default=0, init=False)
    "The current duty cycle of the pin"

class CombinationType(NamedTuple):
    """
    An internal class representing a combination lock.
    """

    pins: tuple[int, ...]
    "The pins of the buttons (order sensitive)"
    seq: list[int]
    "The correct sequence of button indexes"

    def pinindex(self, pin: int) -> int:
        return self.pins.index(pin) if pin in self.pins else -1

# ---------------------------------------------------------------------------- #
#                             Application settings                             #
# ---------------------------------------------------------------------------- #

DEBUG = False

# ------------------------------- PWM settings ------------------------------- #

PWM0 = 12
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

# ---------------------------------------------------------------------------- #
#                                Initialisation                                #
#                                                                              #
#                                DO NOT MODIFY!                                #
# ---------------------------------------------------------------------------- #

DOOR0 = ServoType(DOOR0PIN, DOOR0DEG, DOOR0MIN, DOOR0MAX, servoctl)
DOOR1 = ServoType(DOOR1PIN, DOOR1DEG, DOOR1MIN, DOOR1MAX, servoctl)

COMBO = CombinationType(COMBOPINS, COMBOSEQ)