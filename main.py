#!/usr/bin/python3

"""
The application's main script.

© 2023 Antithesise
"""

from asyncio import CancelledError, create_task, gather, get_event_loop, run, sleep
from logging import error, info
from functools import partial
from platform import machine
from threading import Lock
from RPIO import *

from util import * # also include config.py exports

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
    async def resetbg():
        info("reseting...")

        await gather(
            moveservo(DOOR0, 0),
            moveservo(DOOR1, 0)
        )

    await loop.create_task(resetbg())

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

    try:
        while True:
            pass # run bg code

    except CancelledError:
        pass # clean up etc.

def comlockcbfactory(combo: CombinationType, pin: int) -> Callable[[], None]:
    """
    A factory to generate interrupt callback functions for a combination lock's pins.
    """

    async def callback(combo: CombinationType=combo, pin: int=pin):
        with combolck:
            comboseq.append(combo.pinindex(pin)) # add pin to inputs

    return partial(loop.run_until_complete, callback(combo, pin))

async def comlockcheck(combo: CombinationType) -> None:
    """
    Check if the combination is correct.
    """

    while True:
        await loop.run_in_executor(None, wait_for_interrupts) # wait_for_interrupts blocks synchronously,
                                                              # so we run in it executor and await output
        with combolck: # access combo_seq so its
            if comboseq == combo.seq:
                await gather( # remove callbacks
                    loop.run_in_executor(None, del_interrupt_callback, p) for p in combo.pins
                )

                comboseq.clear() # reset inputs

                break # exit loop, and return to comlockseq

            elif len(comboseq) >= len(combo.seq):
                comboseq.clear() # reset inputs

async def comlockseq(combo: CombinationType, callback: Callable) -> None:
    """
    Implement a 4 digit combintation lock running on gpio pins.
    """

    await gather( # add callbacks
        loop.run_in_executor(None, partial(
            add_interrupt_callback,
            p,
            callback=comlockcbfactory(combo, p),
            edge="rising",
            threaded_callback=True
        )) for p in combo.pins
    )

    await comlockcheck(combo) # blocks until correct code is inputted

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

            await comlockseq(COMBO, clbg.cancel) # start combo lock sequence, bloxking until complete
            await clbg # clean up bg code

            await moveservo(DOOR0, 90)

        except EOFError:
            info("^D detected, reseting...")

            continue

        except KeyboardInterrupt:
            info("^C detected, exiting")

            return


if __name__ == "__main__":
    if machine() != "armv7l":
        raise EnvironmentError("This script must be run on Raspberry Pi")

    run(main())