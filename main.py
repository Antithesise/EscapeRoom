"""
The main script
"""

from platform import machine
from RPIO import *

from config import *


def reset() -> None:
    setmode(BCM)


def comlockseq(pins: tuple[int, int, int, int], callback: function) -> None:
    """
    Implement a 4 digit combintation lock running on gpio pins.
    """

def opendoor(pins: int, dir: bool) -> None:
    """
    Activate a servo running on a gpio pin
    """



if __name__ == "__main__":
    if machine() != "armv7l":
        raise EnvironmentError("This script must be run on Raspberry Pi")

    while True:
        reset()

        try:
            comlockseq((COMBO0, COMBO1, COMBO2, COMBO3), lambda: opendoor(SERVO0, True))
        except EOFError:
            break