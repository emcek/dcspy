from __future__ import annotations

from ctypes import CDLL
from logging import getLogger

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
        dll_path = lib_type.get_path()
        LOG.debug(f'Selected DLL: {dll_path}')

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
