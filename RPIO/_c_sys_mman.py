from threading import Lock

from RPIO._h_sys_mman import *


MEM_LOCK = Lock()
MEM_ASSIGNED: "list[Memory]" = []

def mmap(addr: int, len: int, protection: int, flags: int, fildes: int, off: int) -> Memory:
    with MEM_LOCK:
        mem = Memory(addr, len, protection, flags, fildes, off)

        MEM_ASSIGNED.append(mem)

    return mem

def munmap(addr: int, len: int) -> int:
    with MEM_LOCK:
        output = 0

        for m in MEM_ASSIGNED:
            if m.addr <= addr < m.addr + len:
                if m.addr + m.__len__() > addr + len:
                    mmap(addr + len, m.addr + m.__len__() - addr, m.protection, m.flags, m.fildes, m.off)

                m = m[addr:addr+len]

                output = 1

    return output

def mprotect(addr:int, len: int, prot: int) -> int:
    return 0

def msync(addr: int, len: int, flags: int) -> int:
    return 0

def mlock(addr: int, len: int) -> int:
    return 0

def munlock(addr: int, len: int) -> int:
    return 0
