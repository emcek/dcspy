from ctypes import sizeof, c_void_p
from functools import partial
from importlib import import_module
from logging import basicConfig, DEBUG, info, debug, warning
from math import log2
from platform import architecture
from socket import socket
from sys import maxsize
from typing import List

from PIL import Image, ImageDraw, ImageFont

from dcspy import SUPPORTED_CRAFTS
from dcspy.aircrafts import AircraftHandler
from dcspy.dcsbios import StringBuffer, ProtocolParser
from dcspy.sdk import lcd_sdk

basicConfig(format='%(asctime)s | %(levelname)-7s | %(message)s / %(filename)s:%(lineno)d', level=DEBUG)
consolas_11 = ImageFont.truetype('consola.ttf', 11)


class G13:
    def __init__(self, parser_hook: ProtocolParser) -> None:
        """
        Basic constructor.

        :param parser_hook:
        """
        StringBuffer(parser_hook, 0x0000, 16, partial(self.set_ac))
        self.parser = parser_hook
        self.currentAC = ''
        self.currentACHook = None
        self.shouldActivateNewAC = False
        self.isAlreadyPressed = False
        self._display = list()

        # display parameters
        self.width = lcd_sdk.MONO_WIDTH
        self.height = lcd_sdk.MONO_HEIGHT

        # GLCD Init
        arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
        dll = f"C:\\Program Files\\Logitech Gaming Software\\LCDSDK_8.57.148\\Lib\\GameEnginesWrapper\\{arch}\\LogitechLcdEnginesWrapper.dll"
        lcd_sdk.init_dll(dll)
        lcd_sdk.LogiLcdInit('DCS World', lcd_sdk.TYPE_MONO)

        self.img = Image.new('1', (self.width, self.height), 0)
        self.draw = ImageDraw.Draw(self.img)

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
        # clear bitmap
        self.draw.rectangle((0, 0, self.width, self.height), 0, 0)
        # self.ClearDisplay()
        message.extend(['' for _ in range(4 - len(message))])
        self._display = message
        for line_no, line in enumerate(message):
            self.draw.text((0, 10 * line_no), line, 1, consolas_11)
        lcd_sdk.update_display(self.img)

    def set_ac(self, value: str) -> None:
        """
        Set aircraft.

        :param value:
        """
        if not value == self.currentAC:
            self.currentAC = value
            if value in SUPPORTED_CRAFTS:
                info(f'Detected AC: {value}')
                self.display = [self.currentAC]
                self.shouldActivateNewAC = True
            else:
                warning(f'Not supported aircraft: {value}')
                self.display = ['Not supported aircraft:', self.currentAC]

    def activate_new_ac(self) -> None:
        """Actiate new aircraft."""
        self.shouldActivateNewAC = False
        plane_name = self.currentAC.replace('-', '').replace('_', '')
        plane: AircraftHandler = getattr(import_module('dcspy.aircrafts'), plane_name)(self.width, self.height)
        debug(f'Dynamic load of: {plane_name} as {self.currentAC}')
        self.currentACHook = plane
        for field_name, add_data in plane.bios_data.items():
            StringBuffer(self.parser, add_data['addr'], add_data['length'], partial(plane.set_data, field_name))

    def check_buttons(self) -> int:
        """
        Check button state.

        :return:
        """
        for btn in (lcd_sdk.MONO_BUTTON_0, lcd_sdk.MONO_BUTTON_1, lcd_sdk.MONO_BUTTON_2, lcd_sdk.MONO_BUTTON_3):
            if lcd_sdk.LogiLcdIsButtonPressed(btn):
                if not self.isAlreadyPressed:
                    self.isAlreadyPressed = True
                    return int(log2(btn)) + 1
                return 0
        self.isAlreadyPressed = False
        return 0

    def button_handle(self, sock: socket) -> None:
        """
        Button handler.

        :param sock:
        """
        button = self.check_buttons()
        if button:
            sock.send(bytes(self.currentACHook.button_handle_specific_ac(button), 'utf-8'))
