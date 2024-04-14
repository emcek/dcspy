from functools import partial
from importlib import import_module
from logging import getLogger
from pathlib import Path
from pprint import pformat
from socket import socket
from time import sleep
from typing import Union

from PIL import Image, ImageDraw

from dcspy import dcsbios, get_config_yaml_item
from dcspy.aircraft import BasicAircraft, MetaAircraft
from dcspy.models import KEY_DOWN, SEND_ADDR, SUPPORTED_CRAFTS, TIME_BETWEEN_REQUESTS, Gkey, LcdButton, LcdType, LogitechDeviceModel, MouseButton
from dcspy.sdk import key_sdk, lcd_sdk
from dcspy.utils import get_full_bios_for_plane, get_planes_list

LOG = getLogger(__name__)


class LogitechDevice:
    """General Logitech device."""

    def __init__(self, parser: dcsbios.ProtocolParser, sock: socket, model: LogitechDeviceModel) -> None:
        """
        General Logitech device.

        :param parser: DCS-BIOS parser instance
        :param sock: multicast UDP socket
        :param model: device model
        """
        dcsbios.StringBuffer(parser=parser, address=0x0, max_length=0x10, callback=partial(self.detecting_plane))
        self.parser = parser
        self.socket = sock
        self.plane_name = ''
        self.bios_name = ''
        self.plane_detected = False
        self.lcdbutton_pressed = False
        self._display: list[str] = []
        self.model = model
        self.lcd_sdk = lcd_sdk.LcdSdkManager(name='DCS World', lcd_type=self.model.lcd_info.type)
        self.key_sdk = key_sdk.GkeySdkManager(self.gkey_callback_handler)
        success = self.key_sdk.logi_gkey_init()
        LOG.debug(f'G-Key is connected: {success}')
        self.plane = BasicAircraft(self.model.lcd_info)

    @property
    def display(self) -> list[str]:
        """
        Get the latest text from LCD.

        :return: list of strings with data, row by row
        """
        return self._display

    @display.setter
    def display(self, message: list[str]) -> None:
        """
        Display message as image at LCD.

        For G13/G15/G510 takes first 4 or fewer elements of list and display as 4 rows.
        For G19 takes first 8 or fewer elements of list and display as 8 rows.
        :param message: List of strings to display, row by row.
        """
        self._display = message
        if self.model.lcd_info.type != LcdType.NONE:
            self.lcd_sdk.update_display(self._prepare_image())

    def text(self, message: list[str]) -> None:
        """
        Display message at LCD.

        For G13/G15/G510 takes first 4 or fewer elements of list and display as 4 rows.
        For G19 takes first 8 or fewer elements of list and display as 8 rows.
        :param message: List of strings to display, row by row.
        """
        if self.model.lcd_info.type != LcdType.NONE:
            self.lcd_sdk.update_text(message)

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

    def unload_old_plane(self):
        """Unloads the previous plane by remove all callbacks and keep only one."""
        LOG.debug(f'Unload start: {self.plane_name} Number of callbacks: {len(self.parser.write_callbacks)}')
        for partial_obj in self.parser.write_callbacks:
            for callback in partial_obj.func.__self__.callbacks:
                if callback.func.__name__ == 'detecting_plane':
                    self.parser.write_callbacks = {partial_obj}
            if len(self.parser.write_callbacks) == 1:
                break

    def load_new_plane(self) -> None:
        """
        Dynamic load of new detected aircraft.

        Setup callbacks for detected plane inside DCS-BIOS parser.
        """
        self.plane_detected = False
        if self.plane_name in SUPPORTED_CRAFTS:
            lcd_update_func = self.lcd_sdk.update_display if self.model.lcd_info.type != LcdType.NONE else None
            self.plane = getattr(import_module('dcspy.aircraft'), self.plane_name)(self.model.lcd_info, update_display=lcd_update_func)
            LOG.debug(f'Dynamic load of: {self.plane_name} as AdvancedAircraft | BIOS: {self.plane.bios_name}')
            self._setup_plane_callback()
        else:
            self.plane = MetaAircraft(self.plane_name, (BasicAircraft,), {})(self.model.lcd_info)
            self.plane.bios_name = self.bios_name
            LOG.debug(f'Dynamic load of: {self.plane_name} as BasicAircraft | BIOS: {self.plane.bios_name}')
        LOG.debug(f'{repr(self)}')

    def _setup_plane_callback(self):
        """Setups DCS-BIOS parser callbacks for detected plane."""
        plane_bios = get_full_bios_for_plane(plane=SUPPORTED_CRAFTS[self.plane_name]['bios'], bios_dir=Path(str(get_config_yaml_item('dcsbios'))))
        for ctrl_name in self.plane.bios_data:
            ctrl = plane_bios.get_ctrl(ctrl_name=ctrl_name)
            dcsbios_buffer = getattr(dcsbios, ctrl.output.klass)
            dcsbios_buffer(parser=self.parser, callback=partial(self.plane.set_bios, ctrl_name), **ctrl.output.args.model_dump())

    def gkey_callback_handler(self, key_idx: int, mode: int, key_down: int, mouse: int) -> None:
        """
        Logitech G-Key callback handler.

        Send action to DCS-BIOS via network socket.

        :param key_idx: index number of G-Key
        :param mode: mode of G-Key
        :param key_down: key state, 1 - pressed, 0 - released
        :param mouse: indicate if the Event comes from a mouse, 1 is yes, 0 is no

        """
        key = Gkey(key=key_idx, mode=mode)
        if mouse:
            key = MouseButton(button=key_idx)  # type: ignore[assignment]
        LOG.debug(f'Button {key} is pressed, key down: {key_down}')
        self._send_request(button=key, key_down=key_down)

    def check_buttons(self) -> LcdButton:
        """
        Check if button was pressed and return it`s enum.

        :return: LcdButton enum of pressed button
        """
        for lcd_btn in self.model.lcd_keys:
            if self.lcd_sdk.logi_lcd_is_button_pressed(lcd_btn):
                if not self.lcdbutton_pressed:
                    self.lcdbutton_pressed = True
                    return LcdButton(lcd_btn)
                return LcdButton.NONE
        self.lcdbutton_pressed = False
        return LcdButton.NONE

    def button_handle(self) -> None:
        """
        Button handler.

        * detect if button was pressed
        * sent action to DCS-BIOS via network socket
        """
        if self.model.lcd_info.type != LcdType.NONE:
            button = self.check_buttons()
            if button.value:
                self._send_request(button, key_down=KEY_DOWN)

    def _send_request(self, button: Union[LcdButton, Gkey, MouseButton], key_down: int) -> None:
        """
        Sent action to DCS-BIOS via network socket.

        :param button: LcdButton, Gkey or MouseButton
        :param key_down: 1 indicate when G-Key was push down, 0 when G-Key is up
        """
        req_model = self.plane.button_request(button)
        for request in req_model.bytes_requests(key_down=key_down):
            LOG.debug(f'{button=}: {request=}')
            self.socket.sendto(request, SEND_ADDR)
            sleep(TIME_BETWEEN_REQUESTS)

    def clear(self, true_clear=False) -> None:
        """
        Clear LCD.

        :param true_clear:
        """
        if self.model.lcd_info.type != LcdType.NONE:
            LOG.debug(f'Clear LCD type: {self.model.lcd_info.type}')
            self.lcd_sdk.clear_display(true_clear)

    def _prepare_image(self) -> Image.Image:
        """
        Prepare image for base of LCD type.

        For G13/G15/G510 takes first 4 or fewer elements of list and display as 4 rows.
        For G19 takes first 8 or fewer elements of list and display as 8 rows.
        :return: image instance ready display on LCD
        """
        img = Image.new(mode=self.model.lcd_info.mode.value, color=self.model.lcd_info.background,
                        size=(self.model.lcd_info.width.value, self.model.lcd_info.height.value))
        draw = ImageDraw.Draw(img)
        for line_no, line in enumerate(self._display):
            draw.text(xy=(0, self.model.lcd_info.line_spacing * line_no), text=line, fill=self.model.lcd_info.foreground, font=self.model.lcd_info.font_s)
        return img

    def __str__(self) -> str:
        return f'{type(self).__name__}: {self.model.lcd_info.width.value}x{self.model.lcd_info.height.value}'

    def __repr__(self) -> str:
        return f'{super().__repr__()} with: {pformat(self.__dict__)}'
