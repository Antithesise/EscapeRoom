def setup() -> int: ...
def setup_gpio(gpio: int, direction: int, pud: int) -> None: ...
def output_gpio(gpio: int, value: int) -> None: ...
def input_gpio(gpio: int) -> int: ...
def cleanup() -> None: ...
def gpio_function(gpio: int) -> int: ...
def set_pullupdn(gpio: int, pud: int) -> None: ...

SETUP_OK = 0
SETUP_DEVMEM_FAIL = 1
SETUP_MALLOC_FAIL = 2
SETUP_MMAP_FAIL = 3

INPUT = 1 # is really 0 for control register!
OUTPUT = 0 # is really 1 for control register!
ALT0 = 4

HIGH = 1
LOW = 0

PUD_OFF = 0
PUD_DOWN = 1
PUD_UP = 2