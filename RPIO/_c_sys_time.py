from RPIO._h_sys_time import *

from time import sleep

def nanosleep(ts: int, *args) -> None:
    sleep(ts / 1_000_000)