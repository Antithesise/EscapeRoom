__module__ = "_GPIO"
__doc__ = None
__all__ = []

from RPIO._py_gpio import *

from atexit import register as Py_AtExit
from logging import info

from typing import TypeVar


_T = TypeVar("_T")


def PyModule_AddObject(name: str, obj: _T) -> _T:
    globals()["__all__"].append(name)

    if hasattr(obj, "__name__"):
        obj.__name__ = name # type: ignore

    return obj


setup = PyModule_AddObject("setup", py_setup_channel)
setup.__doc__ = "Set up the GPIO channel, direction and (optional) pull/up down control\nchannel    - Either: RPi board pin number (not BCM GPIO 00..nn number).  Pins start from 1\n                or     : BCM GPIO number\ndirection - INPUT or OUTPUT\n[pull_up_down] - PUD_OFF (default), PUD_UP or PUD_DOWN\n[initial]        - Initial value for an output channel"

cleanup = PyModule_AddObject("cleanup", py_cleanup)
cleanup.__doc__ = "Clean up by resetting all GPIO channels that have been used by this program\nto INPUT with no pullup/pulldown and no event detection"

output = PyModule_AddObject("output", py_output_gpio)
output.__doc__ = "Output to a GPIO channel"

input = PyModule_AddObject("input", py_input_gpio)
input.__doc__ = "Input from a GPIO channel"

setmode = PyModule_AddObject("setmode", setmode)
setmode.__doc__ = "Set up numbering mode to use for channels.\nBOARD - Use Raspberry Pi board numbers\nBCM    - Use Broadcom GPIO 00..nn numbers"

setwarnings = PyModule_AddObject("setwarnings", py_setwarnings)
setwarnings.__doc__ = "Enable or disable warning messages"

# New methods in RPIO
forceoutput = PyModule_AddObject("forceoutput", py_forceoutput_gpio)
forceoutput.__doc__ = "Force output to a GPIO channel, ignoring whether it has been set up before."

forceinput = PyModule_AddObject("forceinput", py_forceinput_gpio)
forceinput.__doc__ = "Force read input from a GPIO channel, ignoring whether it was set up before."

set_pullupdn = PyModule_AddObject("set_pullupdn", py_set_pullupdn)
set_pullupdn.__doc__ = "Set pullup or -down resistor on a GPIO channel."

gpio_function = PyModule_AddObject("gpio_function", py_gpio_function)
gpio_function.__doc__ = "Return the current GPIO function (IN, OUT, ALT0)"

channel_to_gpio = PyModule_AddObject("channel_to_gpio", py_channel_to_gpio)
channel_to_gpio.__doc__ = "Return BCM or BOARD id of channel (depending on current setmode)"

WrongDirectionException = PyModule_AddObject("WrongDirectionException", WrongDirectionException)
InvalidModeException = PyModule_AddObject("InvalidModeException", InvalidModeException)
InvalidDirectionException = PyModule_AddObject("InvalidDirectionException", InvalidDirectionException)
InvalidChannelException = PyModule_AddObject("InvalidChannelException", InvalidChannelException)
InvalidPullException = PyModule_AddObject("InvalidPullException", InvalidPullException)
ModeNotSetException = PyModule_AddObject("ModeNotSetException", ModeNotSetException)

high = HIGH
HIGH = PyModule_AddObject("HIGH", high)
low = LOW
LOW = PyModule_AddObject("LOW", low)
output = OUTPUT
OUT = PyModule_AddObject("OUT", output)
input = INPUT
IN = PyModule_AddObject("IN", input)
alt0 = ALT0
ALT0 = PyModule_AddObject("ALT0", alt0)
board = BOARD
BOARD = PyModule_AddObject("BOARD", board)
bcm = BCM
BCM = PyModule_AddObject("BCM", bcm)
pud_off = PUD_OFF
PUD_OFF = PyModule_AddObject("PUD_OFF", pud_off)
pud_up = PUD_UP
PUD_UP = PyModule_AddObject("PUD_UP", pud_up)
pud_down = PUD_DOWN
PUD_DOWN = PyModule_AddObject("PUD_DOWN", pud_down)

# detect board revision and set up accordingly
cache_rpi_revision()
match revision_int:
    case 1:
        pin_to_gpio = void *pin_to_gpio_rev1
        gpio_to_pin = void *gpio_to_pin_rev1

    case 2:
        pin_to_gpio = void *pin_to_gpio_rev2
        gpio_to_pin = void *gpio_to_pin_rev2

    case 3:
        pin_to_gpio = void *pin_to_gpio_rev3
        gpio_to_pin = void *gpio_to_pin_rev3

    case _:
        info("Running mock RPIO...")

        pin_to_gpio = void *pin_to_gpio_rev3
        gpio_to_pin = void *gpio_to_pin_rev3

rpi_revision = revision_int
RPI_REVISION = PyModule_AddObject("RPI_REVISION", rpi_revision)
rpi_revision_hex = revision_hex
RPI_REVISION_HEX = PyModule_AddObject("RPI_REVISION_HEX", rpi_revision_hex)
version = "0.10.1/0.4.2a"
VERSION_GPIO = PyModule_AddObject("VERSION_GPIO", version)

# set up mmaped areas
module_setup()

Py_AtExit(cleanup)