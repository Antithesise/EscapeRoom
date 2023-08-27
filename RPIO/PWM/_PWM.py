__module__ = "_PWM"
__doc__ = None
__all__ = []

from RPIO.PWM._py_pwm import *

from atexit import register as Py_AtExit

from typing import TypeVar


_T = TypeVar("_T")


def PyModule_AddObject(name: str, obj: _T) -> _T:
    globals()["__all__"].append(name)

    if hasattr(obj, "__name__"):
        obj.__name__ = name # type: ignore

    return obj


setup = PyModule_AddObject("setup", py_setup)
setup.__doc__ = "Setup the DMA-PWM system"

cleanup = PyModule_AddObject("cleanup", py_cleanup)
cleanup.__doc__ = "Stop all pwms and clean up DMA engine"

init_channel = PyModule_AddObject("init_channel", py_init_channel)
init_channel.__doc__ = "Setup a channel with a specific period time and hardware"

clear_channel = PyModule_AddObject("clear_channel", py_clear_channel)
clear_channel.__doc__ = "Clear all pulses on this channel"

clear_channel_gpio = PyModule_AddObject("clear_channel_gpio", py_clear_channel_gpio)
clear_channel_gpio.__doc__ = "Clear one specific GPIO from this channel"

add_channel_pulse = PyModule_AddObject("add_channel_pulse", py_add_channel_pulse)
add_channel_pulse.__doc__ = "Add a specific pulse to a channel"

print_channel = PyModule_AddObject("print_channel", py_print_channel)
print_channel.__doc__ = "Print info about a specific channel"

set_loglevel = PyModule_AddObject("set_loglevel", py_set_loglevel)
set_loglevel.__doc__ = "Set the loglevel to either 0 (debug) or 1 (errors)"

is_setup = PyModule_AddObject("is_setup", py_is_setup)
is_setup.__doc__ = "Returns 1 is setup(..) has been called, else 0"

get_pulse_incr_us = PyModule_AddObject("get_pulse_incr_us", py_get_pulse_incr_us)
get_pulse_incr_us.__doc__ = "Gets the pulse width increment granularity in us"

is_channel_initialized = PyModule_AddObject("is_channel_initialized", py_is_channel_initialized)
is_channel_initialized.__doc__ = "Returns 1 if channel has been initialized, else 0"

get_channel_subcycle_time_us = PyModule_AddObject("get_channel_subcycle_time_us", py_get_channel_subcycle_time_us)
get_channel_subcycle_time_us.__doc__ = "Gets the subcycle time in us of the specified channel"


VERSION = PyModule_AddObject("VERSION", "0.10.1")
DELAY_VIA_PWM = PyModule_AddObject("DELAY_VIA_PWM", DELAY_VIA_PWM)
DELAY_VIA_PCM = PyModule_AddObject("DELAY_VIA_PCM", DELAY_VIA_PCM)
LOG_LEVEL_DEBUG = PyModule_AddObject("LOG_LEVEL_DEBUG", LOG_LEVEL_DEBUG)
LOG_LEVEL_ERRORS = PyModule_AddObject("LOG_LEVEL_ERRORS", LOG_LEVEL_ERRORS)
LOG_LEVEL_DEFAULT = PyModule_AddObject("LOG_LEVEL_DEFAULT", LOG_LEVEL_DEFAULT)
SUBCYCLE_TIME_US_DEFAULT = PyModule_AddObject("SUBCYCLE_TIME_US_DEFAULT", SUBCYCLE_TIME_US_DEFAULT)
PULSE_WIDTH_INCREMENT_GRANULARITY_US_DEFAULT = PyModule_AddObject("PULSE_WIDTH_INCREMENT_GRANULARITY_US_DEFAULT", PULSE_WIDTH_INCREMENT_GRANULARITY_US_DEFAULT)

# Enable PWM.C soft-fatal mode in order to convert them to python exceptions
set_softfatal(1)

Py_AtExit(shutdown)