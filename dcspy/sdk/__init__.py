from ctypes import CDLL, sizeof, c_void_p
from os import environ
from platform import architecture
from sys import maxsize


def init_dll(lib: str) -> CDLL:
    """Initialization od dynamic linking library."""
    arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
    try:
        prog_files = environ['PROGRAMW6432']
    except KeyError:
        prog_files = environ['PROGRAMFILES']
    lib_type = {'LCD': f"{prog_files}\\Logitech Gaming Software\\LCDSDK_8.57.148\\Lib\\GameEnginesWrapper\\{arch}\\LogitechLcdEnginesWrapper.dll",
                'LED': f"{prog_files}\\Logitech Gaming Software\\LED_SDK_9.00\\Lib\\LogitechLedEnginesWrapper\\{arch}\\LogitechLedEnginesWrapper.dll"}
    # 'C:\\Program Files\\Logitech Gaming Software\\SDK\\LCD\\x64\\LogitechLcd.dll'
    # 'C:\\Program Files\\Logitech Gaming Software\\SDK\\LED\\x64\\LogitechLed.dll'
    return CDLL(lib_type[lib])
