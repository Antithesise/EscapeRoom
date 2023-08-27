from RPIO._h_corecrt import *

from typing import NewType


defined = set(dir())


NSIG = 23  # maximum signal number + 1

# Signal types
SIGINT = 2   # interrupt
SIGILL = 4   # illegal instruction - invalid function image
SIGFPE = 8   # floating point exception
SIGSEGV = 11  # segment violation
SIGTERM = 15  # Software termination signal from kill
SIGBREAK = 21  # Ctrl-Break sequence
SIGABRT = 22  # abnormal termination triggered by abort call

SIGABRT_COMPAT = 6   # SIGABRT compatible with other platforms, same as SIGABRT

# Signal action codes
SIG_DFL = 0     # default signal action
SIG_IGN = 1     # ignore signal
SIG_GET = 2     # return current value
SIG_SGE = 3     # signal gets error
SIG_ACK = 4     # acknowledge

if "_CORECRT_BUILD" in defined:
    # Internal use only!  Not valid as an argument to signal().
    SIG_DIE = 5 # terminate process

# Signal error value (returned by signal call on error)
SIG_ERR = -1    # signal error value



# Pointer to exception information pointers structure
_pxcptinfoptrs = None

# Function prototypes
if "_M_CEE_PURE" not in defined:
    def signal(_Signal: int,  _Function: int | None=None) -> int: ...