#!/usr/bin/python3

"""
The application's main script.
"""

from asyncio import gather, run
from functools import lru_cache
from logging import error, info
from platform import machine
from math import floor
from RPIO import PWM
from RPIO import *

from config import *

from typing import Coroutine


setmode(MODE)

servoctl = PWM.Servo()

setup(SERVO0, OUT)
setup(SERVO1, OUT)


async def reset() -> None:
    await gather(
        opendoor(SERVO0, False),
        opendoor(SERVO1, False)
    )


lru_cache(50)
async def degtodutycycle(servo: ServoType, deg: int) -> int:
    """
    Convert degrees to duty cycle in μs based on a servo's config.
    """

    assert 0 <= deg <= 180, f"Servo range invalid: Cannot move servo on pin {servo.pin} to {deg}deg."

    dcdelta = servo.maxdc - servo.mindc

    off = dcdelta * deg / 180

    return floor(servo.mindc + off)

async def comlockseq(combo: CombinationType, callback: Coroutine) -> None:
    """
    Implement a 4 digit combintation lock running on gpio pins.
    """

    while True:
        for p in combo.pins:
            pass # do stuff

        break

    return await callback

async def opendoor(servo: ServoType, deg: int) -> None:
    """
    Activate a servo running on a gpio pin.
    """

    dc = await degtodutycycle(servo, deg)

    servoctl.set_servo(servo.pin, dc)


async def main() -> None:
    """
    The application's main loop.
    """

    info("Starting main loop...")

    while True:
        await reset()

        try:
            await comlockseq(COMBO, opendoor(SERVO0, True))

        except EOFError:
            info("^D detected, reseting...")
            continue

        except KeyboardInterrupt:
            info("^C detected, exiting")
            break


if __name__ == "__main__":
    if machine() != "armv7l":
        raise EnvironmentError("This script must be run on Raspberry Pi")

    run(main())