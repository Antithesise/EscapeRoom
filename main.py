#!/usr/bin/python3

"""
The application's main script.
"""

from asyncio import create_task, gather, get_event_loop, run, sleep
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

setup(DOOR0.pin, OUT)
setup(DOOR1.pin, OUT)

for p in COMBOPINS:
    setup(p, IN)

comboseq = []
combolck = Lock()

loop = get_event_loop()


async def reset() -> None:
    info("reseting...")

    await gather(
        moveservo(DOOR0, 0),
        moveservo(DOOR1, 0)
    )


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

async def moveservo(servo: ServoType, deg: int) -> None:
    """
    Activate a servo running on a gpio pin.
    """

    dc = await degtodutycycle(deg, servo) # also sets servo.dc
    servo.ctl.set_servo(servo.pin, dc)

    await sleep(0.05) # ensure servo has had enough time to move

    await degtodutycycle(0, servo) # servo.dc = 0
    servo.ctl.stop_servo(servo.pin)

async def beep(piezo: PWMType, freqhz: int, duration: int):
    """
    Generate a frequency on a pwm pin for a length of time in ms.
    """

    dc = await freqtodutycycle(freqhz, piezo) # also sets piezo.dc
    piezo.ctl.set_servo(piezo.pin, dc)

    await sleep(duration / 1000)

    await freqtodutycycle(0, piezo) # piezo.dc = 0
    piezo.ctl.stop_servo(piezo.pin)

async def comlockbg() -> None:
    """
    Background process(s) to run while comlockseq is running.
    """

async def comlockcheck(combo: CombinationType) -> None:
    """
    Check if the combination is correct.
    """

    while True:
        await loop.run_in_executor(None, wait_for_interrupts) # wait_for_interrupts blocks, so it needs to be awaited

        with combolck:
            if comboseq == combo.seq:
                for p in combo.pins:
                    del_interrupt_callback(p) # remove callbacks

                comboseq.clear() # reset inputs

                break # exit loop, and return to comlockseq

            elif len(comboseq) >= len(combo.seq):
                comboseq.clear() # reset inputs

def comlockcbfactory(combo: CombinationType, pin: int):
    """
    A factory to generate interrupt callback functions for a combination lock's pins.
    """

    def callback(combo: CombinationType=combo, pin: int=pin) -> None:
        with combolck:
            comboseq.append(combo.pinindex(pin)) # add pin to inputs

    return callback

async def comlockseq(combo: CombinationType, callback: Callable) -> None:
    """
    Implement a 4 digit combintation lock running on gpio pins.
    """

    for p in combo.pins:
        add_interrupt_callback(p, comlockcbfactory(combo, p), edge="rising", threaded_callback=True)

    await comlockcheck(combo) # the func blocks until correct code inputted

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