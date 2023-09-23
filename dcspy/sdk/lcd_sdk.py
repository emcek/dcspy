from logging import getLogger
from typing import List, Tuple

from _cffi_backend import Lib
from cffi import FFI, CDefError
from PIL import Image

from dcspy import COLOR_HEIGHT, COLOR_WIDTH, MONO_HEIGHT, MONO_WIDTH, TYPE_COLOR, TYPE_MONO
from dcspy.sdk import LcdDll, load_dll

LOG = getLogger(__name__)
LCD_DLL: Lib = load_dll(LcdDll)


def logi_lcd_init(name: str, lcd_type: int) -> bool:
    """
    Make necessary initializations.

    You must call this function prior to any other function in the library.
    :param name: the name of your applet, you can't change it after initialization
    :param lcd_type: defines the type of your applet lcd target
    :return: result
    """
    try:
        return LCD_DLL.LogiLcdInit(FFI().new('wchar_t[]', name), lcd_type)
    except AttributeError:
        return False


def logi_lcd_is_connected(lcd_type: int) -> bool:
    """
    Check if a device of the type specified by the parameter is connected.

    :param lcd_type: defines the type of your applet lcd target
    :return: result
    """
    try:
        return LCD_DLL.LogiLcdIsConnected(lcd_type)
    except AttributeError:
        return False


def logi_lcd_is_button_pressed(button: int) -> bool:
    """
    Check if the button specified by the parameter is being pressed.

    :param button: defines the button to check on
    :return: result
    """
    try:
        return LCD_DLL.LogiLcdIsButtonPressed(button)
    except AttributeError:
        return False


def logi_lcd_update() -> None:
    """Update the LCD."""
    try:
        LCD_DLL.LogiLcdUpdate()
    except AttributeError:
        pass


def logi_lcd_shutdown() -> None:
    """Kill the applet and frees memory used by the SDK."""
    try:
        LCD_DLL.LogiLcdShutdown()
    except AttributeError:
        pass


def logi_lcd_mono_set_background(pixels: List[int]) -> bool:
    """
    Set pixels as a rectangular area, 160 bytes wide and 43 bytes high.

    Despite the display being monochrome, 8 bits per pixel are used here for simple
    manipulation of individual pixels.

    Note: The image size must be 160x43 in order to use this function. The SDK will turn on
    the pixel on the screen if the value assigned to that byte is >= 128, it will remain off
    if the  value is < 128.
    :param pixels: list of 6880 (160x43) pixels as int
    :return: result
    """
    try:
        return LCD_DLL.LogiLcdMonoSetBackground(FFI().new('BYTE[]', pixels))
    except (AttributeError, CDefError):  # we need catch error since BYTE[] is windows specific
        return False


def logi_lcd_mono_set_text(line_no: int, text: str) -> bool:
    """
    Set the specified text in the requested line on the monochrome lcd device connected.

    :param line_no: The monochrome LCD has 4 lines, so this parameter can be any number from 0 to 3
    :param text: defines the text you want to display
    :return: result
    """
    try:
        return LCD_DLL.LogiLcdMonoSetText(line_no, FFI().new('wchar_t[]', text))
    except AttributeError:
        return False


def logi_lcd_color_set_background(pixels: List[Tuple[int, int, int, int]]) -> bool:
    """
    Set array of pixels as a rectangular area, 320 bytes wide and 240 bytes high.

    Since the color lcd can display the full RGB gamma, 32 bits per pixel (4 bytes) are used.
    The size of the colorBitmap array has to be 320x240x4 = 307200 therefore.
    Note: The image size must be 320x240 in order to use this function.
    :param pixels: list of 307200 (320x240x4) pixels as int
    :return: result
    """
    img_bytes = [byte for pixel in pixels for byte in pixel]
    try:
        return LCD_DLL.LogiLcdColorSetBackground(FFI().new('BYTE[]', img_bytes))
    except (AttributeError, CDefError):  # we need catch error since BYTE[] is windows specific
        return False


def logi_lcd_color_set_title(text: str, rgb: Tuple[int, int, int] = (255, 255, 255)) -> bool:
    """
    Set the specified text in the first line on the color lcd device connected.

    The font size that will be displayed is bigger than the one used in the other lines,
    so you can use this function to set the title of your applet/page.
    If you don't specify any color, your title will be white.
    :param text: defines the text you want to display as title
    :param rgb: tuple with integer values between 0 and 255 as red, green, blue
    :return: result
    """
    try:
        return LCD_DLL.LogiLcdColorSetTitle(FFI().new('wchar_t[]', text), *rgb)
    except AttributeError:
        return False


def logi_lcd_color_set_text(line_no: int, text: str, rgb: Tuple[int, int, int] = (255, 255, 255)) -> bool:
    """
    Set the specified text in the requested line on the color lcd device connected.

    If you don't specify any color, your title will be white.
    :param line_no: The color LCD has 8 lines for standard text, so this parameter can be any number from 0 to 7
    :param text: defines the text you want to display
    :param rgb: tuple with integer values between 0 and 255 as red, green, blue
    :return: result
    """
    try:
        return LCD_DLL.LogiLcdColorSetText(line_no, FFI().new('wchar_t[]', text), *rgb)
    except AttributeError:
        return False


def update_text(txt: List[str]) -> None:
    """
    Update display LCD with list of text.

    For mono LCD it takes 4 elements of list and display as 4 rows.
    For color LCD  takes 8 elements of list and display as 8 rows.
    :param txt: List of strings to display, row by row
    """
    if logi_lcd_is_connected(TYPE_MONO):
        for line_no, line in enumerate(txt):
            logi_lcd_mono_set_text(line_no, line)
        logi_lcd_update()
    elif logi_lcd_is_connected(TYPE_COLOR):
        for line_no, line in enumerate(txt):
            logi_lcd_color_set_text(line_no, line)
        logi_lcd_update()
    else:
        LOG.warning('LCD is not connected')


def update_display(image: Image.Image) -> None:
    """
    Update display LCD with image.

    :param image: image object from pillow library
    """
    if logi_lcd_is_connected(TYPE_MONO):
        logi_lcd_mono_set_background(list(image.getdata()))
        logi_lcd_update()
    elif logi_lcd_is_connected(TYPE_COLOR):
        logi_lcd_color_set_background(list(image.getdata()))
        logi_lcd_update()
    else:
        LOG.warning('LCD is not connected')


def clear_display(true_clear=False) -> None:
    """
    Clear display.

    :param true_clear:
    """
    if logi_lcd_is_connected(TYPE_MONO):
        _clear_mono(true_clear)
    elif logi_lcd_is_connected(TYPE_COLOR):
        _clear_color(true_clear)
    logi_lcd_update()


def _clear_mono(true_clear) -> None:
    """
    Clear mono display.

    :param true_clear:
    """
    logi_lcd_mono_set_background([0] * MONO_WIDTH * MONO_HEIGHT)
    if true_clear:
        for i in range(4):
            logi_lcd_mono_set_text(i, '')


def _clear_color(true_clear) -> None:
    """
    Clear color display.

    :param true_clear:
    """
    logi_lcd_color_set_background([(0,) * 4] * COLOR_WIDTH * COLOR_HEIGHT)
    if true_clear:
        for i in range(8):
            logi_lcd_color_set_text(i, '')
