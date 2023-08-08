from ctypes import c_void_p, sizeof
from logging import getLogger
from os import environ
from platform import architecture
from sys import maxsize
from typing import Optional

from cffi import FFI

LOG = getLogger(__name__)


def _init_dll(lib_type: str) -> object:
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
    ffi = FFI()
    # dll = CDLL(dll_path)
    ffi.cdef('''
bool LogiLcdInit(wchar_t* friendlyName, int lcdType);
bool LogiLcdIsConnected(int lcdType);
bool LogiLcdIsButtonPressed(int button);
void LogiLcdUpdate();
void LogiLcdShutdown();

bool LogiLcdMonoSetBackground(BYTE monoBitmap[]);
bool LogiLcdMonoSetText(int lineNumber, wchar_t* text);

bool LogiLcdColorSetBackground(BYTE colorBitmap[]);
bool LogiLcdColorSetTitle(wchar_t* text, int red, int green, int blue);
bool LogiLcdColorSetText(int lineNumber, wchar_t* text, int red, int green, int blue);
    ''')
    dll = ffi.dlopen(dll_path)
    return dll


def load_dll(lib_type: str) -> Optional[object]:
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
