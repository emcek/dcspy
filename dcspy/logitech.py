from functools import partial
from importlib import import_module
from logging import getLogger
from math import log2
from socket import socket
from typing import List, Tuple

from PIL import Image, ImageDraw

from dcspy import LcdColor, LcdMono, SUPPORTED_CRAFTS, FONT, SEND_ADDR, lcd_sdk
from dcspy.aircrafts import Aircraft
from dcspy.dcsbios import ProtocolParser

LOG = getLogger(__name__)


class LogitechKeyboard:
    def __init__(self, parser_hook: ProtocolParser, **kwargs) -> None:
        """
        General keyboard with LCD form Logitech.

        It can be easily extended for any of:
        - Mono LCD: G13, G15 (v1 and v2) and G510
        - RGB LCD: G19

        However it define bunch of functionally to be used be child class:
        - DCS-BIOS callback for currently used aircraft in DCS
        - auto-detecting aircraft and load its handling class
        - send button request to DCS-BIOS

        Child class needs redefine:
        - buttons with supported buttons as tuple of int
        - pass lcd_type argument as LcdSize NamedTuple to super constructor

        :param parser_hook: BSC-BIOS parser
        :type parser_hook: ProtocolParser
        """
        getattr(import_module('dcspy.dcsbios'), 'StringBuffer')(parser_hook, 0x0000, 16, partial(self.detecting_plane))
        self.parser = parser_hook
        self.plane_name = ''
        self.plane_detected = False
        self.already_pressed = False
        self.buttons: Tuple[int, ...] = (0,)
        self._display: List[str] = list()
        self.lcd = kwargs.get('lcd_type', LcdMono)
        lcd_sdk.logi_lcd_init('DCS World', self.lcd.type)
        self.plane = Aircraft(self.lcd)

    @property
    def display(self) -> List[str]:
        """
        Get latest set text at LCD.

        :return: list of strings with data, row by row
        :rtype: List[str]
        """
        return self._display

    @display.setter
    def display(self, message: List[str]) -> None:
        """
        Display message at LCD.

        For G13/G15/G510 takes first 4 or less elements of list and display as 4 rows.
        For G19 takes first 8 or less elements of list and display as 8 rows.

        :param message: List of strings to display, row by row.
        :type message: List[str]
        """
        self._display = message
        # todo: use settext form sdk
        img = self._prepare_image()
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
                LOG.info(f'Detected Aircraft: {value}')
                self.display = ['Detected aircraft:', self.plane_name]
                self.plane_detected = True
            else:
                LOG.warning(f'Not supported aircraft: {value}')
                self.display = ['Detected aircraft:', self.plane_name, 'Not supported yet!']

    def load_new_plane(self) -> None:
        """
        Dynamic load of new detected aircraft.

        Setup callbacks for detected plane inside DCS-BIOS parser.
        """
        self.plane_detected = False
        self.plane = getattr(import_module('dcspy.aircrafts'), self.plane_name)(self.lcd)
        LOG.debug(f'Dynamic load of: {self.plane_name} as {SUPPORTED_CRAFTS[self.plane_name]}')
        for field_name, proto_data in self.plane.bios_data.items():
            buffer = getattr(import_module('dcspy.dcsbios'), proto_data['class'])
            buffer(parser=self.parser, callback=partial(self.plane.set_bios, field_name), **proto_data['args'])

    def check_buttons(self) -> int:
        """
        Check if button was pressed and return its number.

        For G13/G15/G510: 1-4
        For G19 9-15: LEFT = 9, RIGHT = 10, OK = 11, CANCEL = 12, UP = 13, DOWN = 14, MENU = 15

        :return: number of pressed button
        :rtype: int
        """
        for btn in self.buttons:
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
        * fetch DCS-BIOS request from current plane
        * sent it action to DCS-BIOS via. network socket

        :param sock: network socket
        :type sock: socket
        """
        button = self.check_buttons()
        if button:
            sock.sendto(bytes(self.plane.button_request(button), 'utf-8'), SEND_ADDR)

    def clear(self, true_clear=False):
        """
        Clear LCD.

        :param true_clear:
        """
        LOG.debug(f'Clear LCD type: {self.lcd.type}')
        lcd_sdk.clear_display(true_clear)

    def _prepare_image(self) -> Image.Image:
        """
        Prepare image for base of LCD type.

        For G13/G15/G510 takes first 4 or less elements of list and display as 4 rows.
        For G19 takes first 8 or less elements of list and display as 8 rows.

        :return: image instance ready display on LCD
        """
        raise NotImplementedError

    def __str__(self):
        return f'{self.__class__.__name__}: {self.lcd.width}x{self.lcd.height}'

    def __repr__(self):
        return f'{super().__repr__()} with: {self.__dict__}'


class KeyboardMono(LogitechKeyboard):
    def __init__(self, parser_hook: ProtocolParser) -> None:
        """
        Logitech keyboard with mono LCD.

        Support for: G510, G13, G15 (v1 and v2)

        :param parser_hook: BSC-BIOS parser
        :type parser_hook: ProtocolParser
        """
        super().__init__(parser_hook, lcd_type=LcdMono)
        self.buttons = (lcd_sdk.MONO_BUTTON_0, lcd_sdk.MONO_BUTTON_1, lcd_sdk.MONO_BUTTON_2, lcd_sdk.MONO_BUTTON_3)

    def _prepare_image(self) -> Image.Image:
        """
        Prepare image for base of Mono LCD.

        For G13/G15/G510 takes first 4 or less elements of list and display as 4 rows.

        :return: image instance ready display on LCD
        """
        # todo extract color to Logitech
        img = Image.new(mode='1', size=(self.lcd.width, self.lcd.height), color=0)
        draw = ImageDraw.Draw(img)
        fill, font, space = 255, FONT[11], 10
        # todo: use settext form sdk
        for line_no, line in enumerate(self._display):
            draw.text(xy=(0, space * line_no), text=line, fill=fill, font=font)
        return img


class KeyboardColor(LogitechKeyboard):
    def __init__(self, parser_hook: ProtocolParser) -> None:
        """
        Logitech keyboard with color LCD.

        Support for: G19

        :param parser_hook: BSC-BIOS parser
        :type parser_hook: ProtocolParser
        """
        super().__init__(parser_hook, lcd_type=LcdColor)
        self.buttons = (lcd_sdk.COLOR_BUTTON_LEFT, lcd_sdk.COLOR_BUTTON_RIGHT, lcd_sdk.COLOR_BUTTON_OK,
                        lcd_sdk.COLOR_BUTTON_CANCEL, lcd_sdk.COLOR_BUTTON_UP, lcd_sdk.COLOR_BUTTON_DOWN,
                        lcd_sdk.COLOR_BUTTON_MENU)

    def _prepare_image(self) -> Image.Image:
        """
        Prepare image for base of Color LCD.

        For G19 takes first 8 or less elements of list and display as 8 rows.

        :return: image instance ready display on LCD
        """
        # todo extract color to Logitech
        img = Image.new(mode='RGBA', size=(self.lcd.width, self.lcd.height), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        fill, font, space = (0, 255, 0, 255), FONT[22], 40
        # todo: use settext form sdk
        for line_no, line in enumerate(self._display):
            draw.text(xy=(0, space * line_no), text=line, fill=fill, font=font)
        return img
