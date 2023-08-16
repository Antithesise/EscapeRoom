#!/usr/bin/python3

"""
The application's main script.
"""

from asyncio import create_task, gather, run
from functools import lru_cache
from logging import error, info
from platform import machine
from math import floor
from RPIO import PWM
from RPIO import *

from config import *

from typing import Callable, Coroutine


setmode(MODE)

servoctl = PWM.Servo()

setup(SERVO0, OUT)
setup(SERVO1, OUT)


async def reset() -> None:
    info("reseting...")

    await gather(
        opendoor(SERVO0, False),
        opendoor(SERVO1, False)
    )


lru_cache(50)
async def degtodutycycle(servo: ServoType, deg: int) -> int:
    """
    Convert degrees to duty cycle in μs based on a servo's config.
    """

    if not 0 <= deg <= servo.deg:
        raise ValueError(f"Servo range invalid: Cannot move servo {servo} to position {deg}deg.")

    dcdelta = servo.maxdc - servo.mindc
    off = dcdelta * deg / servo.deg

    return floor(servo.mindc + off)

async def comlockbg() -> None:
    """
    Background process to run while comlockseq is running.
    """

async def comlockseq(combo: CombinationType, callback: Callable) -> None:
    """
    Implement a 4 digit combintation lock running on gpio pins.
    """

    while True:
        for p in combo.pins:
            pass # do stuff

        break

    return callback()

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
            clbg = create_task(comlockbg())
            await comlockseq(COMBO, clbg.cancel)

            await opendoor(SERVO0, 90)


        except EOFError:
            info("^D detected, reseting...")
            continue

        except KeyboardInterrupt:
            info("^C detected, exiting")
            break


if __name__ == "__main__":
    if machine() != "armv7l":
        raise EnvironmentError("This script must be run on Raspberry Pi")

    run(main()) # simple app doesn't need asyncio.get_event_loop() etc.