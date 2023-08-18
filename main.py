#!/usr/bin/python3

"""
The application's main script.
"""

from asyncio import create_task, gather, run, sleep
from functools import lru_cache
from logging import error, info
from platform import machine
from threading import Lock
from math import floor
from RPIO import PWM
from RPIO import *

from config import *

from typing import Callable


setmode(MODE)

piezoctl = PWM.Servo()
servoctl = PWM.Servo()

setup(DOOR0, OUT)
setup(DOOR1, OUT)

for p in COMBOPINS:
    setup(p, IN)

comboseq = []

mainlock = Lock()


async def reset() -> None:
    info("reseting...")

    await gather(
        moveservo(DOOR0, 0),
        moveservo(DOOR1, 0)
    )


async def moveservo(servo: ServoType, deg: int) -> None:
    """
    Activate a servo running on a gpio pin.
    """

    dc = await degtodutycycle(deg, servo)

    servoctl.set_servo(servo.pin, dc)

    await sleep(0.05) # ensure servo has had enough time to move

    servoctl.stop_servo(servo.pin)

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

async def beep(piezo: PWMType, freqhz: int, duration: int):
    """
    Generate a frequency on a pwm pin for a length of time in ms.
    """

    dc = await freqtodutycycle(freqhz, piezo) # also sets piezo.pw
    piezoctl.set_servo(piezo.pin, dc)

    await sleep(0.05) # ensure servo has had enough time to move

    await freqtodutycycle(0, piezo) # piezo.pw = 0
    piezoctl.stop_servo(piezo.pin)

async def comlockbg() -> None:
    """
    Background process to run while comlockseq is running.
    """

async def comlockcheck(combo: CombinationType) -> None:
    """
    Check if the combination is correct
    """

    while True:
        wait_for_interrupts()

        with mainlock:
            if comboseq == combo.seq:
                comboseq.clear()

            elif len(comboseq) >= len(combo.seq):
                comboseq.clear()



def comlockcbfactory(combo: CombinationType, pin: int):
    """
    A factory to generate callback functions for a combination lock.
    """

    def callback(combo: CombinationType=combo, pin: int=pin) -> None:
        with mainlock:
            comboseq.append(combo.pinindex(pin))

    return callback

async def comlockseq(combo: CombinationType, callback: Callable) -> None:
    """
    Implement a 4 digit combintation lock running on gpio pins.
    """

    for p in combo.pins:
        add_interrupt_callback(p, comlockcbfactory(combo, p), "rising", threaded_callback=True)

    await comlockcheck(combo)

    return callback()


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

            await moveservo(DOOR0, 90)


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