from ctypes import CDLL, c_bool, c_wchar_p, c_int, c_ubyte, sizeof, c_void_p
from itertools import chain
from logging import warning, error
from os import environ, path
from platform import architecture
from sys import maxsize

from PIL import Image

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

# LogiLcdInit = None
LogiLcdIsConnected = None
LogiLcdIsButtonPressed = None
LogiLcdUpdate = None
LogiLcdShutdown = None
LogiLcdMonoSetBackground = None
LogiLcdMonoSetText = None
LogiLcdColorSetBackground = None
LogiLcdColorSetTitle = None
LogiLcdColorSetText = None


def init_dll() -> callable:
    """Initialization od dynamic linking library."""
    global LogiLcdIsConnected, LogiLcdIsButtonPressed, LogiLcdUpdate, LogiLcdShutdown, LogiLcdMonoSetBackground
    global LogiLcdMonoSetText, LogiLcdColorSetBackground, LogiLcdColorSetTitle, LogiLcdColorSetText

    arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
    try:
        prog_files = environ['PROGRAMW6432']
    except KeyError:
        prog_files = environ['PROGRAMFILES']
    dll_path = f"{prog_files}\\Logitech Gaming Software\\LCDSDK_8.57.148\\Lib\\GameEnginesWrapper\\{arch}\\LogitechLcdEnginesWrapper.dll"

    if path.exists(dll_path):
        return CDLL(dll_path)
    else:
        raise FileNotFoundError(dll_path)


try:
    lcd_dll = init_dll()
except FileNotFoundError as err:
    error(err)
    lcd_dll = None


def logi_lcd_init(name: str, lcd_type: int) -> bool:
    """ initializes the sdk for the current thread. """
    if lcd_dll:
        LogiLcdInit = lcd_dll['LogiLcdInit']
        LogiLcdInit.restype = c_bool
        LogiLcdInit.argtypes = (c_wchar_p, c_int)
        return bool(lcd_dll.LogiLcdInit(name, lcd_type))
    return False


def test():
    # https://docs.python.org/2/library/ctypes.html#fundamental-data-types
    # Generic Functions
    LogiLcdInit = lcd_dll['LogiLcdInit']
    LogiLcdInit.restype = c_bool
    LogiLcdInit.argtypes = (c_wchar_p, c_int)

    LogiLcdIsConnected = lcd_dll['LogiLcdIsConnected']
    LogiLcdIsConnected.restype = c_bool
    LogiLcdIsConnected.argtypes = [c_int]

    LogiLcdIsButtonPressed = lcd_dll['LogiLcdIsButtonPressed']
    LogiLcdIsButtonPressed.restype = c_bool
    LogiLcdIsButtonPressed.argtypes = [c_int]

    LogiLcdUpdate = lcd_dll['LogiLcdUpdate']
    LogiLcdUpdate.restype = None

    LogiLcdShutdown = lcd_dll['LogiLcdShutdown']
    LogiLcdShutdown.restype = None

    # Monochrome Lcd Functions
    LogiLcdMonoSetBackground = lcd_dll['LogiLcdMonoSetBackground']
    LogiLcdMonoSetBackground.restype = c_bool
    LogiLcdMonoSetBackground.argtypes = [c_ubyte * 6880]

    LogiLcdMonoSetText = lcd_dll['LogiLcdMonoSetText']
    LogiLcdMonoSetText.restype = c_bool
    LogiLcdMonoSetText.argtypes = (c_int, c_wchar_p)

    # Color LCD Functions
    LogiLcdColorSetBackground = lcd_dll['LogiLcdColorSetBackground']
    LogiLcdColorSetBackground.restype = c_bool
    LogiLcdColorSetBackground.argtypes = [c_ubyte * 307200]

    LogiLcdColorSetTitle = lcd_dll['LogiLcdColorSetTitle']
    LogiLcdColorSetTitle.restype = c_bool
    LogiLcdColorSetTitle.argtypes = (c_wchar_p, c_int, c_int, c_int)

    LogiLcdColorSetText = lcd_dll['LogiLcdColorSetText']
    LogiLcdColorSetText.restype = c_bool
    LogiLcdColorSetText.argtypes = (c_int, c_wchar_p, c_int, c_int, c_int)


def color_gb_picture(im: Image) -> None:
    """
    Set color background picture.

    :param im:
    """
    global LogiLcdColorSetBackground

    LogiLcdColorSetBackground((c_ubyte * 307200)(*list(chain(*list(im.getdata())))))


def update_display(img: Image) -> None:
    """
    Update display.

    :param img:
    """
    global LogiLcdIsConnected, LogiLcdMonoSetBackground, LogiLcdUpdate
    pixels = list(img.getdata())
    for i, _ in enumerate(pixels):
        pixels[i] *= 128

    # put bitmap array into display
    if LogiLcdIsConnected(TYPE_MONO):
        LogiLcdMonoSetBackground((c_ubyte * (160 * 43))(*pixels))
        LogiLcdUpdate()
    else:
        warning('LCD is not connected')


def clear_display(true_clear=False) -> None:
    """
    Clear display.

    :param true_clear:
    """
    global LogiLcdMonoSetBackground, LogiLcdMonoSetText, LogiLcdUpdate
    LogiLcdMonoSetBackground((c_ubyte * (160 * 43))(*[0] * (160 * 43)))
    if true_clear:
        for i in range(4):
            LogiLcdMonoSetText(i, '')
    LogiLcdUpdate()
