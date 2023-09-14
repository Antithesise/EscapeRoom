#!/usr/bin/python3

"""
The application's main script.

© 2023 Antithesise
"""

from asyncio import CancelledError, Event, Task, create_task, gather, get_event_loop_policy, run, sleep, timeout
from logging import error, debug, getLogger, info
from builtins import input as terminput # Grrrr: RPIO overrides `input` namespace
from functools import partial
from platform import machine
from time import time as now # less ambiguous than `time`
from threading import Lock
from RPIO import *

from util import * # also include config.py exports

from typing import Any, Callable


getLogger().setLevel(10 if DEBUG else 20)


setmode(MODE)

setup(DOOR0.pin, OUT)
setup(DOOR1.pin, OUT)

for p in COMBOPINS:
    setup(p, IN)

comboseq = []

mainlck = Lock()

loop = get_event_loop_policy().get_event_loop()


async def reset() -> Task | None:
    async def resetbg():
        debug("Reseting...")

        await gather(
            moveservo(DOOR0, 0),
            moveservo(DOOR1, 0)
        )

    return loop.create_task(resetbg())

async def moveservo(servo: ServoType, deg: int) -> None:
    """
    Activate a servo running on a gpio pin.
    """

    debug(f"Moving {servo} to pos {deg}...")

    dc = await degtodutycycle(deg, servo) # servo.dc = deg
    servo.ctl.set_servo(servo.pin, dc)

    await sleep(SERVODELAY / 1000) # ensure servo has had enough time to move

    await degtodutycycle(0, servo) # servo.dc = 0
    servo.ctl.stop_servo(servo.pin)

async def beep(piezo: PWMType, freqhz: int, duration: int) -> None:
    """
    Generate a frequency on a pwm pin for a length of time in ms.
    """

    debug("Beeping %s at %dhz for %dms...", repr(piezo), freqhz, duration)

    dc = await freqtodutycycle(freqhz, piezo) # piezo.dc = deg
    piezo.ctl.set_servo(piezo.pin, dc)

    await sleep(duration / 1000)

    await freqtodutycycle(0, piezo) # piezo.dc = 0
    piezo.ctl.stop_servo(piezo.pin)

    debug("Stopped beeping %s.", repr(piezo))

async def comlockbg() -> None:
    """
    Background process(s) to run while comlockseq is running.
    """

    debug("Starting combination lock background tasks...")

    try:
        while True:
            pass # run bg code

    except CancelledError:
        debug("Stopping combination lock background tasks...")

    finally:
        debug("Stopped combination lock background tasks.")

def comlockcbfactory(combo: CombinationType, pin: int) -> Callable[[], None]:
    """
    A factory to generate interrupt callback functions for a combination lock's pins.
    """

    async def callback(combo: CombinationType=combo, pin: int=pin):
        debug("Button press detected on pin %d.", pin)

        with mainlck:
            comboseq.append(combo.pinindex(pin)) # add pin to inputs

    return partial(loop.run_until_complete, callback(combo, pin))

async def comlockcheck(combo: CombinationType) -> None:
    """
    Check if (and block until) the combination is correct.
    """

    while True:
        await loop.run_in_executor(None, wait_for_interrupts) # wait_for_interrupts blocks synchronously,
                                                              # so we run in it executor and await output
        with mainlck: # access combo_seq so its threadsafe
            if comboseq == combo.seq:
                await gather( # remove callbacks
                    loop.run_in_executor(None, del_interrupt_callback, p) for p in combo.pins
                )

                debug("Correct combination detected.")

                comboseq.clear()

                break

            elif len(comboseq) >= len(combo.seq):
                debug("Incorrect combination detected: %s.", ", ".join(comboseq))

                comboseq.clear()

async def comlockseq(combo: CombinationType, callback: Callable[..., Any]) -> None:
    """
    Implement a 4 digit combintation lock running on gpio pins.
    """

    debug("Starting combination lock sequence...")

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

    debug("Finishing combination lock sequence...")
    debug("Calling %s...", callback.__name__)

    return callback()

async def ctrlrodbg() -> None:
    """
    Background process(s) to run while ctrlrodseq is running.
    """

    debug("Starting control rod background tasks...")

    try:
        while True:
            pass # run bg code

    except CancelledError:
        debug("Stopping control rod background tasks...")

    finally:
        debug("Stopped control rod background tasks.")

async def ctrlrodcheck(ctrlrodevent: Event) -> None:
    """
    Block until all control rods are in correct position.
    """

    await ctrlrodevent.wait() # blocks until all control rods are in correct place

    debug("All control rods detected.")

    await loop.run_in_executor(None, partial(
        del_interrupt_callback,
        CTRLRODPIN
    ))

async def ctrlrodseq(callback: Callable[..., Any]) -> None:
    """
    Implement a blocking function to wait until all control rods are in correct order.
    """

    debug("Starting control rod sequence...")

    ctrlrodevent = Event()

    await loop.run_in_executor(None, partial(
        add_interrupt_callback,
        CTRLRODPIN,
        callback=ctrlrodevent.set,
        edge="rising",
        threaded_callback=True
    ))

    await ctrlrodcheck(ctrlrodevent) # blocks until all control rods are in correct place

    debug("Finishing control rod sequence...")
    debug("Calling %s...", callback.__name__)

    return callback()

async def disarmcheck(disarmevent: Event) -> None:
    """
    Block until disarm switches have been flipped.
    """

    await disarmevent.wait() # blocks until all control rods are in correct place

    debug("Disarm switch flicked.")

    await loop.run_in_executor(None, partial(
        del_interrupt_callback,
        CTRLRODPIN
    ))

async def disarmbg() -> None:
    """
    Background process(s) to run while disarmseq is running.
    """

    debug("Starting disarm switch background tasks...")

    try:
        while True:
            pass # run bg code

    except CancelledError:
        debug("Stopping disarm switch background tasks...")

    finally:
        debug("Stopped disarm switch background tasks.")

async def disarmseq(callback: Callable[..., Any]) -> None:
    """
    Implement a blocking function to wait until the disarm switches have been flipped.
    """

    debug("Starting control rod sequence...")

    disarmevent = Event()

    await loop.run_in_executor(None, partial(
        add_interrupt_callback,
        DISARMPIN,
        callback=disarmevent.set,
        edge="rising",
        threaded_callback=True
    ))

    await disarmcheck(disarmevent) # blocks until both disarm switches have been flipped

    debug("Finishing disarm switch sequence...")
    debug("Calling %s...", callback.__name__)

    return callback()

async def winseq(timeleft: float | int) -> None:
    info("Escaped successfully!!")

    if timeleft > 0:
        info("Your time was %ds", round(TIMEOUT - timeleft))

async def failseq() -> None:
    info("Attempt failed!!")


async def main() -> None:
    """
    The application's main loop.
    """

    debug("Starting main loop...")

    while True:
        await reset()

        try:
            try:
                async with timeout(TIMEOUT) as gameto:
                    clbg = create_task(comlockbg())

                    await comlockseq(COMBO, clbg.cancel) # start combo lock sequence, blocking until complete
                    await clbg # clean up bg code

                    await moveservo(DOOR0, 90)

                    crbg = create_task(ctrlrodbg())

                    await ctrlrodseq(crbg.cancel) # start control rod sequence, blocking until complete
                    await crbg # clean up bg code

                    finbg = create_task(disarmbg())

                    await disarmseq(finbg.cancel) # start final sequence, blocking until complete
                    await finbg # clean up bg code

                    await moveservo(DOOR1, 90) # successfully escaped!

                await winseq((gameto.when() or 0) - now())

            except TimeoutError:
                await failseq()

            if BLOCKAFTER:
                info("Exit       [^C]")
                info("Next Game  [^D]")

                terminput("Waiting for input...")

        except EOFError:
            info("^D detected.")

            continue

        except KeyboardInterrupt:
            info("^C detected.")

            break

    debug("Exiting main loop...")


if __name__ == "__main__":
    if machine() != "armv7l":
        error("This script must be run on Raspberry Pi. Running mock library...")

    debug("test")

    run(main())