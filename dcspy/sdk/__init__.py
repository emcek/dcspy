from ctypes import CDLL, c_void_p, sizeof
from dataclasses import dataclass
from logging import getLogger
from os import environ
from pathlib import Path
from platform import architecture
from sys import maxsize
from typing import Optional, Union

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


def load_dll(lib_type: DllSdk) -> Optional[Union[Lib, CDLL]]:
    """
    Initialize and load of C dynamic linking library.

    :param lib_type: library to load: LCD, LED or Gkey
    :return: C DLL instance
    """
    try:
        dll_path = _get_ddl_path(lib_type)

        if lib_type.name == 'Gkey':
            dll = CDLL(dll_path)
        else:
            ffi = FFI()
            ffi.cdef(lib_type.header)
            dll = ffi.dlopen(dll_path)  # type: ignore[assignment]

        LOG.info(f'Loading of {lib_type.name} SDK success')
        return dll
    except (KeyError, OSError) as err:
        header = '*' * 44
        LOG.error(f'\n{header}\n*{type(err).__name__:^42}*\n{header}\nLoading of {lib_type.name} SDK failed !', exc_info=True)
        LOG.error(f'{header}')
        return None


def _get_ddl_path(lib_type: DllSdk) -> str:
    """
    Return the path of the DLL file based on the provided library type.

    :param lib_type: library to load: LCD, LED or Gkey
    :return: The path of the DLL file as a string.
    """
    arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
    try:
        prog_files = environ['PROGRAMW6432']
    except KeyError:
        prog_files = environ['PROGRAMFILES']
    dll_path = f'{prog_files}\\Logitech Gaming Software\\SDK\\{lib_type.dir}\\{arch}\\Logitech{lib_type.name.capitalize()}.dll'
    LOG.debug(f'Selected DLL: {dll_path}')
    return dll_path
