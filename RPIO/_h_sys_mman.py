from collections import UserList
from logging import debug

from typing import SupportsInt


defined = set(dir())


if "_WIN32_WINNT" not in defined: # Allow use of features specific to Windows XP or later.
    _WIN32_WINNT = 0x0501         # Change this to the appropriate value to target other versions of Windows.

PROT_NONE = 0
PROT_READ = 1
PROT_WRITE = 2
PROT_EXEC = 4

MAP_FILE = 0
MAP_SHARED = 1
MAP_PRIVATE = 2
MAP_TYPE = 0xf
MAP_FIXED = 0x10
MAP_ANONYMOUS = 0x20
MAP_ANON = MAP_ANONYMOUS

MAP_FAILED = -1

MS_ASYNC = 1
MS_SYNC = 2
MS_INVALIDATE = 4


class Memory(UserList[int]):
    def __init__(self, addr: int, len: int, protection: int, flags: int, fildes: int, off: int):
        debug(f"Assigning memory {addr:x}-{addr + len:x}...")

        self.data = [0] * len
        self.addr = addr
        self.protection = protection
        self.flags = flags
        self.fildes = fildes
        self.off = off

    def __getitem__(self, i: slice | SupportsInt):
        if isinstance(i, slice):
            j = slice(i.start, i.stop, i.step)

            i = i.start
        else:
            j = int(i)

        debug(f"Getting memory at {i:x}...")

        return self.data[j]

    def __setitem__(self, i: SupportsInt, item: int):
        j = int(i)

        debug(f"Setting memory ar {i:x}...")

        self.data[j] = item


def mmap(addr: int, len: int, protection: int, flags: int, fildes: int, off: int) -> Memory: ...

def munmap(addr: int, len: int) -> int: ...

def mprotect(addr:int, len: int, prot: int) -> int: ...

def msync(addr: int, len: int, flags: int) -> int: ...

def mlock(addr: int, len: int) -> int: ...

def munlock(addr: int, len: int) -> int: ...
