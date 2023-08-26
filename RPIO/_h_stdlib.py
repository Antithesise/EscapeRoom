from RPIO._h_corecrt import *
# from corecrt_malloc.h import *
# from corecrt_search.h import *
# from corecrt_wstdlib.h import *
# from limits.h import *

from typing import Any, Callable


defined = set(dir())


if "_countof" not in defined:
    _countof = None


def _swab(_Buf1: str, _Buf2: str, _SizeInBytes: int) -> None: ...

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# Exit and Abort
#
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# Argument values for exit()
EXIT_SUCCESS =  0
EXIT_FAILURE =  1

if _CRT_FUNCTIONS_REQUIRED:
    def exit(_Code: int) -> None: ...
    def _exit(_Code: int) -> None: ...
    def _Exit(_Code: int) -> None: ...
    def quick_exit(_Code: int) -> None: ...
    def abort() -> None: ...

# Argument values for _set_abort_behavior().
_WRITE_ABORT_MSG =   0x1 # debug only, has no effect in release
_CALL_REPORTFAULT =  0x2

def _set_abort_behavior(
    _Flags: int,
    _Mask: int
    ) -> int: ...

if "_CRT_ONEXIT_T_DEFINED" not in defined:
    _CRT_ONEXIT_T_DEFINED = None


def atexit(func: Callable) -> int: ...
def _onexit(_Func: Callable | None=None) -> int: ...

def at_quick_exit() -> int: ...



#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# Global State (errno, global handlers, etc.)
#
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
if "_M_CEE_PURE" not in defined:
    # Establishes a purecall handler
    def _set_purecall_handler(
        _Handler: None
        ) -> None: ...

    def _get_purecall_handler() -> None: ...

    # Establishes an invalid parameter handler
    def _set_invalid_parameter_handler(
        _Handler: None
        ) -> None: ...

    def _get_invalid_parameter_handler() -> None: ...

    def _set_thread_local_invalid_parameter_handler(
        _Handler: None
        ) -> None: ...

    def _get_thread_local_invalid_parameter_handler() -> None: ...


# Argument values for _set_error_mode().
_OUT_TO_DEFAULT =  0
_OUT_TO_STDERR =   1
_OUT_TO_MSGBOX =   2
_REPORT_ERRMODE =  3

def _set_error_mode(_Mode: int) -> int: ...

if _CRT_FUNCTIONS_REQUIRED:
    def _errno() -> int: ...
    errno =  _errno()

    def _set_errno(_Value: int) -> int: ...
    def _get_errno(_Value: int) -> int: ...

    def __doserrno() -> int: ...
    _doserrno =  __doserrno()

    def _set_doserrno(_Value: int) -> int: ...
    def _get_doserrno(_Value: int) -> int: ...

    # This is non- for backwards compatibility do not modify it.
    def __sys_errlist() -> str: ...
    _sys_errlist =  __sys_errlist()

    def __sys_nerr() -> int: ...
    _sys_nerr =  __sys_nerr()

    def perror(_ErrMsg: str) -> None: ...



# These point to the executable module name.
def __p__pgmptr () -> str: ...
def __p__wpgmptr() -> str: ...
def __p__fmode  () -> int: ...

if "_CRT_DECLARE_GLOBAL_VARIABLES_DIRECTLY" in defined:
    _pgmptr: str
    _wpgmptr: str

    if "_CORECRT_BUILD" not in defined:
        _fmode: int

else:
    _pgmptr =   __p__pgmptr ()
    _wpgmptr =  __p__wpgmptr()
    _fmode =    __p__fmode  ()

def _get_pgmptr (_Value: str) -> int: ...

def _get_wpgmptr(_Value: str) -> int: ...

def _set_fmode  (_Mode: int) -> int: ...

def _get_fmode  (_PMode: int) -> int: ...