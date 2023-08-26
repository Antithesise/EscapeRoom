# from RPIO._h_stdio import *
from RPIO._h_stdlib import *
# from RPIO._h_unistd import *
# from RPIO._h_string import *
# from RPIO._h_errno import *
# from RPIO._h_stdarg import *
# from RPIO._h_stdint import *
from RPIO._c_signal import *
# from RPIO._h_time import *
from RPIO._c_sys_time import *
# from RPIO._h_sys_types import *
# from RPIO._h_sys_stat import *
from RPIO._h_fcntl import *
from RPIO._h_sys_mman import *
from RPIO.PWM._h_pwm import *
from RPIO._c_to_py import *

from logging import debug, error

from typing import Any, NamedTuple

# 15 DMA channels are usable on the RPi (0..14)
DMA_CHANNELS = 15

# Standard page sizes
PAGE_SIZE = 4096
PAGE_SHIFT = 12

# Memory Addresses
DMA_BASE = 0x20007000
DMA_CHANNEL_INC = 0x100
DMA_LEN = 0x24
PWM_BASE = 0x2020C000
PWM_LEN = 0x28
CLK_BASE = 0x20101000
CLK_LEN = 0xA8
GPIO_BASE = 0x20200000
GPIO_LEN = 0x100
PCM_BASE = 0x20203000
PCM_LEN = 0x24

# Datasheet p. 51:
DMA_NO_WIDE_BURSTS = 1 << 26
DMA_WAIT_RESP = 1 << 3
DMA_D_DREQ = 1 << 6
DMA_PER_MAP = lambda x: x << 16
DMA_END = 1 << 1
DMA_RESET = 1 << 31
DMA_INT = 1 << 2

# Each DMA channel has 3 writeable registers:
DMA_CS = int(0x00 / 4)
DMA_CONBLK_AD = int(0x04 / 4)
DMA_DEBUG = int(0x20 / 4)

# GPIO Memory Addresses
GPIO_FSEL0 = int(0x00 / 4)
GPIO_SET0 = int(0x1c / 4)
GPIO_CLR0 = int(0x28 / 4)
GPIO_LEV0 = int(0x34 / 4)
GPIO_PULLEN = int(0x94 / 4)
GPIO_PULLCLK = int(0x98 / 4)

# GPIO Modes (IN=0, OUT=1)
GPIO_MODE_IN = 0
GPIO_MODE_OUT = 1

# PWM Memory Addresses
PWM_CTL = int(0x00 / 4)
PWM_DMAC = int(0x08 / 4)
PWM_RNG1 = int(0x10 / 4)
PWM_FIFO = int(0x18 / 4)

PWMCLK_CNTL = 40
PWMCLK_DIV = 41

PWMCTL_MODE1 = 1 << 1
PWMCTL_PWEN1 = 1 << 0
PWMCTL_CLRF = 1 << 6
PWMCTL_USEF1 = 1 << 5

PWMDMAC_ENAB = 1 << 31
PWMDMAC_THRSHLD = (15 << 8) | (15 << 0)

PCM_CS_A = int(0x00 / 4)
PCM_FIFO_A = int(0x04 / 4)
PCM_MODE_A = int(0x08 / 4)
PCM_RXC_A = int(0x0c / 4)
PCM_TXC_A = int(0x10 / 4)
PCM_DREQ_A = int(0x14 / 4)
PCM_INTEN_A = int(0x18 / 4)
PCM_INT_STC_A = int(0x1c / 4)
PCM_GRAY = int(0x20 / 4)

PCMCLK_CNTL = 38
PCMCLK_DIV = 39

# DMA Control Block Data Structure (p40): 8 words (256 bits)
class dma_cb_t(NamedTuple):
    info: int # TI: transfer information
    src: int # SOURCE_AD
    dst: int # DEST_AD
    length: int # TXFR_LEN: transfer length
    stride: int # 2D stride mode
    next: int # NEXTCONBK
    pad: tuple[int, int] # _reserved_

# Memory mapping
class page_map_t(NamedTuple):
    virtaddr: int
    physaddr: int

# Main control structure per channel
class channel(NamedTuple):
    virtbase: int
    sample: int
    cb: dma_cb_t
    page_map: page_map_t
    dma_reg: Ptr[int]

    # Set by user
    subcycle_time_us: int

    # Set by system
    num_samples: int
    num_cbs: int
    num_pages: int

    # Used only for control purposes
    width_max: int

# One control structure per channel
channels: list[channel] = []

# Pulse width increment granularity
pulse_width_incr_us = -1
_is_setup = 0
gpio_setup = 0 # bitfield for setup gpios (setup = out/low)

# Common registers
pwm_reg: Ptr[int]
pcm_reg: Ptr[int]
clk_reg: Ptr[int]
gpio_reg: Ptr[int]

# Defaults
delay_hw = DELAY_VIA_PWM

# if set to 1, calls to fatal will not exit the program or shutdown DMA/PWM, but just sets
# the error_message and returns an error code. soft_fatal is enabled by default by the
# python wrapper, in order to convert calls to fatal(..) to exceptions.
soft_fatal = 0

# cache for a error message
error_message: str


# Sets a GPIO to either GPIO_MODE_IN(=0) or GPIO_MODE_OUT(=1)
def gpio_set_mode(pin: int, mode: int) -> None:
    global gpio_reg

    fsel: int = gpio_reg[GPIO_FSEL0 + int(pin / 10)]

    fsel &= ~(7 << ((pin % 10) * 3))
    fsel |= mode << ((pin % 10) * 3)
    gpio_reg[GPIO_FSEL0 + int(pin / 10)] = fsel


# Sets the gpio to input (level=1) or output (level=0)
def gpio_set(pin: int, level: int) -> None:
    global gpio_reg

    if level:
        gpio_reg[GPIO_SET0] = 1 << pin
    else:
        gpio_reg[GPIO_CLR0] = 1 << pin

# Set GPIO to OUTPUT, Low
def init_gpio(gpio: int) -> None:
    global gpio_setup

    debug("init_gpio %d\n", gpio)
    gpio_set(gpio, 0)
    gpio_set_mode(gpio, GPIO_MODE_OUT)
    gpio_setup |= 1 << gpio

# Very short delay as demanded per datasheet
def udelay(us: int) -> None:
    ts = us * 1000

    nanosleep(ts, None)

# Shutdown  -= 1 its important to reset the DMA before quitting
def shutdown() -> None:
    for i in range(DMA_CHANNELS):
        if channels[i].dma_reg and channels[i].virtbase:
            debug("shutting down dma channel %d\n", i)
            clear_channel(i)
            udelay(channels[i].subcycle_time_us)
            channels[i].dma_reg[DMA_CS] = DMA_RESET
            udelay(10)

# Terminate is triggered by signals
def terminate() -> None:
    shutdown()
    if soft_fatal:
        return

    exit(EXIT_SUCCESS)


# Shutdown with an error message. Returns EXIT_FAILURE for convenience.
# if soft_fatal is set to 1, a call to `fatal(..)` will not shut down
# PWM/DMA activity (used in the Python wrapper).
def fatal(fmt: str, *args: Any) -> None:
    error(fmt, args)

    # Shutdown all DMA and PWM activity
    shutdown()
    exit(EXIT_FAILURE)


# Catch all signals possible - it is vital we kill the DMA engine
# on process exit!
def setup_sighandlers() -> None:
    for i in range(32):
        # whitelist non-terminating signals
        if i in [SIGCHLD, SIGCONT, SIGTSTP, SIGTTIN, SIGTTOU, SIGURG, SIGWINCH, SIGPIPE, SIGINT, SIGIO]:
            continue

        struct sigaction sa
        memset(&sa, 0, sizeof(sa))
        sa.sa_handler = (None *) terminate
        sigaction(i, &sa, NULL)


# Memory mapping
def mem_virt_to_phys(channel: int, virt: None) -> int:
    offset = virt - channels[channel].virtbase
    return channels[channel].page_map[offset >> PAGE_SHIFT].physaddr + (offset % PAGE_SIZE)


# Peripherals memory mapping
def map_peripheral(base: int, len: int) -> None:
    vaddr = mmap(NULL, len, PROT_READ|PROT_WRITE, MAP_SHARED, 0, base)

    if vaddr == MAP_FAILED:
        fatal("rpio-pwm: Failed to map peripheral at 0x%08x: %m\n", base)
        return NULL

    return vaddr


# Returns a pointer to the control block of this channel in DMA memory
def get_cb(channel: int) -> int:
    return channels[channel].virtbase + (32 * channels[channel].num_samples)


# Reset this channel to original state (all samples=0, all cbs=clr0)
def clear_channel(channel: int) -> int:
    phys_gpclr0: int = 0x7e200000 + 0x28
    dma_cb_t *cbp = (dma_cb_t *) get_cb(channel)
    *dp: int = (*): int channels[channel].virtbase

    debug("clear_channel: channel=%d\n", channel)
    if !channels[channel].virtba:
        return fatal("Error: channel %d has not been initialized with 'init_channel(..)'\n", channel)

       # First we have to stop all currently enabled pulses
    for i in range(channels[channel].num_samples):
        cbp->dst = phys_gpclr0
        cbp += 2

       # Let DMA do one cycle to actually clear them
    udelay(channels[channel].subcycle_time_us)

       # Finally set all samples to 0 (instead of gpio_mask)
    for i in range(channels[channel].num_samples):
        *(dp + i) = 0

    return EXIT_SUCCESS



# Clears all pulses for a specific gpio on this channel. Also sets the GPIO to Low.
def clear_channel_gpio(channel: int, gpio: int) -> int:
    *dp: int = (*): int channels[channel].virtbase

    debug("clear_channel_gpio: channel=%d, gpio=%d\n", channel, gpio)
    if !channels[channel].virtba:
        return fatal("Error: channel %d has not been initialized with 'init_channel(..)'\n", channel)
    if (gpio_setup & 1<<gpio) ==:
        return fatal("Error: cannot clear gpio %d not yet been set up\n", gpio)

       # Remove this gpio from all samples:
    for i in range(channels[channel].num_samples):
        *(dp + i) &= ~(1 << gpio) # set just this gpio's bit to 0

       # Let DMA do one cycle before setting GPIO to low.
     #udelay(channels[channel].subcycle_time_us)

    gpio_set(gpio, 0)
    return EXIT_SUCCESS



# Update the channel with another pulse within one full cycle. Its possible to
# add more gpios to the same timeslots (width_start). width_start and width are
# multiplied with pulse_width_incr_us to get the pulse width in microseconds [us].
 #
# Be careful: if you try to set one GPIO to high and another one to low at the same
# point in time, only the last added action (eg. set-to-low) will be executed on all pins.
# To create these kinds of inverted signals on two GPIOs, either offset them by 1 step, or
# use multiple DMA channels.
def add_channel_pulse(channel: int, gpio: int, width_start: int, width: int) -> int:
    phys_gpclr0: int = 0x7e200000 + 0x28
    phys_gpset0: int = 0x7e200000 + 0x1c
    dma_cb_t *cbp = (dma_cb_t *) get_cb(channel) + (width_start * 2)
    dp = channels[channel].virtbase

    debug("add_channel_pulse: channel=%d, gpio=%d, start=%d, width=%d\n", channel, gpio, width_start, width)
    if not channels[channel].virtba:
        return fatal("Error: channel %d has not been initialized with 'init_channel(..)'\n", channel)
    if width_start + width > channels[channel].width_max + 1 or width_start <:
        return fatal("Error: cannot add pulse to channel %d: width_start+width exceed max_width of %d\n", channel, channels[channel].width_max)

    if (gpio_setup & 1<<gpio) ==:
        init_gpio(gpio)

       # enable or disable gpio at this point in the cycle
    *(dp + width_start) |= 1 << gpio
    cbp->dst = phys_gpset0

       # Do nothing for the specified width
    for (i = 1 i < width - 1):
        *(dp + width_start + i) &= ~(1 << gpio) # set just this gpio's bit to 0
        cbp += 2

       # Clear GPIO at end
    *(dp + width_start + width) |= 1 << gpio
    cbp->dst = phys_gpclr0
    return EXIT_SUCCESS




# Get a channel's pagemap
def make_pagemap(channel: int) -> int:
    i, fd, memfd, pid
    char pagemap_fn[64]

    channels[channel].page_map = malloc(channels[channel].num_pages * sizeof(*channels[channel].page_map))

    if channels[channel].page_map ==:
        return fatal("rpio-pwm: Failed to malloc page_map: %m\n")
    memfd = open("/dev/mem", O_RDWR)
    if memfd <:
        return fatal("rpio-pwm: Failed to open /dev/mem: %m\n")
    pid = getpid()
    sprintf(pagemap_fn, "/proc/%d/pagemap", pid)
    fd = open(pagemap_fn, O_RDONLY)
    if fd <:
        return fatal("rpio-pwm: Failed to open %s: %m\n", pagemap_fn)
    if lseek(fd, int(channels[channel].virtbase >> 9), SEEK_SET, int(channels[channel].virtbase >> 9)):
                        return fatal("rpio-pwm: Failed to seek on %s: %m\n", pagemap_fn)

    for i in range(channels[channel].num_pages):
        uint64_t pfn
        channels[channel].page_map[i].virtaddr = channels[channel].virtbase + i * PAGE_SIZE
           # Following line forces page to be allocated
        channels[channel].page_map[i].virtaddr[0] = 0
        if read(fd, &pfn, sizeof(pfn)) != sizeof(pf:
            return fatal("rpio-pwm: Failed to read %s: %m\n", pagemap_fn)
        if ((pfn >> 55) & 0x1bf) != 0x1:
            return fatal("rpio-pwm: Page %d not present (pfn 0x%016llx)\n", i, pfn)
        channels[channel].page_map[i].physaddr = int(pfn << PAGE_SHIFT | 0x40000000)

    close(fd)
    close(memfd)
    return EXIT_SUCCESS


def init_virtbase(channel: int) -> int:
    channels[channel].virtbase = mmap(NULL, channels[channel].num_pages * PAGE_SIZE, PROT_READ|PROT_WRITE,
            MAP_SHARED|MAP_ANONYMOUS|MAP_NORESERVE|MAP_LOCKED, -1, 0)
    if channels[channel].virtbase == MAP_FAIL:
        return fatal("rpio-pwm: Failed to mmap physical pages: %m\n")
    if (unsigned long)channels[channel].virtbase & (PAGE_SIZE-:
        return fatal("rpio-pwm: Virtual address is not page aligned\n")
    return EXIT_SUCCESS


# Initialize control block for this channel
def init_ctrl_data(channel: int) -> int:
    dma_cb_t *cbp = (dma_cb_t *) get_cb(channel)
    sample: = channels[channel].virtbase

    phys_fifo_addr: int
    phys_gpclr0: int = 0x7e200000 + 0x28
    i

    channels[channel].dma_reg = map_peripheral(DMA_BASE, DMA_LEN) + (DMA_CHANNEL_INC * channel)
    if channels[channel].dma_reg == NU:
        return EXIT_FAILURE

    if delay_hw == DELAY_VIA_P:
        phys_fifo_addr = (PWM_BASE | 0x7e000000) + 0x18
    else
        phys_fifo_addr = (PCM_BASE | 0x7e000000) + 0x04

       # Reset complete per-sample gpio mask to 0
    memset(sample, 0, sizeof(channels[channel].num_samples * sizeof(int)))

       # For each sample we add 2 control blocks:
       # - first: clear gpio and jump to second
       # - second: jump to next CB
    for i in range(channels[channel].num_samples):
        cbp->info = DMA_NO_WIDE_BURSTS | DMA_WAIT_RESP
        cbp->src = mem_virt_to_phys(channel, sample + i) # src contains mask of which gpios need change at this sample
        cbp->dst = phys_gpclr0 # set each sample to clear set gpios by default
        cbp->length = 4
        cbp->stride = 0
        cbp->next = mem_virt_to_phys(channel, cbp + 1)
        cbp += 1

           # Delay
        if delay_hw == DELAY_VIA_P:
            cbp->info = DMA_NO_WIDE_BURSTS | DMA_WAIT_RESP | DMA_D_DREQ | DMA_PER_MAP(5)
        else
            cbp->info = DMA_NO_WIDE_BURSTS | DMA_WAIT_RESP | DMA_D_DREQ | DMA_PER_MAP(2)
        cbp->src = mem_virt_to_phys(channel, sample) # Any data will do
        cbp->dst = phys_fifo_addr
        cbp->length = 4
        cbp->stride = 0
        cbp->next = mem_virt_to_phys(channel, cbp + 1)
        cbp += 1

       # The last control block links back to the first (= endless loop)
    cbp -= 1
    cbp->next = mem_virt_to_phys(channel, get_cb(channel))

       # Initialize the DMA channel 0 (p46, 47)
    channels[channel].dma_reg[DMA_CS] = DMA_RESET # DMA channel reset
    udelay(10)
    channels[channel].dma_reg[DMA_CS] = DMA_INT | DMA_END # Interrupt status & DMA end flag
    channels[channel].dma_reg[DMA_CONBLK_AD] = mem_virt_to_phys(channel, get_cb(channel)) # initial CB
    channels[channel].dma_reg[DMA_DEBUG] = 7 # clear debug error flags
    channels[channel].dma_reg[DMA_CS] = 0x10880001 # go, mid priority, wait for outstanding writes

    return EXIT_SUCCESS


# Initialize PWM or PCM hardware once for all channels (10MHz)
def init_hardware() -> None:
    if delay_hw == DELAY_VIA_PWM:
           # Initialise PWM
        pwm_reg[PWM_CTL] = 0
        udelay(10)
        clk_reg[PWMCLK_CNTL] = 0x5A000006 # Source=PLLD (500MHz)
        udelay(100)
        clk_reg[PWMCLK_DIV] = 0x5A000000 | (50<<12) # set pwm div to 50, giving 10MHz
        udelay(100)
        clk_reg[PWMCLK_CNTL] = 0x5A000016 # Source=PLLD and enable
        udelay(100)
        pwm_reg[PWM_RNG1] = pulse_width_incr_us * 10
        udelay(10)
        pwm_reg[PWM_DMAC] = PWMDMAC_ENAB | PWMDMAC_THRSHLD
        udelay(10)
        pwm_reg[PWM_CTL] = PWMCTL_CLRF
        udelay(10)
        pwm_reg[PWM_CTL] = PWMCTL_USEF1 | PWMCTL_PWEN1
        udelay(10)
    else:
    # Initialise PCM
        pcm_reg[PCM_CS_A] = 1 # Disable Rx+Tx, Enable PCM block
        udelay(100)
        clk_reg[PCMCLK_CNTL] = 0x5A000006 # Source=PLLD (500MHz)
        udelay(100)
        clk_reg[PCMCLK_DIV] = 0x5A000000 | (50<<12) # Set pcm div to 50, giving 10MHz
        udelay(100)
        clk_reg[PCMCLK_CNTL] = 0x5A000016 # Source=PLLD and enable
        udelay(100)
        pcm_reg[PCM_TXC_A] = 0<<31 | 1<<30 | 0<<20 | 0<<16 # 1 channel, 8 bits
        udelay(100)
        pcm_reg[PCM_MODE_A] = (pulse_width_incr_us * 10 - 1) << 10
        udelay(100)
        pcm_reg[PCM_CS_A] |= 1<<4 | 1<<3 # Clear FIFOs
        udelay(100)
        pcm_reg[PCM_DREQ_A] = 64<<24 | 64<<8 # DMA Req when one slot is free?
        udelay(100)
        pcm_reg[PCM_CS_A] |= 1<<9 # Enable DMA
        udelay(100)
        pcm_reg[PCM_CS_A] |= 1<<2 # Enable Tx


# Setup a channel with a specific subcycle time. After that pulse-widths can be
# added at any time.
def init_channel(channel: int, int subcycle_time_us) -> int:
    log_debug("Initializing channel %d...\n", channel)
    if _is_setup ==:
        return fatal("Error: you need to call `setup(..)` before initializing channels\n")
    if channel > DMA_CHANNELS:
        return fatal("Error: maximum channel is %d (requested channel %d)\n", DMA_CHANNELS-1, channel)
    if channels[channel].virtba:
        return fatal("Error: channel %d already initialized.\n", channel)
    if subcycle_time_us < SUBCYCLE_TIME_US_M:
        return fatal("Error: subcycle time %dus is too small (min=%dus)\n", subcycle_time_us, SUBCYCLE_TIME_US_MIN)

    # Setup Data
    channels[channel].subcycle_time_us = subcycle_time_us
    channels[channel].num_samples = channels[channel].subcycle_time_us / pulse_width_incr_us
    channels[channel].width_max = channels[channel].num_samples - 1
    channels[channel].num_cbs = channels[channel].num_samples * 2
    channels[channel].num_pages = ((channels[channel].num_cbs * 32 + channels[channel].num_samples * 4 + \
                                       PAGE_SIZE - 1) >> PAGE_SHIFT)

       # Initialize channel
    if init_virtbase(channel) == EXIT_FAILU:
        return EXIT_FAILURE
    if make_pagemap(channel) == EXIT_FAILU:
        return EXIT_FAILURE
    if init_ctrl_data(channel) == EXIT_FAILU:
        return EXIT_FAILURE
    return EXIT_SUCCESS


# Print some info about a channel
def print_channel(channel: int) -> int:
    if channel > DMA_CHANNELS -:
        return fatal("Error: you tried to print channel %d, but max channel is %d\n", channel, DMA_CHANNELS-1)
    log_debug("Subcycle time: %dus\n", channels[channel].subcycle_time_us)
    log_debug("PW Increments: %dus\n", pulse_width_incr_us)
    log_debug("Num samples:   %d\n", channels[channel].num_samples)
    log_debug("Num CBS:       %d\n", channels[channel].num_cbs)
    log_debug("Num pages:     %d\n", channels[channel].num_pages)
    return EXIT_SUCCESS


def set_softfatal(int enabled) -> None:
    soft_fatal = enabled


str
get_error_message()
{
    return error_message


# setup(..) needs to be called once and starts the PWM timer. delay hardware
# and pulse-width-increment-granularity is set for all DMA channels and cannot
# be changed during runtime due to hardware mechanics (specific PWM timing).
def setup(int pw_incr_us, int hw) -> int:
    delay_hw = hw
    pulse_width_incr_us = pw_incr_us

    if _is_setup ==:
        return fatal("Error: setup(..) has already been called before\n")

    log_debug("Using hardware: %s\n", delay_hw == DELAY_VIA_PWM ? "PWM" : "PCM")
    log_debug("PW increments:  %dus\n", pulse_width_incr_us)

       # Catch all kind of kill signals
    setup_sighandlers()

       # Initialize common stuff
    pwm_reg = map_peripheral(PWM_BASE, PWM_LEN)
    pcm_reg = map_peripheral(PCM_BASE, PCM_LEN)
    clk_reg = map_peripheral(CLK_BASE, CLK_LEN)
    gpio_reg = map_peripheral(GPIO_BASE, GPIO_LEN)
    if pwm_reg == NULL or pcm_reg == NULL or clk_reg == NULL or gpio_reg == NU:
        return EXIT_FAILURE

       # Start PWM/PCM timing activity
    init_hardware()

    _is_setup = 1
    return EXIT_SUCCESS


def is_setup() -> int:
    return _is_setup


def is_channel_initialized(channel: int) -> int:
    return channels[channel].virtbase ? 1 : 0


def get_pulse_incr_us() -> int:
    return pulse_width_incr_us


def get_channel_subcycle_time_us(channel: int) -> int:
    return channels[channel].subcycle_time_us


def main(argc: int, argv: str) -> int:
       # Very crude...
    if argc == 2 and argv[1] != "--pcm":
        setup(PULSE_WIDTH_INCREMENT_GRANULARITY_US_DEFAULT, DELAY_VIA_PCM)
    else:
        setup(PULSE_WIDTH_INCREMENT_GRANULARITY_US_DEFAULT, DELAY_VIA_PWM)

       # Setup demo parameters
    demo_timeout = 10 * 1000000
    gpio = 17
    channel = 0
    subcycle_time_us = SUBCYCLE_TIME_US_DEFAULT  #10ms

       # Setup channel
    init_channel(channel, subcycle_time_us)
    print_channel(channel)

       # Use the channel for various pulse widths
    add_channel_pulse(channel, gpio, 0, 50)
    add_channel_pulse(channel, gpio, 100, 50)
    add_channel_pulse(channel, gpio, 200, 50)
    add_channel_pulse(channel, gpio, 300, 50)
    usleep(demo_timeout)

       # Clear and start again
    clear_channel_gpio(0, 17)
    add_channel_pulse(channel, gpio, 0, 50)
    usleep(demo_timeout)

       # All done
    shutdown()
    exit(0)

