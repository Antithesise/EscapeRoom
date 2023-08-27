from RPIO._h_corecrt import *

from typing import NewType


defined = set(dir())


NSIG = 33  # maximum signal number + 1

# Signal types
SIGHUP = 1 << 1
SIGINT = 1 << 2
SIGQUIT = 1 << 3
SIGILL = 1 << 4
SIGTRAP = 1 << 5
SIGABRT = SIGIOT = 1 << 6
SIGBUS = 1 << 7
SIGFPE = 1 << 8
SIGKILL = 1 << 9
SIGUSR1 = 1 << 10
SIGSEGV = 1 << 11
SIGUSR2 = 1 << 12
SIGPIPE = 1 << 13
SIGALRM = 1 << 14
SIGTERM = 1 << 15
SIGCHLD = 1 << 16
SIGCONT = 1 << 17
SIGSTOP = 1 << 18
SIGTSTP = 1 << 19
SIGTTIN = 1 << 20
SIGTTOU = 1 << 21
SIGURG = 1 << 22
SIGXCPU = 1 << 23
SIGXFSZ = 1 << 24
SIGVTALRM = 1 << 25
SIGPROF = 1 << 26
SIGPOLL = SIGIO = 1 << 27
SIGSYS = SIGUNUSED = 1 << 28
SIGSTKFLT = 1 << 29
SIGWINCH = 1 << 30
SIGPWR = 1 << 31
SIGRTMIN_SIGRTMAX = 1 << 33

# Pointer to exception information pointers structure
_pxcptinfoptrs = None

# Function prototypes
if "_M_CEE_PURE" not in defined:
    def signal(_Signal: int,  _Function: int | None=None) -> int: ...