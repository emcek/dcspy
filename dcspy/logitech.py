from functools import partial
from importlib import import_module
from logging import getLogger
from math import log2
from socket import socket
from typing import List

from PIL import Image, ImageDraw

from dcspy import SUPPORTED_CRAFTS, FONT_11, LcdSize, SEND_ADDR
from dcspy.aircrafts import Aircraft
from dcspy.dcsbios import ProtocolParser
from dcspy.sdk import lcd_sdk

LOGGER = getLogger(__name__)


class G13:
    def __init__(self, parser_hook: ProtocolParser) -> None:
        """
        Setup G13 LCD and callback for current DCS aircraft in used.

        :param parser_hook: BSC-BIOS parser
        :type parser_hook: ProtocolParser
        """
        getattr(import_module('dcspy.dcsbios'), 'StringBuffer')(parser_hook, 0x0000, 16, partial(self.detecting_plane))
        self._display: List[str] = list()
        self.g13_lcd = LcdSize(width=lcd_sdk.MONO_WIDTH, height=lcd_sdk.MONO_HEIGHT)
        self.parser = parser_hook
        self.plane_name = ''
        self.plane = Aircraft(self.g13_lcd.width, self.g13_lcd.height)
        self.plane_detected = False
        self.already_pressed = False
        lcd_sdk.logi_lcd_init('DCS World', lcd_sdk.TYPE_MONO)

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
                LOGGER.info(f'Detected Aircraft: {value}')
                self.display = ['Detected aircraft:', self.plane_name]
                self.plane_detected = True
            else:
                LOGGER.warning(f'Not supported aircraft: {value}')
                self.display = ['Detected aircraft:', self.plane_name, 'Not supported yet!']

    def load_new_plane(self) -> None:
        """
        Dynamic load of new detected aircraft.

        Setup callbacks for detected plane inside DCS-BIOS parser.
        """
        self.plane_detected = False
        self.plane = getattr(import_module('dcspy.aircrafts'), self.plane_name)(self.g13_lcd.width, self.g13_lcd.height)
        LOGGER.debug(f'Dynamic load of: {self.plane_name} as {SUPPORTED_CRAFTS[self.plane_name]}')
        for field_name, proto_data in self.plane.bios_data.items():
            buffer = getattr(import_module('dcspy.dcsbios'), proto_data['class'])
            buffer(parser=self.parser, callback=partial(self.plane.set_bios, field_name), **proto_data['args'])

    def check_buttons(self) -> int:
        """
        Check if button was pressed and return its number.

        :return: number of pressed button 1-4
        :rtype: int
        """
        for btn in (lcd_sdk.MONO_BUTTON_0, lcd_sdk.MONO_BUTTON_1, lcd_sdk.MONO_BUTTON_2, lcd_sdk.MONO_BUTTON_3):
            if lcd_sdk.logi_lcd_is_button_pressed(btn):
                if not self.already_pressed:
                    self.already_pressed = True
                    return int(log2(btn)) + 1
                return 0
        self.already_pressed = False
        return 0

    def button_handle(self, sock: socket) -> None:
        """
        Button handler.

        * detect if button was pressed
        * fetch BSD-BIOS request form plane
        * sent it action to DCS-BIOS via. network socket

        :param sock: network socket
        :type sock: socket
        """
        button = self.check_buttons()
        if button:
            sock.sendto(bytes(self.plane.button_request(button), 'utf-8'), SEND_ADDR)
