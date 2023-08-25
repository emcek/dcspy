from functools import partial
from importlib import import_module
from logging import getLogger
from pprint import pformat
from socket import socket
from time import sleep
from typing import List, Sequence, Union

from PIL import Image, ImageDraw

from dcspy import (SEND_ADDR, SUPPORTED_CRAFTS, Gkey, LcdButton, LcdColor,
                   LcdMono, generate_gkey)
from dcspy.aircraft import Aircraft
from dcspy.dcsbios import ProtocolParser
from dcspy.sdk import key_sdk, lcd_sdk

LOG = getLogger(__name__)


class KeyboardManager:
    """General keyboard with LCD from Logitech."""
    def __init__(self, parser: ProtocolParser, **kwargs) -> None:
        """
        General keyboard with LCD from Logitech.

        It can be easily extended for any of:
        - Mono LCD: G13, G15 (v1 and v2) and G510
        - RGB LCD: G19

        However, it defines a bunch of functionally to be used be child class:
        - DCS-BIOS callback for currently used aircraft in DCS
        - auto-detecting aircraft and load its handling class
        - send button request to DCS-BIOS

        Child class needs redefine:
        - pass lcd_type argument as LcdInfo to super constructor

        :param parser: DCS-BIOS parser instance
        """
        detect_plane = {'parser': parser, 'address': 0x0, 'max_length': 0x10, 'callback': partial(self.detecting_plane)}
        getattr(import_module('dcspy.dcsbios'), 'StringBuffer')(**detect_plane)
        self.parser = parser
        self.plane_name = ''
        self.plane_detected = False
        self.lcdbutton_pressed = False
        self.gkey_pressed = False
        self._display: List[str] = []
        self.lcd = kwargs.get('lcd_type', LcdMono)
        self.gkey: Sequence[Gkey] = ()
        self.buttons: Sequence[LcdButton] = ()
        lcd_sdk.logi_lcd_init('DCS World', self.lcd.type.value)
        key_sdk.logi_gkey_init()
        self.plane = Aircraft(self.lcd)
        self.vert_space = 0

    @property
    def display(self) -> List[str]:
        """
        Get the latest text from LCD.

        :return: list of strings with data, row by row
        """
        return self._display

    @display.setter
    def display(self, message: List[str]) -> None:
        """
        Display message as image at LCD.

        For G13/G15/G510 takes first 4 or fewer elements of list and display as 4 rows.
        For G19 takes first 8 or fewer elements of list and display as 8 rows.
        :param message: List of strings to display, row by row.
        """
        self._display = message
        lcd_sdk.update_display(self._prepare_image())

    @staticmethod
    def text(message: List[str]) -> None:
        """
        Display message at LCD.

        For G13/G15/G510 takes first 4 or fewer elements of list and display as 4 rows.
        For G19 takes first 8 or fewer elements of list and display as 8 rows.
        :param message: List of strings to display, row by row.
        """
        lcd_sdk.update_text(message)

    def detecting_plane(self, value: str) -> None:
        """
        Try to detect airplane base on value received from DCS-BIOS.

        :param value: data from DCS-BIOS
        """
        short_name = value.replace('-', '').replace('_', '')
        if self.plane_name != short_name:
            self.plane_name = short_name
            if self.plane_name in SUPPORTED_CRAFTS:
                LOG.info(f'Detected Aircraft: {value}')
                self.display = ['Detected aircraft:', SUPPORTED_CRAFTS[self.plane_name]['name']]
                self.plane_detected = True
            elif self.plane_name not in SUPPORTED_CRAFTS and self.plane_name:
                LOG.warning(f'Not supported aircraft: {value}')
                self.display = ['Detected aircraft:', self.plane_name, 'Not supported yet!']

    def load_new_plane(self) -> None:
        """
        Dynamic load of new detected aircraft.

        Setup callbacks for detected plane inside DCS-BIOS parser.
        """
        self.plane_detected = False
        self.plane = getattr(import_module('dcspy.aircraft'), self.plane_name)(self.lcd)
        LOG.debug(f'Dynamic load of: {self.plane_name} as {SUPPORTED_CRAFTS[self.plane_name]["name"]}')
        LOG.debug(f'{repr(self)}')
        for field_name, proto_data in self.plane.bios_data.items():
            dcsbios_buffer = getattr(import_module('dcspy.dcsbios'), proto_data['klass'])
            dcsbios_buffer(parser=self.parser, callback=partial(self.plane.set_bios, field_name), **proto_data['args'])

    def check_buttons(self) -> LcdButton:
        """
        Check if button was pressed and return it`s enum.

        :return: LcdButton enum of pressed button
        """
        for btn in self.buttons:
            if lcd_sdk.logi_lcd_is_button_pressed(btn.value):
                if not self.lcdbutton_pressed:
                    self.lcdbutton_pressed = True
                    return LcdButton(btn)
                return LcdButton.NONE
        self.lcdbutton_pressed = False
        return LcdButton.NONE

    def check_gkey(self) -> Gkey:
        """
        Check if G-Key was pressed and return it`s enum.

        :return: Gkey enum of pressed button
        """
        for key in self.gkey:
            if key_sdk.logi_gkey_is_keyboard_gkey_pressed(g_key=key.key, mode=key.mode):
                gkey = key_sdk.logi_gkey_is_keyboard_gkey_string(g_key=key.key, mode=key.mode).replace('/', '_')
                LOG.debug(f"Button {gkey} is pressed")
                if not self.gkey_pressed:
                    self.gkey_pressed = True
                    return key
                return Gkey(0, 0)
        self.gkey_pressed = False
        return Gkey(0, 0)

    def button_handle(self, sock: socket) -> None:
        """
        Button handler.

        * detect if button was pressed
        * fetch DCS-BIOS request from current plane
        * sent action to DCS-BIOS via network socket
        :param sock: network socket
        """
        button = self.check_buttons()
        gkey = self.check_gkey()
        if button.value:
            self._send_request(button, sock)
        if gkey:
            self._send_request(gkey, sock)

    def _send_request(self, button: Union[LcdButton, Gkey], sock) -> None:
        """
        Sent action to DCS-BIOS via network socket.

        :param button: LcdButton or Gkey
        :param sock: network socket
        """
        for request in self.plane.button_request(button).split('|'):
            sock.sendto(bytes(request, 'utf-8'), SEND_ADDR)
            sleep(0.05)

    def clear(self, true_clear=False) -> None:
        """
        Clear LCD.

        :param true_clear:
        """
        LOG.debug(f'Clear LCD type: {self.lcd.type}')
        lcd_sdk.clear_display(true_clear)

    def _prepare_image(self) -> Image.Image:
        """
        Prepare image for base of LCD type.

        For G13/G15/G510 takes first 4 or fewer elements of list and display as 4 rows.
        For G19 takes first 8 or fewer elements of list and display as 8 rows.
        :return: image instance ready display on LCD
        """
        img = Image.new(mode=self.lcd.mode.value, size=(self.lcd.width, self.lcd.height), color=self.lcd.background)
        draw = ImageDraw.Draw(img)
        for line_no, line in enumerate(self._display):
            draw.text(xy=(0, self.vert_space * line_no), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)
        return img

    def __str__(self) -> str:
        return f'{type(self).__name__}: {self.lcd.width}x{self.lcd.height}'

    def __repr__(self) -> str:
        return f'{super().__repr__()} with: {pformat(self.__dict__)}'


class G13(KeyboardManager):
    """Logitech`s keyboard with mono LCD."""
    def __init__(self, parser: ProtocolParser) -> None:
        """
        Logitech`s keyboard with mono LCD.

        Support for: G13
        :param parser: DCS-BIOS parser instance
        """
        super().__init__(parser, lcd_type=LcdMono)
        self.buttons = (LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR)
        self.gkey = generate_gkey(key=29, mode=3)
        self.vert_space = 10


class G510(KeyboardManager):
    """Logitech`s keyboard with mono LCD."""
    def __init__(self, parser: ProtocolParser) -> None:
        """
        Logitech`s keyboard with mono LCD.

        Support for: G510
        :param parser: DCS-BIOS parser instance
        """
        super().__init__(parser, lcd_type=LcdMono)
        self.buttons = (LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR)
        self.gkey = generate_gkey(key=18, mode=13)
        self.vert_space = 10


class G15v1(KeyboardManager):
    """Logitech`s keyboard with mono LCD."""
    def __init__(self, parser: ProtocolParser) -> None:
        """
        Logitech`s keyboard with mono LCD.

        Support for: G15 v1
        :param parser: DCS-BIOS parser instance
        """
        super().__init__(parser, lcd_type=LcdMono)
        self.buttons = (LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR)
        self.gkey = generate_gkey(key=18, mode=3)
        self.vert_space = 10


class G15v2(KeyboardManager):
    """Logitech`s keyboard with mono LCD."""
    def __init__(self, parser: ProtocolParser) -> None:
        """
        Logitech`s keyboard with mono LCD.

        Support for: G15 v2
        :param parser: DCS-BIOS parser instance
        """
        super().__init__(parser, lcd_type=LcdMono)
        self.buttons = (LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR)
        self.gkey = generate_gkey(key=6, mode=3)
        self.vert_space = 10


class G19(KeyboardManager):
    """Logitech`s keyboard with color LCD."""
    def __init__(self, parser: ProtocolParser) -> None:
        """
        Logitech`s keyboard with color LCD.

        Support for: G19
        :param parser: DCS-BIOS parser instance
        """
        super().__init__(parser, lcd_type=LcdColor)
        self.buttons = (LcdButton.LEFT, LcdButton.RIGHT, LcdButton.UP, LcdButton.DOWN, LcdButton.OK, LcdButton.CANCEL, LcdButton.MENU)
        self.gkey = generate_gkey(key=12, mode=3)
        self.vert_space = 40
