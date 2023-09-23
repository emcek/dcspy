from ctypes import c_void_p, sizeof
from dataclasses import dataclass
from logging import getLogger
from os import environ
from pathlib import Path
from platform import architecture
from sys import maxsize
from typing import Optional

from _cffi_backend import Lib
from cffi import FFI

LOG = getLogger(__name__)


@dataclass
class DllSdk:
    """DLL SDK."""
    name: str
    header: str
    dir: str


with open(file=Path(__file__).resolve().with_name('LogitechLCDLib.h')) as lcd_header_file:
    lcd_header = lcd_header_file.read()
with open(file=Path(__file__).resolve().with_name('LogitechLEDLib.h')) as led_header_file:
    led_header = led_header_file.read()
with open(file=Path(__file__).resolve().with_name('LogitechGkeyLib.h')) as led_header_file:
    key_header = led_header_file.read()

LcdDll = DllSdk(name='LCD', dir='LCD', header=lcd_header)
LedDll = DllSdk(name='LED', dir='LED', header=led_header)
KeyDll = DllSdk(name='Gkey', dir='G-key', header=key_header)


def load_dll(lib_type: DllSdk) -> Optional[Lib]:
    """
    Initialize and load of C dynamic linking library.

    :param lib_type: library to load: LCD or LED
    :return: C DLL instance
    """
    try:
        arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
        try:
            prog_files = environ['PROGRAMW6432']
        except KeyError:
            prog_files = environ['PROGRAMFILES']
        dll_path = f'{prog_files}\\Logitech Gaming Software\\SDK\\{lib_type.dir}\\{arch}\\Logitech{lib_type.name.capitalize()}.dll'
        LOG.debug(f'Selected DLL: {dll_path}')
        ffi = FFI()
        ffi.cdef(lib_type.header)
        dll = ffi.dlopen(dll_path)
        LOG.info(f'Loading of {lib_type.name} SDK success')
        return dll
    except (KeyError, OSError) as err:
        header = '*' * 44
        LOG.error(f'\n{header}\n*{type(err).__name__:^42}*\n{header}\nLoading of {lib_type.name} SDK failed !', exc_info=True)
        LOG.error(f'{header}')
        return None
