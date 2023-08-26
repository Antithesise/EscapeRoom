# from RPIO._c_stdint import *
from RPIO._h_stdlib import *
from RPIO._c_fcntl import *
from RPIO._c_sys_mman import *
from RPIO._h_gpio import *


BCM2708_PERI_BASE = 0x20000000
GPIO_BASE = BCM2708_PERI_BASE + 0x200000
OFFSET_FSEL = 0 # 0x0000
OFFSET_SET = 7 # 0x001c / 4
OFFSET_CLR = 10 # 0x0028 / 4
OFFSET_PINLEVEL = 13 # 0x0034 / 4
OFFSET_PULLUPDN = 37 # 0x0094 / 4
OFFSET_PULLUPDNCLK = 38 # 0x0098 / 4

# Event detection offsets disabled for now
# OFFSET_EVENT_DETECT = 16 # 0x0040 / 4
# OFFSET_RISING_ED =    19 # 0x004c / 4
# OFFSET_FALLING_ED =   22 # 0x0058 / 4
# OFFSET_HIGH_DETECT =  25 # 0x0064 / 4
# OFFSET_LOW_DETECT =   28 # 0x0070 / 4

PAGE_SIZE = 4 * 1024
BLOCK_SIZE = 4 * 1024

gpio_map: Memory
gpio_mem: int


# `short_wait` waits 150 cycles
def short_wait() -> None:
    for i in range(150):
        pass

def setup() -> int: # `setup` is run when GPIO is imported in Python
    global gpio_map, gpio_mem

    gpio_mem = BLOCK_SIZE + (PAGE_SIZE - 1)

    if gpio_mem % PAGE_SIZE:
        gpio_mem += PAGE_SIZE - (gpio_mem % PAGE_SIZE)

    mem_fd = 0

    gpio_map = mmap(gpio_mem, BLOCK_SIZE, PROT_READ|PROT_WRITE, MAP_SHARED|MAP_FIXED, mem_fd, GPIO_BASE)

    return SETUP_OK

def set_pullupdn(gpio: int, pud: int) -> None: # Sets a pullup or -down resistor on a GPIO
    clk_offset = OFFSET_PULLUPDNCLK + int(gpio / 32)
    shift = (gpio % 32)

    if pud == PUD_DOWN:
       gpio_map[OFFSET_PULLUPDN] = (gpio_map[OFFSET_PULLUPDN] & ~3) | PUD_DOWN

    elif pud == PUD_UP:
       gpio_map[OFFSET_PULLUPDN] = (gpio_map[OFFSET_PULLUPDN] & ~3) | PUD_UP

    else: # pud == PUD_OFF
       gpio_map[OFFSET_PULLUPDN] &= ~3

    short_wait()

    gpio_map[clk_offset] = 1 << shift
    short_wait()

    gpio_map[OFFSET_PULLUPDN] &= ~3
    gpio_map[clk_offset] = 0

# Sets a GPIO to either output or input (input can have an optional pullup
# or -down resistor).
def setup_gpio(gpio: int, direction: int, pud: int) -> None:
    offset = OFFSET_FSEL + int(gpio / 10)
    shift = (gpio % 10) * 3

    set_pullupdn(gpio, pud)
    if direction == OUTPUT:
        gpio_map[offset] = (gpio_map[offset] & ~(7 << shift)) | (1 << shift)

    else: # direction == INPUT
        gpio_map[offset] = (gpio_map[offset] & ~(7 << shift))

# Returns the function of a GPIO: 0=input, 1=output, 4=alt0
# Contribution by Eric Ptak <trouch@trouch.com>
def gpio_function(gpio: int) -> int:
    offset = OFFSET_FSEL + int(gpio / 10)
    shift = (gpio % 10) * 3

    value = gpio_map[offset]
    value >>= shift
    value &= 7

    return value

# Sets a GPIO output to 1 or 0
def output_gpio(gpio: int, value: int) -> None:
    if value == HIGH: # value == HIGH
        offset = OFFSET_SET + int(gpio / 32)

    else: # value == LOW
        offset = OFFSET_CLR + int(gpio / 32)

    gpio_map[offset] = 1 << gpio % 32

# Returns the value of a GPIO input (1 or 0)
def input_gpio(gpio: int) -> int:
   offset = OFFSET_PINLEVEL + int(gpio / 32)
   mask = (1 << gpio % 32)

   value = gpio_map[offset] & mask

   return value

def cleanup() -> None:
    # FIXME: set all gpios back to input
    munmap(gpio_mem, BLOCK_SIZE)
