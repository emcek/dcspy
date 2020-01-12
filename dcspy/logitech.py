from ctypes import sizeof, c_void_p
from functools import partial
from importlib import import_module
from logging import info, debug, warning
from math import log2
from platform import architecture
from socket import socket
from sys import maxsize
from typing import List

from PIL import Image, ImageDraw

from dcspy import SUPPORTED_CRAFTS, FONT_11, LcdSize
from dcspy.aircrafts import Aircraft
from dcspy.dcsbios import StringBuffer, ProtocolParser
from dcspy.sdk import lcd_sdk


class G13:
    def __init__(self, parser_hook: ProtocolParser) -> None:
        """
        Basic constructor.

        :param parser_hook:
        """
        StringBuffer(parser_hook, 0x0000, 16, partial(self.detecting_plane))
        self._display: List[str] = list()
        self.g13_lcd = LcdSize(width=lcd_sdk.MONO_WIDTH, height=lcd_sdk.MONO_HEIGHT)
        self.parser = parser_hook
        self.plane_name = ''
        self.plane = Aircraft(self.g13_lcd.width, self.g13_lcd.height)
        self.plane_detected = False
        self.already_pressed = False
        arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
        lcd_sdk.init_dll(f"C:\\Program Files\\Logitech Gaming Software\\LCDSDK_8.57.148\\Lib\\GameEnginesWrapper\\{arch}\\LogitechLcdEnginesWrapper.dll")
        lcd_sdk.LogiLcdInit('DCS World', lcd_sdk.TYPE_MONO)

    @property
    def display(self) -> List[str]:
        """
        Get latest set text at LCD.

        :return: list with 4 strings row by row
        :rtype: List[str]
        """
        return self._display

    @display.setter
    def display(self, message: List[str]) -> None:
        """
        Display message at LCD.

        :param message: List of strings to display, row by row. G13 support 4 rows.
        :type message: List[str, ...]
        """
        img = Image.new('1', (self.g13_lcd.width, self.g13_lcd.height), 0)
        draw = ImageDraw.Draw(img)
        message.extend(['' for _ in range(4 - len(message))])
        self._display = message
        for line_no, line in enumerate(message):
            draw.text((0, 10 * line_no), line, 1, FONT_11)
        lcd_sdk.update_display(img)

    def detecting_plane(self, value: str) -> None:
        """
        Try detect airplane base on value received from DCS-BIOS.

        :param value: data from DCS-BIOS
        :type value: str
        """
        value = value.replace('-', '').replace('_', '')
        if self.plane_name != value:
            self.plane_name = value
            if self.plane_name in SUPPORTED_CRAFTS:
                self.plane_name = value
                info(f'Detected Aircraft: {value}')
                self.display = ['Detected aircraft:', self.plane_name]
                self.plane_detected = True
            else:
                warning(f'Not supported aircraft: {value}')
                self.display = ['Detected aircraft:', self.plane_name, 'Not supported yet!']

    def load_new_plane(self) -> None:
        """Load new detected aircraft."""
        self.plane_detected = False
        self.plane = getattr(import_module('dcspy.aircrafts'), self.plane_name)(self.g13_lcd.width, self.g13_lcd.height)
        debug(f'Dynamic load of: {self.plane_name} as {SUPPORTED_CRAFTS[self.plane_name]}')
        for field_name, proto_data in self.plane.bios_data.items():
            StringBuffer(self.parser, proto_data['addr'], proto_data['len'], partial(self.plane.set_bios, field_name))

    def check_buttons(self) -> int:
        """
        Check button state.

        :return:
        """
        for btn in (lcd_sdk.MONO_BUTTON_0, lcd_sdk.MONO_BUTTON_1, lcd_sdk.MONO_BUTTON_2, lcd_sdk.MONO_BUTTON_3):
            if lcd_sdk.LogiLcdIsButtonPressed(btn):
                if not self.already_pressed:
                    self.already_pressed = True
                    return int(log2(btn)) + 1
                return 0
        self.already_pressed = False
        return 0

    def button_handle(self, sock: socket) -> None:
        """
        Button handler.

        :param sock:
        """
        button = self.check_buttons()
        if button:
            sock.send(bytes(self.plane.button_handle_specific_ac(button), 'utf-8'))
