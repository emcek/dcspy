from __future__ import annotations

from ctypes import CDLL, c_void_p, sizeof
from logging import getLogger
from os import environ
from platform import architecture
from sys import maxsize

from _cffi_backend import Lib
from cffi import FFI, CDefError

from dcspy.models import DllSdk

LOG = getLogger(__name__)


def load_dll(lib_type: DllSdk) -> Lib | CDLL | None:
    """
    Initialize and load of the C dynamic linking library.

    :param lib_type: Library to load: LCD, LED or Gkey
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
    except (KeyError, OSError, CDefError) as err:
        header = '*' * 44
        LOG.error(f'\n{header}\n*{type(err).__name__:^42}*\n{header}\nLoading of {lib_type.name} SDK failed !', exc_info=True)
        LOG.error(f'{header}')
        return None


def _get_ddl_path(lib_type: DllSdk) -> str:
    """
    Return the path of the DLL file based on the provided library type.

    :param lib_type: Library to load: LCD, LED or Gkey
    :return: The path of the DLL file as a string.
    """
    arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
    try:
        prog_files = environ['PROGRAMW6432']
    except KeyError:
        prog_files = environ['PROGRAMFILES']
    dll_path = f'{prog_files}\\Logitech Gaming Software\\SDK\\{lib_type.directory}\\{arch}\\Logitech{lib_type.name.capitalize()}.dll'
    LOG.debug(f'Selected DLL: {dll_path}')
    return dll_path
