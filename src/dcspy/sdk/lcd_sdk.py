from contextlib import suppress
from logging import getLogger

from _cffi_backend import Lib
from cffi import FFI, CDefError
from PIL import Image

from dcspy.models import Color, LcdButton, LcdDll, LcdSize, LcdType
from dcspy.sdk import load_dll
from dcspy.utils import rgb

LOG = getLogger(__name__)


class LcdSdkManager:
    """Lcd SDK manager."""

    def __init__(self, name: str, lcd_type: LcdType) -> None:
        """
        Create Lcd SDK manager.

        :param name: A name of the LCD
        :param lcd_type: An integer representing the type of the LCD
        """
        result = None
        if lcd_type != LcdType.NONE:
            self.lcd_dll: Lib = load_dll(LcdDll)  # type: ignore[assignment]
            result = self.logi_lcd_init(name=name, lcd_type=lcd_type)
        LOG.debug(f'LCD is connected: {result}')

    def logi_lcd_init(self, name: str, lcd_type: LcdType) -> bool:
        """
        Make the necessary initializations.

        You must call this function prior to any other function in the library.
        :param name: The name of your applet, you can't change it after initialization
        :param lcd_type: LCD type
        :return: A result of execution
        """
        with suppress(AttributeError):
            return self.lcd_dll.LogiLcdInit(FFI().new('wchar_t[]', name), lcd_type.value)  # type: ignore[attr-defined]
        return False

    def logi_lcd_is_connected(self, lcd_type: LcdType) -> bool:
        """
        Check if a device of the type specified by the parameter is connected.

        :param lcd_type: LCD type
        :return: A result of execution
        """
        with suppress(AttributeError):
            return self.lcd_dll.LogiLcdIsConnected(lcd_type.value)  # type: ignore[attr-defined]
        return False

    def logi_lcd_is_button_pressed(self, button: LcdButton) -> bool:
        """
        Check if the button specified by the parameter is being pressed.

        :param button: Defines the button to check on
        :return: True if a button is being pressed, False otherwise
        """
        with suppress(AttributeError):
            return self.lcd_dll.LogiLcdIsButtonPressed(button.value)  # type: ignore[attr-defined]
        return False

    def logi_lcd_update(self) -> None:
        """Update the LCD."""
        with suppress(AttributeError):
            self.lcd_dll.LogiLcdUpdate()  # type: ignore[attr-defined]

    def logi_lcd_shutdown(self) -> None:
        """Kill the applet and frees memory used by the SDK."""
        with suppress(AttributeError):
            self.lcd_dll.LogiLcdShutdown()  # type: ignore[attr-defined]

    def logi_lcd_mono_set_background(self, pixels: list[int]) -> bool:
        """
        Set pixels as a rectangular area, 160 bytes wide and 43 bytes high.

        Despite the display being monochrome, 8 bits per pixel are used here for simple
        manipulation of individual pixels.

        Note: In order to use this function, the image size must be 160x43.
        The SDK will turn on the pixel on the screen if the value assigned to that byte is >= 128, it will remain off
        if the value is < 128.
        :param pixels: List of 6880 (160x43) pixels as integer
        :return: A result of execution
        """
        with suppress(AttributeError, CDefError):  # we need catch error since BYTE[] is a Windows specific
            return self.lcd_dll.LogiLcdMonoSetBackground(FFI().new('BYTE[]', pixels))  # type: ignore[attr-defined]
        return False

    def logi_lcd_mono_set_text(self, line_no: int, text: str) -> bool:
        """
        Set the specified text in the requested line on the monochrome lcd device connected.

        :param line_no: The monochrome LCD has four (4) lines, so this parameter can be any number from zero (0) to three (3)
        :param text: The text to display
        :return: A result of execution
        """
        with suppress(AttributeError):
            return self.lcd_dll.LogiLcdMonoSetText(line_no, FFI().new('wchar_t[]', text))  # type: ignore[attr-defined]
        return False

    def logi_lcd_color_set_background(self, pixels: list[tuple[int, int, int, int]]) -> bool:
        """
        Set an array of pixels as a rectangular area, 320 bytes wide and 240 bytes high.

        Since the color lcd can display the full RGB gamma, 32 bits per pixel (4-bytes) are used.
        The size of the colorBitmap array has to be 320x240x4 = 307,200 therefore.
        Note: In order to use this function, the image size must be 320x240
        :param pixels: List of 320x240x4 pixels as integers
        :return: A result of execution
        """
        img_bytes = [byte for pixel in pixels for byte in pixel]
        with suppress(AttributeError, CDefError):  # we need catch error since BYTE[] is a Windows specific
            return self.lcd_dll.LogiLcdColorSetBackground(FFI().new('BYTE[]', img_bytes))  # type: ignore[attr-defined]
        return False

    def logi_lcd_color_set_title(self, text: str, rgb: tuple[int, int, int] = (255, 255, 255)) -> bool:
        """
        Set the specified text in the first line on the color lcd device connected.

        The font size that will be displayed is bigger than the one used in the other lines,
        so you can use this function to set the title of your applet/page.
        If you don't specify any color, your title will be white.
        :param text: The text to display as a title
        :param rgb: a tuple with integer values between 0 and 255 as red, green, blue
        :return: A result of execution
        """
        with suppress(AttributeError):
            return self.lcd_dll.LogiLcdColorSetTitle(FFI().new('wchar_t[]', text), *rgb)  # type: ignore[attr-defined]
        return False

    def logi_lcd_color_set_text(self, line_no: int, text: str, rgb: tuple[int, int, int] = (255, 255, 255)) -> bool:
        """
        Set the specified text in the requested line on the color lcd device connected.

        If you don't specify any color, your title will be white.
        :param line_no: The color LCD has eight (8) lines for standard text
        :param text: defines the text you want to display
        :param rgb: tuple with integer values between 0 and 255 (interpreted as red, green or blue)
        :return: A result of execution
        """
        with suppress(AttributeError):
            return self.lcd_dll.LogiLcdColorSetText(line_no, FFI().new('wchar_t[]', text), *rgb)  # type: ignore[attr-defined]
        return False

    def update_text(self, txt: list[tuple[str, Color]]) -> None:
        """
        Update display LCD with a list of a text.

        For mono, LCD it takes four (4) elements of the list and displays as four (4) rows.
        For color, LCD takes eight (8) elements of the list and displays as eight (8) rows.
        :param txt: List of strings to display, row by row
        """
        title = txt.pop(0)
        title_txt = title[0]
        title_color = rgb(title[1])
        if self.logi_lcd_is_connected(LcdType.MONO):
            for line_no, txt_and_color in enumerate(txt[:4]):
                self.logi_lcd_mono_set_text(line_no, txt_and_color[0])
            self.logi_lcd_update()
        elif self.logi_lcd_is_connected(LcdType.COLOR):
            self.logi_lcd_color_set_title(title_txt, title_color)
            for line_no, txt_and_color in enumerate(txt):
                self.logi_lcd_color_set_text(line_no, txt_and_color[0], rgb(txt_and_color[1]))
            self.logi_lcd_update()
        else:
            LOG.warning('LCD is not connected')

    def update_display(self, image: Image.Image) -> None:
        """
        Update display LCD with image.

        :param image: Image object from the Pillow library
        """
        if self.logi_lcd_is_connected(LcdType.MONO):
            self.logi_lcd_mono_set_background(image.get_flattened_data())  # type: ignore[attr-defined]
            self.logi_lcd_update()
        elif self.logi_lcd_is_connected(LcdType.COLOR):
            self.logi_lcd_color_set_background(image.get_flattened_data())  # type: ignore[attr-defined]
            self.logi_lcd_update()
        else:
            LOG.warning('LCD is not connected')

    def clear_display(self, true_clear: bool = False) -> None:
        """
        Clear display.

        :param true_clear:
        """
        if self.logi_lcd_is_connected(LcdType.MONO):
            self._clear_mono(true_clear)
        elif self.logi_lcd_is_connected(LcdType.COLOR):
            self._clear_color(true_clear)
        self.logi_lcd_update()

    def _clear_mono(self, true_clear: bool) -> None:
        """
        Clear mono display.

        :param true_clear:
        """
        self.logi_lcd_mono_set_background([0] * LcdSize.MONO_WIDTH.value * LcdSize.MONO_HEIGHT.value)
        if true_clear:
            for i in range(4):
                self.logi_lcd_mono_set_text(i, '')

    def _clear_color(self, true_clear: bool) -> None:
        """
        Clear color display.

        :param true_clear:
        """
        self.logi_lcd_color_set_background([(0,) * 4] * LcdSize.COLOR_WIDTH.value * LcdSize.COLOR_HEIGHT.value)
        if true_clear:
            self.logi_lcd_color_set_title('')
            for i in range(8):
                self.logi_lcd_color_set_text(i, '')
