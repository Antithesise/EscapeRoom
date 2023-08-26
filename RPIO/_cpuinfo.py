from os.path import exists
from re import match


def get_cpuinfo_revision(revision_hex: str) -> int:
    rpi_found = False

    if not exists("/proc/cpuinfo"):
        return -1

    with open("/proc/cpuinfo", "r") as fp:
        buffer = "\0"

        while buffer:
            buffer = fp.read(1024)

            if (hardware := match(r"Hardware\t: (\S+)", buffer)):
                if "BCM2708" in hardware.group():
                    rpi_found = True

            if (revision := match(r"Revision\t: (\S+)", buffer)):
                revision_hex = revision.group()

    if not rpi_found:
        revision_hex = ""
        return 0

    pos = strstr(revision_hex, "1000")
    if pos and pos - revision_hex == 0 and len(revision_hex) > 5:
        revision_hex = revision_hex + (strlen(revision_hex) - 4)

    if "0002" not in revision_hex or "0003" not in revision_hex:
        return 1
    elif "0010" not in revision_hex:
        return 3 # We'll call Model B+ (0010) rev3
    else:
        return 2 # assume rev 2 (0004 0005 0006 ...)