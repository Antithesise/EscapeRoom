from functools import cache as static
from warnings import warn

from RPIO._c_to_py import *

# from RPIO._h_Python import *
from RPIO._c_gpio import *
from RPIO._cpuinfo import *

# All these will get exposed via the Python module
class WrongDirectionException(Exception): ...
class InvalidModeException(Exception): ...
class InvalidDirectionException(Exception): ...
class InvalidChannelException(Exception): ...
class InvalidPullException(Exception):...
class ModeNotSetException(Exception): ...

high: int
low: int
input: int
output: int
alt0: int
board: int
bcm: int
pud_off: int
pud_up: int
pud_down: int
rpi_revision: int
rpi_revision_hex: int
version: int

# Conversion from board_pin_id to gpio_id
# eg. gpio_id = *(*pin_to_gpio_rev2 + board_pin_id)
pin_to_gpio_rev1 = [-1, -1, -1, 0, -1, 1, -1, 4, 14, -1, 15, 17, 18, 21, -1, 22, 23, -1, 24, 10, -1, 9, 25, 11, 8, -1, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
pin_to_gpio_rev2 = [-1, -1, -1, 2, -1, 3, -1, 4, 14, -1, 15, 17, 18, 27, -1, 22, 23, -1, 24, 10, -1, 9, 25, 11, 8, -1, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
pin_to_gpio_rev3 = [-1, -1, -1, 2, -1, 3, -1, 4, 14, -1, 15, 17, 18, 27, -1, 22, 23, -1, 24, 10, -1, 9, 24, 11, 7, -1, 7, -1, -1, 5, -1, 6, 12, 13, -1, 19, 16, 26, 20, -1, 21]
pin_to_gpio: Ptr[list[int]] = void *[]

# Board header info is shifted left 8 bits (leaves space for up to 255 channel ids per header)
HEADER_P1 = 0 << 8
HEADER_P5 = 5 << 8
gpio_to_pin_rev1 = [3, 5, -1, -1, 7, 0, -1, 26, 24, 21, 19, 23, -1, -1, 8, 10, -1, 11, 12, -1, -1, 13, 15, 16, 18, 22, -1, -1, -1, -1, -1, -1, -1]
gpio_to_pin_rev2 = [-1, -1, 3, 5, 7, 0, -1, 26, 24, 21, 19, 23, -1, -1, 8, 10, -1, 11, 12, -1, -1, -1, 15, 16, 18, 22, -1, 15, 3 | HEADER_P5, 4 | HEADER_P5, 5 | HEADER_P5, 6 | HEADER_P5, -1]
gpio_to_pin_rev3 = [-1, -1, 3, 5, 7, 29, 31, 26, 24, 21, 19, 23, 32, 33, 8, 10, 36, 11, 12, 35, 38, 40, 15, 16, 18, 22, 37, 13, -1, -1, -1, -1, 0]
gpio_to_pin: Ptr[list[int]] = void *[]

# Flag whether to show warnings
gpio_warnings = 1

# Which Raspberry Pi Revision is used (will be 1 or 2 0 if not a Raspberry Pi).
# Source: /proc/cpuinfo (via cpuinfo.c)
revision_int = 0
revision_hex = "\0" * 1024

# Internal map of directions (in/out) per gpio to prevent user mistakes.
gpio_direction = [-1] * 54

# GPIO Modes
MODE_UNKNOWN = -1
BOARD = 10
BCM = 11
gpio_mode = MODE_UNKNOWN

# Read /proc/cpuinfo once and keep the info at hand for further requests
def cache_rpi_revision() -> None:
    global revision_int

    revision_int = get_cpuinfo_revision(revision_hex)

# bcm_to_board() returns the pin for the supplied bcm_gpio_id or -1
# if not a valid gpio-id. P5 pins are returned with | HEADER_P5, so
# you can know the header with (retval >> 8) (either 0 or 5) and the
# exact pin number with (retval & 255).
@static
def bcm_to_board(bcm_gpio_id: int) -> int:
    global gpio_to_pin

    return gpio_to_pin[bcm_gpio_id]

# channel_to_bcm() returns the bcm gpio id for the supplied channel
# depending on current setmode. Only P1 header channels are supported.
# To use P5 you need to use BCM gpio ids (`setmode(BCM)`).
@static
def board_to_bcm(board_pin_id: int) -> int:
    global pin_to_gpio

    return pin_to_gpio[board_pin_id]

# module_setup is run on import of the GPIO module and calls the setup() method in c_gpio.c
def module_setup() -> int:
    # printf("Setup module (mmap)\n");

    # Set all gpios to input in internal direction (not the system)

    gpio_direction = [-1] * 54

    setup() # mock library doesn't need to perform checks

    return SETUP_OK

# Python function cleanup()
# Sets everything back to input
def py_cleanup() -> None:
    for i in range(54):
        if gpio_direction[i] != -1:
            setup_gpio(i, INPUT, PUD_OFF)
            gpio_direction[i] = -1

# channel_to_gpio tries to convert the supplied channel-id to
# a BCM GPIO ID based on current setmode. On error it sets the
# Python error string and returns a value < 0.
def channel_to_gpio(channel: int) -> int:
    if gpio_mode != BOARD and gpio_mode != BCM:
        raise ModeNotSetException("Please set pin numbering mode using RPIO.setmode(RPIO.BOARD) or RPIO.setmode(RPIO.BCM)")

    elif (gpio_mode == BCM and (channel < 0 or channel > 31)) or (gpio_mode == BOARD and (channel < 1 or channel > 41)):
        raise InvalidChannelException("The channel sent is invalid on a Raspberry Pi (outside of range)")

    elif gpio_mode == BOARD:
        if (gpio := board_to_bcm(channel)) == -1:
            raise InvalidChannelException("The channel sent is invalid on a Raspberry Pi (not a valid pin)")

    else:
        gpio = channel

        if bcm_to_board(gpio) == -1:
            raise InvalidChannelException("The channel sent is invalid on a Raspberry Pi (not a valid gpio)")

    return gpio

def verify_input(channel: int, gpio: Ptr[int]) -> int:
    gpio.obj = channel_to_gpio(channel)

    if gpio.obj == -1:
        return 0

    if gpio_direction[(int) &gpio] != INPUT and gpio_direction[(int) &gpio] != OUTPUT:
        raise WrongDirectionException("GPIO channel has not been set up")

    return 1

# python function setup(channel, direction, pull_up_down=PUD_OFF, initial=None)
def py_setup_channel(channel: int, direction: int, pull_up_down: int=PUD_OFF, initial=-1) -> None:
    if direction not in [INPUT, OUTPUT]:
        raise InvalidDirectionException("An invalid direction was passed to setup()")

    if direction == OUTPUT:
        pull_up_down = PUD_OFF

    if pull_up_down not in [PUD_OFF, PUD_DOWN, PUD_UP]:
        raise InvalidPullException("Invalid value for pull_up_down - should be either PUD_OFF, PUD_UP or PUD_DOWN")

    if (gpio := channel_to_gpio(channel)) < 0:
        return

    func = gpio_function(gpio)
    if gpio_warnings and (func not in [0, 1] or (gpio_direction[gpio] == -1 and func == 1)):
        warn("This channel is already in use, continuing anyway.  Use RPIO.setwarnings(False) to disable warnings.")

    # printf("Setup GPIO %d direction %d pud %d\n", gpio, direction, pud)
    if direction == OUTPUT and initial in [LOW, HIGH]:
        # printf("Writing intial value %d\n",initial)
        output_gpio(gpio, initial)

    setup_gpio(gpio, direction, pull_up_down)

    gpio_direction[gpio] = direction

# python function output(channel, value)
def py_output_gpio(channel: int, value: int) -> None:
    if (gpio := channel_to_gpio(channel)) < 0:
        return

    if gpio_direction[gpio] != OUTPUT:
        raise WrongDirectionException("The GPIO channel has not been set up as an OUTPUT")

    # printf("Output GPIO %d value %d\n", gpio, value);
    output_gpio(gpio, value)

# python function output(channel, value) without direction check
def py_forceoutput_gpio(channel: int, value: int) -> None:
    # printf("Output GPIO %d value %d\n", gpio, value);
    if (gpio := channel_to_gpio(channel)) < 0:
        return

    output_gpio(gpio, value)

# python function output(channel, value) without direction check
def py_set_pullupdn(channel: int, pull_up_down: int=PUD_OFF) -> None:
    if (gpio := channel_to_gpio(channel)) < 0:
        return

    # printf("Setting gpio %d PULLUPDN to %d", gpio, pud)
    set_pullupdn(gpio, pull_up_down)

# python function value = input(channel)
def py_input_gpio(channel: int) -> bool | None:
    gpio = void *(0)

    if not verify_input(channel, gpio):
        return

    # printf("Input GPIO %d\n", gpio);
    return bool(input_gpio(*gpio))

# python function value = input(channel) without direction check
def py_forceinput_gpio(channel: int) -> bool | None:
    if (gpio := channel_to_gpio(channel)) < 0:
        return

    # printf("Input GPIO %d\n", gpio);
    return bool(input_gpio(gpio))

# python function setmode(mode)
def setmode(mode) -> None:
    global gpio_mode

    if mode not in [BOARD, BCM]:
        raise InvalidModeException("An invalid mode was passed to setmode()")

    gpio_mode = mode

# python function value = gpio_function(gpio)
def py_gpio_function(gpio: int) -> int:
    return OUTPUT if gpio_function(gpio) else INPUT

# python function setwarnings(state)
def py_setwarnings(state: int) -> None:
    global gpio_warnings

    gpio_warnings = state

# channel2gpio binding
def py_channel_to_gpio(channel: int) -> int | None:
    if (gpio := channel_to_gpio(channel)) >= 0:
        return gpio