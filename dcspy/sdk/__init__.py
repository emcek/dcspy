from ctypes import CDLL, c_void_p, sizeof
from logging import getLogger
from os import environ
from platform import architecture
from sys import maxsize
from typing import Optional

LOG = getLogger(__name__)


def _init_dll(lib_type: str) -> CDLL:
    """
    Initialize C dynamic linking library.

    :param lib_type: LCD or LED
    :return: C DLL instance
    """
    arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
    try:
        prog_files = environ['PROGRAMW6432']
    except KeyError:
        prog_files = environ['PROGRAMFILES']
    dll_path = f"{prog_files}\\Logitech Gaming Software\\SDK\\{lib_type}\\{arch}\\Logitech{lib_type.capitalize()}.dll"
    LOG.debug(f'Selected DLL: {dll_path}')
    return CDLL(dll_path)


def load_dll(lib_type: str) -> Optional[CDLL]:
    """
    Initialize and load of C dynamic linking library.

    :param lib_type: library to load: LCD or LED
    :return: C DLL instance
    """
    try:
        dll = _init_dll(lib_type)
        LOG.info(f'Loading of {lib_type} SDK success')
        return dll
    except (KeyError, OSError) as err:
        header = '*' * 44
        LOG.error(f'\n{header}\n*{type(err).__name__:^42}*\n{header}\nLoading of {lib_type} SDK failed !', exc_info=True)
        LOG.error(f'{header}')
        return None
