"""
Mock library to debug on windows, etc.
"""

from logging import debug
from time import sleep
from io import FileIO


EPOLLERR = 1
EPOLLHUP = 2
EPOLLIN = 4
EPOLLPRI = 8


class Epoll:
    def poll(self, timeout: int) -> list[tuple[int, int]]: # fd, event
        debug(f"polling")

        sleep(timeout)

        return [(0, 0)]

    def register(self, fd: int, mode: int) -> None:
        debug(f"registered listener to fd {fd} with mode {mode}.")

    def unregister(self, fd: int) -> None:
        debug(f"unregistred listner to fd {fd}.")


def epoll() -> Epoll:
    return Epoll()