from RPIO._h_corecrt import *


defined = set(dir())


_O_RDONLY = "r" # open for reading only
_O_WRONLY = "w" # open for writing only
_O_RDWR = "r+" # open for reading and writing
_O_APPEND = "a" # writes done at eof

_O_CREAT = "x" # create and open file
_O_TRUNC = 0x0200 # open and truncate
_O_EXCL = 0x0400 # open only if file doesn't already exist

# O_TEXT files have <cr><lf> sequences translated to <lf> on read()'s and <lf>
# sequences translated to <cr><lf> on write()'s

_O_TEXT = 0x4000 # file mode is text (translated)
_O_BINARY = "b" # file mode is binary (untranslated)
_O_WTEXT = 0x10000 # file mode is UTF16 (translated)
_O_U16TEXT = 0x20000 # file mode is UTF16 no BOM (translated)
_O_U8TEXT = 0x40000 # file mode is UTF8  no BOM (translated)

# macro to translate the C 2.0 name used to force binary mode for files
_O_RAW = _O_BINARY

_O_NOINHERIT = 0x0080 # child process doesn't inherit file
_O_TEMPORARY = 0x0040 # temporary file bit (file is deleted when last handle is closed)
_O_SHORT_LIVED = 0x1000 # temporary storage file, try not to flush
_O_OBTAIN_DIR = 0x2000 # get information about a directory
_O_SEQUENTIAL = 0x0020 # file access is primarily sequential
_O_RANDOM = 0x0010 # file access is primarily random


if {"_CRT_DECLARE_NONSTDC_NAMES", "_CRT_DECLARE_NONSTDC_NAMES"}.issubset(defined) or {"_CRT_DECLARE_NONSTDC_NAMES", "__STDC"}.isdisjoint(defined):
    O_RDONLY = _O_RDONLY
    O_WRONLY = _O_WRONLY
    O_RDWR = _O_RDWR
    O_APPEND = _O_APPEND
    O_CREAT = _O_CREAT
    O_TRUNC = _O_TRUNC
    O_EXCL = _O_EXCL
    O_TEXT = _O_TEXT
    O_BINARY = _O_BINARY
    O_RAW = _O_BINARY
    O_TEMPORARY = _O_TEMPORARY
    O_NOINHERIT = _O_NOINHERIT
    O_SEQUENTIAL = _O_SEQUENTIAL
    O_RANDOM = _O_RANDOM
