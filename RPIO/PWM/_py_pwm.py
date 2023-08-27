# from _h_Python import *
from RPIO._h_stdlib import *
from RPIO.PWM._c_pwm import *

def raise_error() -> None:
    raise RuntimeError(get_error_message())

# python function int setup(int pw_incr_us, int hw)
def py_setup(pw_incr_us: Ptr[int]=void *-1, delay_hw: Ptr[int]=void *-1) -> None:
    if pw_incr_us.obj == -1:
        pw_incr_us.obj = PULSE_WIDTH_INCREMENT_GRANULARITY_US_DEFAULT
    if delay_hw.obj == -1:
        delay_hw.obj = DELAY_VIA_PWM

    if setup(pw_incr_us, delay_hw) == EXIT_FAILURE:
        return raise_error()

# python function cleanup()
def py_cleanup() -> None:
    shutdown()

# python function init_channel(int channel, int subcycle_time_us)
def py_init_channel(channel: int, subcycle_time_us: int=-1) -> None:
    if subcycle_time_us == -1:
        subcycle_time_us = SUBCYCLE_TIME_US_DEFAULT

    if init_channel(channel, subcycle_time_us) == EXIT_FAILURE:
        return raise_error()

# python function clear_channel_pulses(int channel)
def py_clear_channel(channel: int) -> None:
    if clear_channel(channel) == EXIT_FAILURE:
        return raise_error()

# python function int clear_channel_gpio(int channel, int gpio)
def py_clear_channel_gpio(channel: int, gpio: int) -> None:
    if clear_channel_gpio(channel, gpio) == EXIT_FAILURE:
        return raise_error()

# python function (void) add_channel_pulse(int channel, int gpio, int width_start, int width)
def py_add_channel_pulse(channel: int, gpio: int, width_start: int, width: int) -> None:
    if add_channel_pulse(channel, gpio, width_start, width) == EXIT_FAILURE:
        return raise_error()

# python function print_channel(int channel)
def py_print_channel(channel: int) -> None:
    if print_channel(channel) == EXIT_FAILURE:
        return raise_error()

# python function (void) set_loglevel(level)
def py_set_loglevel(level: int) -> None:
    set_loglevel(level)

# python function int is_setup()
def py_is_setup() -> int:
    return is_setup()

# python function int get_pulse_incr_us()
def py_get_pulse_incr_us():
    return get_pulse_incr_us()

# python function int is_channel_initialized(int channel)
def py_is_channel_initialized(channel: int):
    return is_channel_initialized(channel)

# python function int get_channel_subcycle_time_us(int channel)
def py_get_channel_subcycle_time_us(channel: int):
    return get_channel_subcycle_time_us(channel)