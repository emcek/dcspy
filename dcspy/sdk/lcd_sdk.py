from ctypes import CDLL, c_bool, c_wchar_p, c_int, c_ubyte, sizeof, c_void_p
from itertools import chain
from logging import warning
from os import environ
from platform import architecture
from sys import maxsize
from typing import List

from PIL import Image

# LCD types
TYPE_MONO = 1
TYPE_COLOR = 2

# LCD Monochrome buttons
MONO_BUTTON_0 = 0x1
MONO_BUTTON_1 = 0x2
MONO_BUTTON_2 = 0x4
MONO_BUTTON_3 = 0x8

# LCD Color buttons
COLOR_BUTTON_LEFT = 0x0100
COLOR_BUTTON_RIGHT = 0x0200
COLOR_BUTTON_OK = 0x0400
COLOR_BUTTON_CANCEL = 0x0800
COLOR_BUTTON_UP = 0x1000
COLOR_BUTTON_DOWN = 0x2000
COLOR_BUTTON_MENU = 0x4000

# LCD Monochrome size
MONO_WIDTH = 160
MONO_HEIGHT = 43

# LCD Color size
COLOR_WIDTH = 320
COLOR_HEIGHT = 240


def _init_dll() -> CDLL:
    """Initialization od dynamic linking library."""
    arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
    try:
        prog_files = environ['PROGRAMW6432']
    except KeyError:
        prog_files = environ['PROGRAMFILES']
    dll_path = f"{prog_files}\\Logitech Gaming Software\\LCDSDK_8.57.148\\Lib\\GameEnginesWrapper\\{arch}\\LogitechLcdEnginesWrapper.dll"
    return CDLL(dll_path)


lcd_dll = _init_dll()


def logi_lcd_init(name: str, lcd_type: int) -> bool:
    """
    Function makes necessary initializations.

    You must call this function prior to any other function in the library.

    :param name: the name of your applet, you cant change it after initialization
    :param lcd_type: defines the type of your applet lcd target
    :return: result
    :rtype: bool
    """
    if lcd_dll:
        logilcdinit = lcd_dll['LogiLcdInit']
        logilcdinit.restype = c_bool
        logilcdinit.argtypes = (c_wchar_p, c_int)
        return logilcdinit(name, lcd_type)
    return False


def logi_lcd_is_connected(lcd_type: int) -> bool:
    """
    Function checks if a device of the type specified by the parameter is connected.

    :param lcd_type: defines the type of your applet lcd target
    :return: result
    :rtype: bool
    """
    if lcd_dll:
        logilcdisconnected = lcd_dll['LogiLcdIsConnected']
        logilcdisconnected.restype = c_bool
        logilcdisconnected.argtypes = [c_int]
        return logilcdisconnected(lcd_type)
    return False


def logi_lcd_is_button_pressed(button: int) -> bool:
    """
    Function checks if the button specified by the parameter is being pressed.

    :param button: defines the button to check on
    :return: result
    :rtype: bool
    """
    if lcd_dll:
        logilcdisbuttonpressed = lcd_dll['LogiLcdIsButtonPressed']
        logilcdisbuttonpressed.restype = c_bool
        logilcdisbuttonpressed.argtypes = [c_int]
        return logilcdisbuttonpressed(button)
    return False


def logi_lcd_update() -> None:
    """Function updates the LCD display."""
    if lcd_dll:
        logilcdupdate = lcd_dll['LogiLcdUpdate']
        logilcdupdate.restype = None
        logilcdupdate()


def logi_lcd_shutdown():
    """Function kills the applet and frees memory used by the SDK."""
    if lcd_dll:
        logilcdshutdown = lcd_dll['LogiLcdShutdown']
        logilcdshutdown.restype = None
        logilcdshutdown()


def logi_lcd_mono_set_background(pixels: List[int]) -> bool:
    """
    The array of pixels is organized as a rectangular area, 160 bytes wide and 43 bytes high.

    Despite the display being monochrome, 8 bits per pixel are used here for simple
    manipulation of individual pixels.

    Note: The image size must be 160x43 in order to use this function. The SDK will turn on
    the pixel on the screen if the value assigned to that byte is >= 128, it will remain off
    if the  value is < 128.

    :param pixels: list of 6880 (160x43) pixels as int
    :type pixels: List[int]
    :return: result
    :rtype: bool
    """
    if lcd_dll:
        logilcdmonosetbackground = lcd_dll['LogiLcdMonoSetBackground']
        logilcdmonosetbackground.restype = c_bool
        logilcdmonosetbackground.argtypes = [c_ubyte * (MONO_WIDTH * MONO_HEIGHT)]
        return logilcdmonosetbackground((c_ubyte * (MONO_WIDTH * MONO_HEIGHT))(*[p * 128 for p in pixels]))
    return False


def logi_lcd_mono_set_text(line_no: int, text: str):
    """
    Function sets the specified text in the requested line on the monochrome lcd device connected.

    :param line_no: The monochrome lcd display has 4 lines, so this parameter can be any number from 0 to 3
    :param text: defines the text you want to display
    :return: result
    :rtype: bool
    """
    if lcd_dll:
        logilcdmonosettext = lcd_dll['LogiLcdMonoSetText']
        logilcdmonosettext.restype = c_bool
        logilcdmonosettext.argtypes = (c_int, c_wchar_p)
        return logilcdmonosettext(line_no, text)
    return False


def logi_lcd_color_set_background(pixels: List[int]) -> bool:
    """
    The array of pixels is organized as a rectangular area, 320 bytes wide and 240 bytes high.

    Since the color lcd can display the full RGB gamma, 32 bits per pixel (4 bytes) are used.
    The size of the colorBitmap array has to be 320x240x4 = 307200 therefore.

    Note: The image size must be 320x240 in order to use this function.

    :param pixels: list of 307200 (320x240x4) pixels as int
    :type pixels: List[int]
    :return: result
    :rtype: bool
    """
    if lcd_dll:
        logilcdcolorsetbackground = lcd_dll['LogiLcdColorSetBackground']
        logilcdcolorsetbackground.restype = c_bool
        logilcdcolorsetbackground.argtypes = [c_ubyte * (4 * COLOR_WIDTH * COLOR_HEIGHT)]
        return logilcdcolorsetbackground((c_ubyte * (4 * COLOR_WIDTH * COLOR_HEIGHT))(*pixels))
    return False


def logi_lcd_color_set_title(text: str, red=255, green=255, blue=255):
    """
    Function sets the specified text in the first line on the color lcd device connected.

    The font size that will be displayed is bigger than the one used in the other lines,
    so you can use this function to set the title of your applet/page.
    If you dont specify any color, your title will be white.

    :param text: defines the text you want to display as title
    :param red: Values between 0 and 255 are accepted
    :param green: Values between 0 and 255 are accepted
    :param blue: Values between 0 and 255 are accepted
    :return: result
    :rtype: bool
    """
    if lcd_dll:
        logilcdcolorsettitle = lcd_dll['LogiLcdColorSetTitle']
        logilcdcolorsettitle.restype = c_bool
        logilcdcolorsettitle.argtypes = (c_wchar_p, c_int, c_int, c_int)
        return logilcdcolorsettitle(text, red, green, blue)
    return False


def logi_lcd_color_set_text(line_no: int, text: str, red: int, green: int, blue: int):
    """
    Function sets the specified text in the requested line on the color lcd device connected.

    If you dont specify any color, your title will be white.

    :param line_no: The color lcd display has 8 lines for standard text, so this parameter can be any number from 0 to 7
    :param text: defines the text you want to display
    :param red: Values between 0 and 255 are accepted
    :param green: Values between 0 and 255 are accepted
    :param blue: Values between 0 and 255 are accepted
    :return: result
    :rtype: bool
    """
    if lcd_dll:
        logilcdcolorsettext = lcd_dll['LogiLcdColorSetText']
        logilcdcolorsettext.restype = c_bool
        logilcdcolorsettext.argtypes = (c_int, c_wchar_p, c_int, c_int, c_int)
        return logilcdcolorsettext(line_no, text, red, green, blue)
    return False


def color_bg_picture(image: Image) -> None:
    """
    Set color background picture.

    :param image: image object from pillow library
    """
    if logi_lcd_is_connected(TYPE_COLOR):
        logi_lcd_mono_set_background(*list(chain(*list(image.getdata()))))
        logi_lcd_update()
    else:
        warning('LCD is not connected')


def update_display(image: Image) -> None:
    """
    Update display LCD with image.

    :param image: image object from pillow library
    """
    if logi_lcd_is_connected(TYPE_MONO):
        logi_lcd_mono_set_background(list(image.getdata()))
        logi_lcd_update()
    else:
        warning('LCD is not connected')


def clear_display(true_clear=False) -> None:
    """
    Clear display.

    :param true_clear:
    """
    logi_lcd_mono_set_background([0] * (MONO_WIDTH * MONO_HEIGHT))
    if true_clear:
        for i in range(4):
            logi_lcd_mono_set_text(i, '')
    logi_lcd_update()
