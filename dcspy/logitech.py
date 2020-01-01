from ctypes import c_ubyte, sizeof, c_void_p
from importlib import import_module
from logging import basicConfig, DEBUG, info, debug, warning
from math import log2
from platform import architecture
from socket import socket
from sys import maxsize

from PIL import Image, ImageFont, ImageDraw

from dcspy.sdk import lcd_sdk
from dcspy.dcsbios import StringBuffer, ProtocolParser

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

    def set_ac(self, value: str) -> None:
        """
        Set aircraft.

        :param value:
        """
        if not value == self.currentAC:
            self.currentAC = value
            if value in ('FA-18C_hornet', 'Ka-50', 'F-16C_50'):
                info(f'Detected AC: {value}')
                self.info_display()
                self.shouldActivateNewAC = True
            else:
                # FIXME a może tylko tyo zostawić, żeby po prostu zaczynał aktywaować nowy moduł, a weryfikację zostawić w metodzie poniżej?
                warning(f'Unknown AC data: {value}')
                self.info_display(('Unknown AC data:', self.currentAC))

    def activate_new_ac(self) -> None:
        """Actiate new aircraft."""
        self.shouldActivateNewAC = False
        plane_name = self.currentAC.replace('-', '').replace('_', '')
        plane_class = getattr(import_module('dcspy.aircrafts'), plane_name)
        debug(f'Dynamic load of: {plane_name} as {self.currentAC}')
        self.currentACHook = plane_class(self)

    def info_display(self, message=('', '')) -> None:
        """
        Send message to display.

        :param message:
        """
        # clear bitmap
        self.draw.rectangle((0, 0, self.width, self.height), 0, 0)
        # self.ClearDisplay()

        if message == ('', ''):
            self.draw.text((0, 0), self.currentAC, 1, self.font1)
        else:
            y = 0
            # self.draw.text((0,0), message, 1, self.font1)
            for line in message:
                self.draw.text((0, y), line, 1, self.font1)
                y = y + 10

        self.update_display(self.img)

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

    def button_handle(self, s: socket) -> None:
        """
        Button handler.

        :param s:
        """
        button = self.check_buttons()
        if button:
            s.send(bytes(self.currentACHook.button_handle_specific_ac(button), 'utf-8'))
