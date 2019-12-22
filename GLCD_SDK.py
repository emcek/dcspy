from ctypes import CDLL, c_bool, c_wchar_p, c_int, c_ubyte
from itertools import chain
from platform import system
from sys import exit

NAME = "GLCD SDK.py"
VERSION = "0.0.1"

# LCD types
TYPE_MONO = 1
TYPE_COLOR = 2

# LCD Monochrome buttons
MONO_BUTTON_0 = 0x00000001
MONO_BUTTON_1 = 0x00000002
MONO_BUTTON_2 = 0x00000004
MONO_BUTTON_3 = 0x00000008

# LCD Color buttons
COLOR_BUTTON_LEFT = 0x00000100
COLOR_BUTTON_RIGHT = 0x00000200
COLOR_BUTTON_OK = 0x00000400
COLOR_BUTTON_CANCEL = 0x00000800
COLOR_BUTTON_UP = 0x00001000
COLOR_BUTTON_DOWN = 0x00002000
COLOR_BUTTON_MENU = 0x00004000

# LCD Monochrome size
MONO_WIDTH = 160
MONO_HEIGHT = 43

# LCD Color size
COLOR_WIDTH = 320
COLOR_HEIGHT = 240


def chkDLL():
    try:
        _dll
    except NameError() as e:
        if str(e).split("'")[1] == "_dll":
            raise Exception('initDLL!!!!!!!!')
        else:
            raise Exception(e)


def initDLL(dll_path):
    global _dll, LogiLcdInit, LogiLcdIsConnected, LogiLcdIsButtonPressed, LogiLcdUpdate, LogiLcdShutdown, LogiLcdMonoSetBackground, LogiLcdMonoSetText, LogiLcdColorSetBackground, LogiLcdColorSetTitle, LogiLcdColorSetText, ColorBGPIL

    _dll = CDLL(dll_path)

    # https://docs.python.org/2/library/ctypes.html#fundamental-data-types
    # Generic Functions
    LogiLcdInit = _dll['LogiLcdInit']
    LogiLcdInit.restype = c_bool
    LogiLcdInit.argtypes = (c_wchar_p, c_int)

    LogiLcdIsConnected = _dll['LogiLcdIsConnected']
    LogiLcdIsConnected.restype = c_bool
    LogiLcdIsConnected.argtypes = [c_int]

    LogiLcdIsButtonPressed = _dll['LogiLcdIsButtonPressed']
    LogiLcdIsButtonPressed.restype = c_bool
    LogiLcdIsButtonPressed.argtypes = [c_int]

    LogiLcdUpdate = _dll['LogiLcdUpdate']
    LogiLcdUpdate.restype = None
    # LogiLcdUpdate.argtypes = [None]

    LogiLcdShutdown = _dll['LogiLcdShutdown']
    LogiLcdShutdown.restype = None
    # LogiLcdShutdown.argtypes = [None]

    # Monochrome Lcd Functions
    LogiLcdMonoSetBackground = _dll['LogiLcdMonoSetBackground']
    LogiLcdMonoSetBackground.restype = c_bool
    LogiLcdMonoSetBackground.argtypes = [c_ubyte * 6880]

    LogiLcdMonoSetText = _dll['LogiLcdMonoSetText']
    LogiLcdMonoSetText.restype = c_bool
    LogiLcdMonoSetText.argtypes = (c_int, c_wchar_p)

    # Color LCD Functions
    LogiLcdColorSetBackground = _dll['LogiLcdColorSetBackground']
    LogiLcdColorSetBackground.restype = c_bool
    LogiLcdColorSetBackground.argtypes = [c_ubyte * 307200]

    LogiLcdColorSetTitle = _dll['LogiLcdColorSetTitle']
    LogiLcdColorSetTitle.restype = c_bool
    LogiLcdColorSetTitle.argtypes = (c_wchar_p, c_int, c_int, c_int)

    LogiLcdColorSetText = _dll['LogiLcdColorSetText']
    LogiLcdColorSetText.restype = c_bool
    LogiLcdColorSetText.argtypes = (c_int, c_wchar_p, c_int, c_int, c_int)

    def ColorBGPIL(im):
        LogiLcdColorSetBackground((c_ubyte * 307200)(*list(chain(*list(im.getdata())))))


def flatten(listOfLists):
    # Flatten one level of nesting
    return chain.from_iterable(listOfLists)


if __name__ == "__main__":
    if system() != "Windows":
        print("Host is not Windows. This module can't work")
        exit(0)
    else:
        print("Host is Windows. This module can work")
