from ctypes import c_ubyte, sizeof, c_void_p
from functools import partial
from importlib import import_module
from logging import basicConfig, DEBUG, info, debug, warning
from math import log2
from platform import architecture
from socket import socket
from sys import maxsize
from typing import List

from PIL import Image, ImageFont, ImageDraw

from dcspy import SUPPORTED_CRAFTS
from dcspy.aircrafts import AircraftHandler
from dcspy.dcsbios import StringBuffer, ProtocolParser
from dcspy.sdk import lcd_sdk

basicConfig(format='%(asctime)s | %(levelname)-7s | %(message)s / %(filename)s:%(lineno)d', level=DEBUG)


class G13:
    def __init__(self, parser_hook: ProtocolParser) -> None:
        """
        Basic constructor.

        :param parser_hook:
        """
        self.bufferAC = StringBuffer(parser_hook, 0x0000, 16, lambda val: self.set_ac(value=val))
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
        self.font1 = ImageFont.truetype('consola.ttf', 11)
        self.font2 = ImageFont.truetype('consola.ttf', 16)

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
            self.draw.text((0, 10 * line_no), line, 1, self.font1)
        self.update_display(self.img)

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
        plane: AircraftHandler = getattr(import_module('dcspy.aircrafts'), plane_name)(self)
        debug(f'Dynamic load of: {plane_name} as {self.currentAC}')
        self.currentACHook = plane
        from copy import deepcopy
        for field_name, add_data in plane.bios_data.items():
            debug(f'{field_name} {add_data["addr"]} {add_data["length"]}')
            # field_val = StringBuffer(self.parser, add_data['addr'], add_data['length'], lambda s: plane.set_data(field_name, s))
            field_val = StringBuffer(self.parser, add_data['addr'], add_data['length'], partial(plane.set_data, field_name))
            debug(f'{plane} buffer{field_name} {field_val}')
            setattr(plane, f'buffer{deepcopy(field_name)}', field_val)
            del field_val

        # bufferScratchpadStr1 = StringBuffer(self.parser, 0x744e, 2, lambda s: plane.set_data('ScratchpadStr1', s))
        # bufferScratchpadStr2 = StringBuffer(self.parser, 0x7450, 2, lambda s: plane.set_data('ScratchpadStr2', s))
        # bufferScratchpadNum = StringBuffer(self.parser, 0x7446, 8, lambda s: plane.set_data('ScratchpadNum', s))
        # bufferCOMM1 = StringBuffer(self.parser, 0x7424, 2, lambda s: plane.set_data('COMM1', s))
        # bufferCOMM2 = StringBuffer(self.parser, 0x7426, 2, lambda s: plane.set_data('COMM2', s))
        # bufferFuelTotal = StringBuffer(self.parser, 0x748a, 6, lambda s: plane.set_data('FuelTotal', s))
        # bufferOptionDisplay1 = StringBuffer(self.parser, 0x7432, 4, lambda s: plane.set_data('OptionDisplay1', s))
        # bufferOptionDisplay2 = StringBuffer(self.parser, 0x7436, 4, lambda s: plane.set_data('OptionDisplay2', s))
        # bufferOptionDisplay3 = StringBuffer(self.parser, 0x743a, 4, lambda s: plane.set_data('OptionDisplay3', s))
        # bufferOptionDisplay4 = StringBuffer(self.parser, 0x743e, 4, lambda s: plane.set_data('OptionDisplay4', s))
        # bufferOptionDisplay5 = StringBuffer(self.parser, 0x7442, 4, lambda s: plane.set_data('OptionDisplay5', s))
        # bufferOptionCueing1 = StringBuffer(self.parser, 0x7428, 1, lambda s: plane.set_data('OptionCueing1', s))
        # bufferOptionCueing2 = StringBuffer(self.parser, 0x742a, 1, lambda s: plane.set_data('OptionCueing2', s))
        # bufferOptionCueing3 = StringBuffer(self.parser, 0x742c, 1, lambda s: plane.set_data('OptionCueing3', s))
        # bufferOptionCueing4 = StringBuffer(self.parser, 0x742e, 1, lambda s: plane.set_data('OptionCueing4', s))
        # bufferOptionCueing5 = StringBuffer(self.parser, 0x7430, 1, lambda s: plane.set_data('OptionCueing5', s))
        # setattr(plane, 'bufferOptionDisplay1', bufferOptionDisplay1)
        # setattr(plane, 'bufferOptionDisplay2', bufferOptionDisplay2)
        # setattr(plane, 'bufferOptionDisplay3', bufferOptionDisplay3)
        # setattr(plane, 'bufferOptionDisplay4', bufferOptionDisplay4)
        # setattr(plane, 'bufferOptionDisplay5', bufferOptionDisplay5)
        # setattr(plane, 'bufferOptionCueing1', bufferOptionCueing1)
        # setattr(plane, 'bufferOptionCueing2', bufferOptionCueing2)
        # setattr(plane, 'bufferOptionCueing3', bufferOptionCueing3)
        # setattr(plane, 'bufferOptionCueing4', bufferOptionCueing4)
        # setattr(plane, 'bufferOptionCueing5', bufferOptionCueing5)
        # setattr(plane, 'bufferScratchpadStr1', bufferScratchpadStr1)
        # setattr(plane, 'bufferScratchpadStr2', bufferScratchpadStr2)
        # setattr(plane, 'bufferScratchpadNum', bufferScratchpadNum)
        # setattr(plane, 'bufferCOMM1', bufferCOMM1)
        # setattr(plane, 'bufferCOMM2', bufferCOMM2)
        # setattr(plane, 'bufferFuelTotal', bufferFuelTotal)

        bios_data = {
            'ScratchpadStr1': {'addr': 0x744e, 'length': 2},
            'ScratchpadStr2': {'addr': 0x7450, 'length': 2},
            'ScratchpadNum': {'addr': 0x7446, 'length': 8},
            'OptionDisplay1': {'addr': 0x7432, 'length': 4},
            'OptionDisplay2': {'addr': 0x7436, 'length': 4},
            'OptionDisplay3': {'addr': 0x743a, 'length': 4},
            'OptionDisplay4': {'addr': 0x743e, 'length': 4},
            'OptionDisplay5': {'addr': 0x7442, 'length': 4},
            'COMM1': {'addr': 0x7424, 'length': 2},
            'COMM2': {'addr': 0x7426, 'length': 2},
            'OptionCueing1': {'addr': 0x7428, 'length': 1},
            'OptionCueing2': {'addr': 0x742a, 'length': 1},
            'OptionCueing3': {'addr': 0x742c, 'length': 1},
            'OptionCueing4': {'addr': 0x742e, 'length': 1},
            'OptionCueing5': {'addr': 0x7430, 'length': 1},
            'FuelTotal': {'addr': 0x748a, 'length': 6}}
        for field_name, add_data in bios_data.items():
            field_val = StringBuffer(self.parser, add_data['addr'], add_data['length'], lambda s: plane.set_data(field_name, s))
            setattr(plane, f'buffer{field_name}', deepcopy(field_val))
            del field_val
        # debug(dir(plane))

    def update_display(self, img: Image) -> None:
        """
        Update display.

        :param img:
        """
        pixels = list(img.getdata())
        for i, _ in enumerate(pixels):
            pixels[i] *= 128

        # put bitmap array into display
        if lcd_sdk.LogiLcdIsConnected(lcd_sdk.TYPE_MONO):
            lcd_sdk.LogiLcdMonoSetBackground((c_ubyte * (self.width * self.height))(*pixels))
            lcd_sdk.LogiLcdUpdate()
        else:
            warning('LCD is not connected')

    def clear_display(self, true_clear=False) -> None:
        """
        Clear display.

        :param true_clear:
        """
        lcd_sdk.LogiLcdMonoSetBackground((c_ubyte * (self.width * self.height))(*[0] * (self.width * self.height)))
        if true_clear:
            for i in range(4):
                lcd_sdk.LogiLcdMonoSetText(i, '')
        lcd_sdk.LogiLcdUpdate()

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
