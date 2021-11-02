from ctypes import CDLL, sizeof, c_void_p
from logging import getLogger
from os import environ
from platform import architecture
from sys import maxsize
from typing import Optional

LOG = getLogger(__name__)


def _init_dll(lib_type: str) -> CDLL:
    """
    Initialization of C dynamic linking library.

    :param lib_type: LCD or LED
    :return: C DLL instance
    """
    arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
    try:
        prog_files = environ['PROGRAMW6432']
    except KeyError:
        prog_files = environ['PROGRAMFILES']
    return CDLL(f"{prog_files}\\Logitech Gaming Software\\SDK\\{lib_type}\\{arch}\\Logitech{lib_type.capitalize()}.dll")


def load_dll(lib_type: str) -> Optional[CDLL]:
    """
    Initialization and loading of C dynamic linking library.

    :param lib_type: library to load: LCD or LED
    :return: C DLL instance
    """
    try:
        dll = _init_dll(lib_type)
        LOG.info(f'Loading of {lib_type} SDK success')
        return dll
    except (KeyError, FileNotFoundError) as err:
        header = '*' * 40
        space = ' ' * 15
        LOG.error(f'\n{header}\n*{space}ERROR!!!{space}*\n{header}\n'
                  f'Loading of {lib_type} SDK failed: {err.__class__.__name__}', exc_info=True)
        LOG.error(f'\n{header}')
        return None
