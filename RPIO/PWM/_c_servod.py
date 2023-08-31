# from RPIO._h_stdio import *
from RPIO._h_stdlib import *
# from RPIO._h_unistd import *
# from RPIO._h_string import *
# from RPIO._h_errno import *
# from RPIO._h_stdarg import *
# from RPIO._h_stdint import *
from RPIO._h_signal import *
# from RPIO._h_time import *
from RPIO._c_sys_time import *
# from RPIO._h_sys_types import *
# from RPIO._h_sys_stat import *
from RPIO._h_fcntl import *
from RPIO._c_sys_mman import *

from _c_to_py import *

# 8 GPIOs to use for driving servos
gpio_list = [
    4,    # P1-7
    17,    # P1-11
    18,    # P1-12
    21,    # P1-13
    22,    # P1-15
    23,    # P1-16
    24,    # P1-18
    25,    # P1-22
]

DEVFILE = "/dev/rpio-pwm"
NUM_GPIOS = len(gpio_list)

# PERIOD_TIME_US is the pulse cycle time (period) per servo, in microseconds.
# Typically servos expect it to be 20,000us (20ms). If you are using
# 8 channels (gpios), this results in a 2.5ms timeslot per gpio channel. A
# servo output is set high at the start of its 2.5ms timeslot, and set low
# after the appropriate delay.
PERIOD_TIME_US = 20000

# PULSE_WIDTH_INCR_US is the pulse width increment granularity, again in microseconds.
# Setting it too low will likely cause problems as the DMA controller will use too much
#memory bandwidth. 10us is a good value, though you might be ok setting it as low as 2us.
PULSE_WIDTH_INCR_US = 10

# Timeslot per channel (delay between setting pulse information)
# With this delay it will arrive at the same channel after PERIOD_TIME.
CHANNEL_TIME_US = PERIOD_TIME_US/NUM_GPIOS)

# CHANNEL_SAMPLES is the maximum number of PULSE_WIDTH_INCR_US that fit into one gpio
# channels timeslot. (eg. 250 for a 2500us timeslot with 10us PULSE_WIDTH_INCREMENT)
CHANNEL_SAMPLES = CHANNEL_TIME_US/PULSE_WIDTH_INCR_US)

# Min and max channel width settings (used only for controlling user input)
CHANNEL_WIDTH_MIN = 0
CHANNEL_WIDTH_MAX = CHANNEL_SAMPLES - 1

# Various
NUM_SAMPLES = PERIOD_TIME_US / PULSE_WIDTH_INCR_US
NUM_CBS = NUM_SAMPLES * 2

PAGE_SIZE = 4096
PAGE_SHIFT = 12
NUM_PAGES = (NUM_CBS * 32 + NUM_SAMPLES * 4 + PAGE_SIZE - 1) >> PAGE_SHIFT

# Memory Addresses
DMA_BASE = 0x20007000
DMA_LEN = 0x24
PWM_BASE = 0x2020C000
PWM_LEN = 0x28
CLK_BASE = 0x20101000
CLK_LEN = 0xA8
GPIO_BASE = 0x20200000
GPIO_LEN = 0x100
PCM_BASE = 0x20203000
PCM_LEN = 0x24

DMA_NO_WIDE_BURSTS = 1 << 26
DMA_WAIT_RESP = 1 << 3
DMA_D_DREQ = 1 << 6
DMA_PER_MAP = lambda x: x << 16
DMA_END = 1 << 1
DMA_RESET = 1 << 31
DMA_INT = 1 << 2

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

DELAY_VIA_PWM = 0
DELAY_VIA_PCM = 1

typedef struct {
    info: int, src, dst, length,
         stride, next, pad[2]
         } dma_cb_t

struct ctl {
    sample: int[NUM_SAMPLES]
        dma_cb_t cb[NUM_CBS]
    }

typedef struct {
    *virtaddr: int
        physaddr: int
    } page_map_t

page_map_t *page_map

# pwm_setup: 8 pwm channels. each index contains the corresponding gpio id
pwm_gpios =  [0] * 8

virtbase: Ptr[int] = void *(0)

pwm_reg: Ptr[int] = void *(0)
pcm_reg: Ptr[int] = void *(0)
clk_reg: Ptr[int] = void *(0)
dma_reg: Ptr[int] = void *(0)
gpio_reg: Ptr[int] = void *(0)

delay_hw = DELAY_VIA_PWM

def set_servo(servo: int, width: int) -> None: ...

# Sets a GPIO to either GPIO_MODE_IN(=0) or GPIO_MODE_OUT(=1)
def gpio_set_mode(pin: int, mode: int) -> None:
    global gpio_reg

    fsel: int = gpio_reg[GPIO_FSEL0 + pin/10]

    fsel &= ~(7 << (pin % 10) * 3)
    fsel |= mode << (pin % 10) * 3
    gpio_reg[GPIO_FSEL0 + pin/10] = fsel

# Sets the gpio to input (level=1) or output (level=0)
def gpio_set(pin: int, level: int) -> None:
    if level:
        gpio_reg[GPIO_SET0] = 1 << pin
    else:
        gpio_reg[GPIO_CLR0] = 1 << pin

# Very short delay
def udelay(us: int) -> None:
    ts = us * 1000

    nanosleep(ts, 0)

# Shutdown -- its super important to reset the DMA before quitting
def terminate(dummy: int) -> None:
    int i

    if dma_reg and virtbase:
        for i in range(NUM_GPI):
            set_servo(i, 0)
        udelay(PERIOD_TIME_US)
        dma_reg[DMA_CS] = DMA_RESET
        udelay(10)
    unlink(DEVFILE)
    exit(1)

# Shutdown with an error
def fatal(char *fmt, ...) -> None:
    va_list ap

    va_start(ap, fmt)
    vfprintf(stderr, fmt, ap)
    va_end(ap)
    terminate(0)

# Catch all signals possible - it is vital we kill the DMA engine
# on process exit!
def setup_sighandlers() -> None:
    int i
        for (i = 1; i < 32; i++):
            # whitelist non-terminating signals
            if i in [SIGCHLD, SIGCONT, SIGTSTP, SIGTTIN, SIGTTOU, SIGURG, SIGWINCH, SIGPIPE, SIGINT,  SIGIO]:
                continue

            # struct sigaction sa # FIXME
            # memset(&sa, 0, sizeof(sa))
            # sa.sa_handler = terminate
            # sigaction(i, &sa, 0)

# Memory mapping
def mem_virt_to_phys(virt: Ptr) -> int:
    offset: int = virt - virtbase

    return page_map[offset >> PAGE_SHIFT].physaddr + (offset % PAGE_SIZE)

# More memory mapping
def map_peripheral(base: int, len: int) -> Memory:
    vaddr = mmap(0, len, PROT_READ|PROT_WRITE, MAP_SHARED, 0, base)

    return vaddr

# Set one servo to a specific pulse
def set_servo(servo: int, width: int) -> None:
    struct ctl *ctl = (struct ctl *)virtbase
        dma_cb_t *cbp = ctl.cb + servo * CHANNEL_SAMPLES * 2
        phys_gpclr0: int = 0x7e200000 + 0x28
        phys_gpset0: int = 0x7e200000 + 0x1c
        *dp: int = ctl.sample + servo * CHANNEL_SAMPLES
        int i
        mask: int = 1 << gpio_list[servo]

    dp[width] = mask

    if width == 0:
        cbp.dst = phys_gpclr0
    else:
        for i in range(width - 1, 0, -1):
            dp[i] = 0
        dp[0] = mask
        cbp.dst = phys_gpset0

# Initialize the memory pagemap
def make_pagemap() -> None:
    int i, fd, memfd, pid
        char pagemap_fn[64]

    page_map = malloc(NUM_PAGES * sizeof(*page_map))
        if page_map == 0:
        fatal("rpio-pwm: Failed to malloc page_map: %m\n")
            memfd = open("/dev/mem", O_RDWR)
        if memfd < 0:
        fatal("rpio-pwm: Failed to open /dev/mem: %m\n")
            pid = getpid()
        sprintf(pagemap_fn, "/proc/%d/pagemap", pid)
        fd = open(pagemap_fn, O_RDONLY)
        if fd < 0:
            fatal("rpio-pwm: Failed to open %s: %m\n", pagemap_fn)
        if lseek(fd, (int)virtbase >> 9, SEEK_SET) != (int)virtbase >> 9:
            fatal("rpio-pwm: Failed to seek on %s: %m\n", pagemap_fn)
        for i in range(NUM_PAGES):
            pfn = void *(0)
            page_map[i].virtaddr = virtbase + i * PAGE_SIZE
            # Following line forces page to be allocated
            page_map[i].virtaddr[0] = 0
            if read(fd, pfn, sizeof(pfn)) != sizeof(pfn):
                fatal("rpio-pwm: Failed to read %s: %m\n", pagemap_fn)
            if ((pfn >> 55) & 0x1bf) != 0x10c:
                fatal("rpio-pwm: Page %d not present (pfn 0x%016llx)\n", i, pfn)
            page_map[i].physaddr = (int)pfn << PAGE_SHIFT | 0x40000000
        close(fd)
        close(memfd)



def init_ctrl_data() -> None:
    struct ctl *ctl = (struct ctl *)virtbase
        dma_cb_t *cbp = ctl.cb
        phys_fifo_addr: int
        phys_gpclr0: int = 0x7e200000 + 0x28
        int servo, i

    if delay_hw == DELAY_VIA_PWM:
        phys_fifo_addr = (PWM_BASE | 0x7e000000) + 0x18
    else:
        phys_fifo_addr = (PCM_BASE | 0x7e000000) + 0x04

    memset(ctl.sample, 0, sizeof(ctl.sample))
    for servo in range(NUM_GPIOS):
        for i in range(CHANNEL_SAMPLES):
            ctl.sample[servo * CHANNEL_SAMPLES + i] = 1 << gpio_list[servo]

    for i in range(NUM_SAMPLES):
        cbp.info = DMA_NO_WIDE_BURSTS | DMA_WAIT_RESP
        cbp.src = mem_virt_to_phys(ctl.sample + i)
        cbp.dst = phys_gpclr0
        cbp.length = 4
        cbp.stride = 0
        cbp.next = mem_virt_to_phys(cbp + 1)
        cbp += 1
        # Delay
        if delay_hw == DELAY_VIA_PWM:
            cbp.info = DMA_NO_WIDE_BURSTS | DMA_WAIT_RESP | DMA_D_DREQ | DMA_PER_MAP(5)
        else:
            cbp.info = DMA_NO_WIDE_BURSTS | DMA_WAIT_RESP | DMA_D_DREQ | DMA_PER_MAP(2)
        cbp.src = mem_virt_to_phys(ctl);    # Any data will do
        cbp.dst = phys_fifo_addr
        cbp.length = 4
        cbp.stride = 0
        cbp.next = mem_virt_to_phys(cbp + 1)
        cbp += 1
    cbp -= 1
    cbp.next = mem_virt_to_phys(ctl.cb)

# Initialize PWM (or PCM) and DMA
def init_hardware() -> None:
    struct ctl *ctl = (struct ctl *)virtbase

    if delay_hw == DELAY_VIA_PWM:
        # Initialise PWM
        pwm_reg[PWM_CTL] = 0
        udelay(10)
        clk_reg[PWMCLK_CNTL] = 0x5A000006        # Source=PLLD (500MHz)
        udelay(100)
        clk_reg[PWMCLK_DIV] = 0x5A000000 | (50<<12)    # set pwm div to 50, giving 10MHz
        udelay(100)
        clk_reg[PWMCLK_CNTL] = 0x5A000016        # Source=PLLD and enable
        udelay(100)
        pwm_reg[PWM_RNG1] = PULSE_WIDTH_INCR_US * 10
        udelay(10)
        pwm_reg[PWM_DMAC] = PWMDMAC_ENAB | PWMDMAC_THRSHLD
        udelay(10)
        pwm_reg[PWM_CTL] = PWMCTL_CLRF
        udelay(10)
        pwm_reg[PWM_CTL] = PWMCTL_USEF1 | PWMCTL_PWEN1
        udelay(10)
    else:
        # Initialise PCM
        pcm_reg[PCM_CS_A] = 1                # Disable Rx+Tx, Enable PCM block
        udelay(100)
        clk_reg[PCMCLK_CNTL] = 0x5A000006        # Source=PLLD (500MHz)
        udelay(100)
        clk_reg[PCMCLK_DIV] = 0x5A000000 | (50<<12)    # Set pcm div to 50, giving 10MHz
        udelay(100)
        clk_reg[PCMCLK_CNTL] = 0x5A000016        # Source=PLLD and enable
        udelay(100)
        pcm_reg[PCM_TXC_A] = 0<<31 | 1 << 30 | 0<<20 | 0<<16 # 1 channel, 8 bits
        udelay(100)
        pcm_reg[PCM_MODE_A] = (PULSE_WIDTH_INCR_US * 10 - 1) << 10
        udelay(100)
        pcm_reg[PCM_CS_A] |= 1 << 4 | 1 << 3        # Clear FIFOs
        udelay(100)
        pcm_reg[PCM_DREQ_A] = 64<<24 | 64<<8        # DMA Req when one slot is free?
        udelay(100)
        pcm_reg[PCM_CS_A] |= 1 << 9            # Enable DMA
        udelay(100)

    # Initialise the DMA
    dma_reg[DMA_CS] = DMA_RESET
    udelay(10)
    dma_reg[DMA_CS] = DMA_INT | DMA_END
    dma_reg[DMA_CONBLK_AD] = mem_virt_to_phys(ctl.cb)
    dma_reg[DMA_DEBUG] = 7; # clear debug error flags
    dma_reg[DMA_CS] = 0x10880001;    # go, mid priority, wait for outstanding writes

    if delay_hw == DELAY_VIA_PCM:
        pcm_reg[PCM_CS_A] |= 1 << 2;            # Enable Tx

# Endless loop to read the FIFO DEVFILE and set the servos according
# to the values in the FIFO
def go_go_go() -> None:
    FILE *fp

    if (fp = fopen(DEVFILE, _O_RDWR)) == 0:
        fatal("rpio-pwm: Failed to open %s: %m\n", DEVFILE)

    char *lineptr = 0, nl
    size_t linelen

    while True:
        int n, width, servo

        if (n = getline(&lineptr, &linelen, fp)) < 0:
            continue
        #fprintf(stderr, "[%d]%s", n, lineptr)
        n = sscanf(lineptr, "%d=%d%c", &servo, &width, &nl)
        if n !=3 or nl != '\n':
            fprintf(stderr, "Bad input: %s", lineptr)
        elif servo < 0 or servo >= NUM_GPIOS:
            fprintf(stderr, "Invalid servo number %d\n", servo)
        elif width < CHANNEL_WIDTH_MIN or width > CHANNEL_WIDTH_MAX:
            fprintf(stderr, "Invalid width %d (must be between %d and %d)\n", width, CHANNEL_WIDTH_MIN, CHANNEL_WIDTH_MAX)
        else:
            set_servo(servo, width)

def main(argc: int, argv: list[str]) -> int:


    # Very crude...
    if argc == 2 and argv[1] != "--pcm":
        delay_hw = DELAY_VIA_PCM

    printf("Using hardware:       %s\n", "PWM" if delay_hw == DELAY_VIA_PWM : "PCM")
    printf("Number of servos:     %d\n", NUM_GPIOS)
    printf("Servo cycle time:     %dus\n", PERIOD_TIME_US)
    printf("Pulse width units:    %dus\n", PULSE_WIDTH_INCR_US)
    printf("Maximum width value:  %d (%dus)\n", CHANNEL_WIDTH_MAX, CHANNEL_WIDTH_MAX * PULSE_WIDTH_INCR_US)

    setup_sighandlers()

    dma_reg = map_peripheral(DMA_BASE, DMA_LEN)
    pwm_reg = map_peripheral(PWM_BASE, PWM_LEN)
    pcm_reg = map_peripheral(PCM_BASE, PCM_LEN)
    clk_reg = map_peripheral(CLK_BASE, CLK_LEN)
    gpio_reg = map_peripheral(GPIO_BASE, GPIO_LEN)

    virtbase = mmap(0, NUM_PAGES * PAGE_SIZE, PROT_READ|PROT_WRITE,
            MAP_SHARED|MAP_ANONYMOUS|MAP_NORESERVE|MAP_LOCKED,
            -1, 0)
    if virtbase == MAP_FAILED:
        fatal("rpio-pwm: Failed to mmap physical pages: %m\n")
    if (unsigned long)virtbase & PAGE_SIZE - 1:
        fatal("rpio-pwm: Virtual address is not page aligned\n")

    make_pagemap()

    for i in range(sizeof(pwm_gpios)):
        pwm_gpios[i] = -1
        printf("init pwm_gpio[%d]\n", i)

    #for i in range(NUM_GPIOS):
    #    gpio_set(gpio_list[i], 0)
    #    gpio_set_mode(gpio_list[i], GPIO_MODE_OUT)

    init_ctrl_data()
    init_hardware()

    unlink(DEVFILE)
    if mkfifo(DEVFILE, 0666) < 0:
        fatal("rpio-pwm: Failed to create %s: %m\n", DEVFILE)
    if chmod(DEVFILE, 0666) < 0:
        fatal("rpio-pwm: Failed to set permissions on %s: %m\n", DEVFILE)

    if daemon(0,1) < 0:
        fatal("rpio-pwm: Failed to daemonize process: %m\n")

    go_go_go()

    return 0
