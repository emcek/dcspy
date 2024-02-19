from functools import partial
from importlib import import_module
from logging import getLogger
from pathlib import Path
from pprint import pformat
from socket import socket
from time import sleep
from typing import List, Sequence, Union

from PIL import Image, ImageDraw

from dcspy import get_config_yaml_item
from dcspy.aircraft import BasicAircraft, MetaAircraft
from dcspy.dcsbios import ProtocolParser
from dcspy.models import (SEND_ADDR, SUPPORTED_CRAFTS, TIME_BETWEEN_REQUESTS, Gkey, KeyboardModel, LcdButton, LcdColor, LcdMono, ModelG13, ModelG15v1,
                          ModelG15v2, ModelG19, ModelG510)
from dcspy.sdk import lcd_sdk
from dcspy.sdk.key_sdk import GkeySdkManager
from dcspy.utils import get_full_bios_for_plane, get_planes_list

LOG = getLogger(__name__)


class KeyboardManager:
    """General keyboard with LCD from Logitech."""
    def __init__(self, parser: ProtocolParser, sock: socket, **kwargs) -> None:
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
        :param sock: multicast UDP socket
        """
        detect_plane = {'parser': parser, 'address': 0x0, 'max_length': 0x10, 'callback': partial(self.detecting_plane)}
        getattr(import_module('dcspy.dcsbios'), 'StringBuffer')(**detect_plane)
        self.parser = parser
        self.socket = sock
        self.plane_name = ''
        self.bios_name = ''
        self.plane_detected = False
        self.lcdbutton_pressed = False
        self.gkey_pressed = False
        self._display: List[str] = []
        self.lcd = kwargs.get('lcd_type', LcdMono)
        self.model = KeyboardModel(name='', klass='', modes=0, gkeys=0, lcdkeys=(LcdButton.NONE,), lcd='mono')
        self.gkey: Sequence[Gkey] = ()
        self.buttons: Sequence[LcdButton] = ()
        lcd_sdk.logi_lcd_init('DCS World', self.lcd.type.value)
        key_sdk = GkeySdkManager(self.gkey_callback_handler)
        success = key_sdk.logi_gkey_init()
        LOG.info(f'logitech gkey sdk initialised: {success}')
        self.plane = BasicAircraft(self.lcd)
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
            planes_list = get_planes_list(bios_dir=Path(str(get_config_yaml_item('dcsbios'))))
            if self.plane_name in SUPPORTED_CRAFTS:
                LOG.info(f'Advanced supported aircraft: {value}')
                self.display = ['Detected aircraft:', SUPPORTED_CRAFTS[self.plane_name]['name']]
                self.plane_detected = True
            elif self.plane_name not in SUPPORTED_CRAFTS and value in planes_list:
                LOG.info(f'Basic supported aircraft: {value}')
                self.bios_name = value
                self.display = ['Detected aircraft:', value]
                self.plane_detected = True
            elif value not in planes_list:
                LOG.warning(f'Not supported aircraft: {value}')
                self.display = ['Detected aircraft:', value, 'Not supported yet!']

    def load_new_plane(self) -> None:
        """
        Dynamic load of new detected aircraft.

        Setup callbacks for detected plane inside DCS-BIOS parser.
        """
        self.plane_detected = False
        if self.plane_name in SUPPORTED_CRAFTS:
            self.plane = getattr(import_module('dcspy.aircraft'), self.plane_name)(self.lcd)
            LOG.debug(f'Dynamic load of: {self.plane_name} as AdvancedAircraft | BIOS: {self.plane.bios_name}')
            self._setup_plane_callback()
        else:
            self.plane = MetaAircraft(self.plane_name, (BasicAircraft,), {})(self.lcd)
            self.plane.bios_name = self.bios_name
            LOG.debug(f'Dynamic load of: {self.plane_name} as BasicAircraft | BIOS: {self.plane.bios_name}')
        LOG.debug(f'{repr(self)}')

    def _setup_plane_callback(self):
        """Setups DCS-BIOS parser callbacks for detected plane."""
        plane_bios = get_full_bios_for_plane(plane=SUPPORTED_CRAFTS[self.plane_name]['bios'], bios_dir=Path(str(get_config_yaml_item('dcsbios'))))
        for ctrl_name in self.plane.bios_data:
            ctrl = plane_bios.get_ctrl(ctrl_name=ctrl_name)
            dcsbios_buffer = getattr(import_module('dcspy.dcsbios'), ctrl.output.klass)
            dcsbios_buffer(parser=self.parser, callback=partial(self.plane.set_bios, ctrl_name), **ctrl.output.args.model_dump())

    def gkey_callback_handler(self, key_idx: int, mode: int, key_down: int) -> None:
        """
        Logitech G-Key callback handler.

        Send action to DCS-BIOS via network socket.

        :param key_idx: index number of G-Key
        :param mode: mode of G-Key
        :param key_down: key state, 1 - pressed, 0 - released
        """
        gkey = Gkey(key=key_idx, mode=mode)
        LOG.debug(f'Button {gkey} is pressed, key down: {key_down}')
        gkey_request = self.plane.button_request(gkey)
        if gkey_request:
            if 'BUTTON' in gkey_request:
                gkey_request = gkey_request.split(' BUTTON')[0]
                request = f'{gkey_request} {key_down}\n'
                self._send_request(request)
            elif not key_down:
                return
            else:
                self._send_request(gkey)

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

    def button_handle(self) -> None:
        """
        Button handler.

        * detect if button was pressed
        * fetch DCS-BIOS request from current plane
        * sent action to DCS-BIOS via network socket
        """
        button = self.check_buttons()
        if button.value:
            self._send_request(button)

    def _send_request(self, btn_or_str: Union[LcdButton, Gkey, str], /) -> None:
        """
        Sent action to DCS-BIOS via network socket.

        :param btn_or_str: LcdButton, Gkey or request string
        """
        if isinstance(btn_or_str, (LcdButton, Gkey)):
            for request in self.plane.button_request(btn_or_str).split('|'):
                self.socket.sendto(bytes(request, 'utf-8'), SEND_ADDR)
                sleep(TIME_BETWEEN_REQUESTS)
        else:
            self.socket.sendto(bytes(btn_or_str, 'utf-8'), SEND_ADDR)

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
    def __init__(self, parser: ProtocolParser, sock: socket, **kwargs) -> None:
        """
        Logitech`s keyboard with mono LCD.

        Support for: G13
        :param parser: DCS-BIOS parser instance
        """
        LcdMono.set_fonts(kwargs['fonts'])
        super().__init__(parser, sock, lcd_type=LcdMono)
        self.model = ModelG13
        self.buttons = (LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR)
        self.gkey = Gkey.generate(key=self.model.gkeys, mode=self.model.modes)
        self.vert_space = 10


class G510(KeyboardManager):
    """Logitech`s keyboard with mono LCD."""
    def __init__(self, parser: ProtocolParser, sock: socket, **kwargs) -> None:
        """
        Logitech`s keyboard with mono LCD.

        Support for: G510
        :param parser: DCS-BIOS parser instance
        :param sock: multicast UDP socket
        """
        LcdMono.set_fonts(kwargs['fonts'])
        super().__init__(parser, sock, lcd_type=LcdMono)
        self.model = ModelG510
        self.buttons = (LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR)
        self.gkey = Gkey.generate(key=self.model.gkeys, mode=self.model.modes)
        self.vert_space = 10


class G15v1(KeyboardManager):
    """Logitech`s keyboard with mono LCD."""
    def __init__(self, parser: ProtocolParser, sock: socket, **kwargs) -> None:
        """
        Logitech`s keyboard with mono LCD.

        Support for: G15 v1
        :param parser: DCS-BIOS parser instance
        :param sock: multicast UDP socket
        """
        LcdMono.set_fonts(kwargs['fonts'])
        super().__init__(parser, sock, lcd_type=LcdMono)
        self.model = ModelG15v1
        self.buttons = (LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR)
        self.gkey = Gkey.generate(key=self.model.gkeys, mode=self.model.modes)
        self.vert_space = 10


class G15v2(KeyboardManager):
    """Logitech`s keyboard with mono LCD."""
    def __init__(self, parser: ProtocolParser, sock: socket, **kwargs) -> None:
        """
        Logitech`s keyboard with mono LCD.

        Support for: G15 v2
        :param parser: DCS-BIOS parser instance
        :param sock: multicast UDP socket
        """
        LcdMono.set_fonts(kwargs['fonts'])
        super().__init__(parser, sock, lcd_type=LcdMono)
        self.model = ModelG15v2
        self.buttons = (LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR)
        self.gkey = Gkey.generate(key=self.model.gkeys, mode=self.model.modes)
        self.vert_space = 10


class G19(KeyboardManager):
    """Logitech`s keyboard with color LCD."""
    def __init__(self, parser: ProtocolParser, sock: socket, **kwargs) -> None:
        """
        Logitech`s keyboard with color LCD.

        Support for: G19
        :param parser: DCS-BIOS parser instance
        :param sock: multicast UDP socket
        """
        LcdColor.set_fonts(kwargs['fonts'])
        super().__init__(parser, sock, lcd_type=LcdColor)
        self.model = ModelG19
        self.buttons = (LcdButton.LEFT, LcdButton.RIGHT, LcdButton.UP, LcdButton.DOWN, LcdButton.OK, LcdButton.CANCEL, LcdButton.MENU)
        self.gkey = Gkey.generate(key=self.model.gkeys, mode=self.model.modes)
        self.vert_space = 40
