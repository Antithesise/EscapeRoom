"""
Classes and helper functions, etc. Additionally contains all of config.py

© 2023 Antithesise
"""

from dataclasses import dataclass, field
from functools import lru_cache
from math import floor
from RPIO import PWM

from config import *

from typing import NamedTuple


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


lru_cache(50)
async def degtodutycycle(deg: int, servo: ServoType) -> int:
    """
    Convert degrees to duty cycle in μs based on a servo's config, updating it with the calculated value.
    """

    if not 0 <= deg <= servo.deg:
        raise ValueError(f"Servo range invalid: Cannot move servo {servo} to position {deg}deg.")

    dcdelta = servo.maxdc - servo.mindc
    off = dcdelta * deg / servo.deg

    dc = floor(servo.mindc + off)
    servo.dc = dc

    return dc

lru_cache(50)
async def freqtodutycycle(freqhz: int, piezo: PWMType | None=None) -> int:
    """
    Convert hertz to duty cycle in μs, optionally updating a piezo's config.
    """

    dc = floor(1000000 / freqhz) if freqhz else 0

    if piezo:
        piezo.dc = dc

    return dc


DOOR0 = ServoType(DOOR0PIN, DOOR0DEG, DOOR0MIN, DOOR0MAX, servoctl)
DOOR1 = ServoType(DOOR1PIN, DOOR1DEG, DOOR1MIN, DOOR1MAX, servoctl)

COMBO = CombinationType(COMBOPINS, COMBOSEQ)
