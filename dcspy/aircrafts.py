from logging import getLogger
from string import whitespace
from typing import Dict, Union

from PIL import Image, ImageDraw, ImageFont

# from dcspy import FONT_11, FONT_16
from sys import platform
from dcspy.sdk import lcd_sdk

try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict


if platform == 'win32':
    FONT_11 = ImageFont.truetype('consola.ttf', 11)
    FONT_16 = ImageFont.truetype('consola.ttf', 16)
else:
    FONT_11 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
    FONT_16 = ImageFont.truetype('DejaVuSansMono.ttf', 16)


BIOS_VALUE = TypedDict('BIOS_VALUE', {'class': str, 'args': Dict[str, int], 'value': Union[int, str]})
LOG = getLogger(__name__)


class Aircraft:
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        self.width = width
        self.height = height
        self.bios_data: Dict[str, BIOS_VALUE] = {}

    def button_request(self, button: int, request: str = '\n') -> str:
        """
        Prepare aircraft specific DCS-BIOS request for button pressed.

        If button is out of scope new line is return.

        :param button: possible values 1-4
        :type: int
        :param request: valid DCS-BIOS command as string
        :type request: str
        :return: ready to send DCS-BIOS request
        :rtype: str
        """
        LOG.debug(f'{self.__class__.__name__} Button: {button}')
        LOG.debug(f'Request: {request.replace(whitespace[2], " ")}')
        return request

    @staticmethod
    def update_display(image: Image.Image) -> None:
        """Update display."""
        lcd_sdk.update_display(image)

    def prepare_image(self) -> Image.Image:
        """
        Prepare image to bo send to LCD.

        :return: image instance ready display on LCD
        :rtype: Image.Image
        """
        raise NotImplementedError

    def set_bios(self, selector: str, value: str, update=True) -> None:
        """
        Set value for DCS-BIOS selector.

        :param selector:
        :param value:
        :param update:
        """
        self.bios_data[selector]['value'] = value
        LOG.debug(f'{self.__class__.__name__} {selector} value: "{value}"')
        lcd_image = self.prepare_image()
        if update:
            self.update_display(lcd_image)

    def get_bios(self, selector: str) -> Union[str, int]:
        """
        Get value for DCS-BIOS selector.

        :param selector:
        """
        try:
            return self.bios_data[selector]['value']
        except KeyError:
            return ''


class FA18Chornet(Aircraft):
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        super().__init__(width, height)
        self.bios_data: Dict[str, BIOS_VALUE] = {
            'ScratchpadStr1': {'class': 'StringBuffer', 'args': {'address': 0x744e, 'length': 2}, 'value': str()},
            'ScratchpadStr2': {'class': 'StringBuffer', 'args': {'address': 0x7450, 'length': 2}, 'value': str()},
            'ScratchpadNum': {'class': 'StringBuffer', 'args': {'address': 0x7446, 'length': 8}, 'value': str()},
            'OptionDisplay1': {'class': 'StringBuffer', 'args': {'address': 0x7432, 'length': 4}, 'value': str()},
            'OptionDisplay2': {'class': 'StringBuffer', 'args': {'address': 0x7436, 'length': 4}, 'value': str()},
            'OptionDisplay3': {'class': 'StringBuffer', 'args': {'address': 0x743a, 'length': 4}, 'value': str()},
            'OptionDisplay4': {'class': 'StringBuffer', 'args': {'address': 0x743e, 'length': 4}, 'value': str()},
            'OptionDisplay5': {'class': 'StringBuffer', 'args': {'address': 0x7442, 'length': 4}, 'value': str()},
            'COMM1': {'class': 'StringBuffer', 'args': {'address': 0x7424, 'length': 2}, 'value': str()},
            'COMM2': {'class': 'StringBuffer', 'args': {'address': 0x7426, 'length': 2}, 'value': str()},
            'OptionCueing1': {'class': 'StringBuffer', 'args': {'address': 0x7428, 'length': 1}, 'value': str()},
            'OptionCueing2': {'class': 'StringBuffer', 'args': {'address': 0x742a, 'length': 1}, 'value': str()},
            'OptionCueing3': {'class': 'StringBuffer', 'args': {'address': 0x742c, 'length': 1}, 'value': str()},
            'OptionCueing4': {'class': 'StringBuffer', 'args': {'address': 0x742e, 'length': 1}, 'value': str()},
            'OptionCueing5': {'class': 'StringBuffer', 'args': {'address': 0x7430, 'length': 1}, 'value': str()},
            'FuelTotal': {'class': 'StringBuffer', 'args': {'address': 0x748a, 'length': 6}, 'value': str()}}

    def prepare_image(self) -> Image.Image:
        """
        Prepare image to bo send to LCD.

        :return: image instance ready display on LCD
        :rtype: Image.Image
        """
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        # Scrachpad
        draw.text((0, 0), f'{self.get_bios("ScratchpadStr1")}{self.get_bios("ScratchpadStr2")}{self.get_bios("ScratchpadNum")}', 1, FONT_16)
        draw.line((0, 20, 115, 20), 1, 1)

        # comm1
        draw.rectangle((0, 29, 20, 42), 0, 1)
        draw.text((2, 29), self.get_bios('COMM1'), 1, FONT_16)

        # comm2
        offset_comm2 = 44
        draw.rectangle((139 - offset_comm2, 29, 159 - offset_comm2, 42), 0, 1)
        draw.text((140 - offset_comm2, 29), self.get_bios('COMM2'), 1, FONT_16)

        # option display 1..5 with cueing
        for i in range(1, 6):
            offset = (i - 1) * 8
            draw.text((120, offset), f'{i}{self.get_bios(f"OptionCueing{i}")}{self.get_bios(f"OptionDisplay{i}")}', 1, FONT_11)

        # Fuel Totaliser
        draw.text((36, 29), self.get_bios('FuelTotal'), 1, FONT_16)
        return img

    def set_bios(self, selector: str, value: str, update=True) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        :param update:
        """
        if selector in ('ScratchpadStr1', 'ScratchpadStr2', 'COMM1', 'COMM2'):
            value = value.replace('`', '1').replace('~', '2')
        super().set_bios(selector, value, update)

    def button_request(self, button: int, request: str = '\n') -> str:
        """
        Prepare F/A-18 Hornet specific DCS-BIOS request for button pressed.

        If button is out of scope new line is return.

        :param button: possible values 1-4
        :type: int
        :param request: valid DCS-BIOS command as string
        :type request: str
        :return: ready to send DCS-BIOS request
        :rtype: str
        """
        action = {1: 'UFC_COMM1_CHANNEL_SELECT DEC\n',
                  2: 'UFC_COMM1_CHANNEL_SELECT INC\n',
                  3: 'UFC_COMM2_CHANNEL_SELECT DEC\n',
                  4: 'UFC_COMM2_CHANNEL_SELECT INC\n'}
        return super().button_request(button, action.get(button, '\n'))


class F16C50(Aircraft):
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        super().__init__(width, height)
        self.bios_data: Dict[str, BIOS_VALUE] = {
            'DED_LINE_1': {'class': 'StringBuffer', 'args': {'address': 0x4502, 'length': 25}, 'value': str()},
            'DED_LINE_2': {'class': 'StringBuffer', 'args': {'address': 0x451c, 'length': 25}, 'value': str()},
            'DED_LINE_3': {'class': 'StringBuffer', 'args': {'address': 0x4536, 'length': 25}, 'value': str()},
            'DED_LINE_4': {'class': 'StringBuffer', 'args': {'address': 0x4550, 'length': 25}, 'value': str()},
            'DED_LINE_5': {'class': 'StringBuffer', 'args': {'address': 0x456a, 'length': 25}, 'value': str()}}

    def prepare_image(self) -> Image.Image:
        """
        Prepare image to bo send to LCD.

        :return: image instance ready display on LCD
        :rtype: Image.Image
        """
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        for i in range(1, 6):
            offset = (i - 1) * 8
            # replace 'o' to degree sign and 'a' with up-down arrow
            text = str(self.get_bios(f'DED_LINE_{i}')).replace('o', '\u00b0').replace('a', '\u2195')
            draw.text((0, offset), text, 1, FONT_11)
        return img


class Ka50(Aircraft):
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        super().__init__(width, height)
        self.bios_data: Dict[str, BIOS_VALUE] = {
            'l1_apostr1': {'class': 'StringBuffer', 'args': {'address': 0x1934, 'length': 1}, 'value': str()},
            'l1_apostr2': {'class': 'StringBuffer', 'args': {'address': 0x1936, 'length': 1}, 'value': str()},
            'l1_point': {'class': 'StringBuffer', 'args': {'address': 0x1930, 'length': 1}, 'value': str()},
            'l1_sign': {'class': 'StringBuffer', 'args': {'address': 0x1920, 'length': 1}, 'value': str()},
            'l1_text': {'class': 'StringBuffer', 'args': {'address': 0x1924, 'length': 6}, 'value': str()},
            'l2_apostr1': {'class': 'StringBuffer', 'args': {'address': 0x1938, 'length': 1}, 'value': str()},
            'l2_apostr2': {'class': 'StringBuffer', 'args': {'address': 0x193a, 'length': 1}, 'value': str()},
            'l2_point': {'class': 'StringBuffer', 'args': {'address': 0x1932, 'length': 1}, 'value': str()},
            'l2_sign': {'class': 'StringBuffer', 'args': {'address': 0x1922, 'length': 1}, 'value': str()},
            'l2_text': {'class': 'StringBuffer', 'args': {'address': 0x192a, 'length': 6}, 'value': str()},
            'AP_ALT_HOLD_LED': {'class': 'IntegerBuffer', 'args': {'address': 0x1936, 'mask': 0x8000, 'shift_by': 0xf}, 'value': int()},
            'AP_BANK_HOLD_LED': {'class': 'IntegerBuffer', 'args': {'address': 0x1936, 'mask': 0x200, 'shift_by': 0x9}, 'value': int()},
            'AP_FD_LED': {'class': 'IntegerBuffer', 'args': {'address': 0x1938, 'mask': 0x200, 'shift_by': 0x9}, 'value': int()},
            'AP_HDG_HOLD_LED': {'class': 'IntegerBuffer', 'args': {'address': 0x1936, 'mask': 0x800, 'shift_by': 0xb}, 'value': int()},
            'AP_PITCH_HOLD_LED': {'class': 'IntegerBuffer', 'args': {'address': 0x1936, 'mask': 0x2000, 'shift_by': 0xd}, 'value': int()}}

    def button_request(self, button: int, request: str = '\n') -> str:
        """
        Prepare Ka-50 Black Shark specific DCS-BIOS request for button pressed.

        If button is out of scope new line is return.

        :param button: possible values 1-4
        :type: int
        :param request: valid DCS-BIOS command as string
        :type request: str
        :return: ready to send DCS-BIOS request
        :rtype: str
        """
        action = {1: 'PVI_WAYPOINTS_BTN 1\nPVI_WAYPOINTS_BTN 0\n',
                  2: 'PVI_FIXPOINTS_BTN 1\nPVI_FIXPOINTS_BTN 0\n',
                  3: 'PVI_AIRFIELDS_BTN 1\nPVI_AIRFIELDS_BTN 0\n',
                  4: 'PVI_TARGETS_BTN 1\nPVI_TARGETS_BTN 0\n'}
        return super().button_request(button, action.get(button, '\n'))

    def prepare_image(self) -> Image.Image:
        """
        Prepare image to bo send to LCD.

        :return: image instance ready display on LCD
        :rtype: Image.Image
        """
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        text1, text2 = '', ''
        draw.rectangle((0, 1, 85, 18), 0, 1)
        draw.rectangle((0, 22, 85, 39), 0, 1)
        draw.rectangle((88, 1, 103, 18), 0, 1)
        draw.rectangle((88, 22, 103, 39), 0, 1)
        l1_text = str(self.get_bios('l1_text'))
        l2_text = str(self.get_bios('l2_text'))
        if l1_text:
            text1 = f'{l1_text[-6:-3]}{self.get_bios("l1_apostr1")}{l1_text[-3:-1]}{self.get_bios("l1_apostr2")}{l1_text[-1]}'
        if l2_text:
            text2 = f'{l2_text[-6:-3]}{self.get_bios("l2_apostr1")}{l2_text[-3:-1]}{self.get_bios("l2_apostr2")}{l2_text[-1]}'
        line1 = f'{self.get_bios("l1_sign")}{text1} {self.get_bios("l1_point")}'
        line2 = f'{self.get_bios("l2_sign")}{text2} {self.get_bios("l2_point")}'
        draw.text((2, 3), line1, 1, FONT_16)
        draw.text((2, 24), line2, 1, FONT_16)
        self._auto_pilot_switch(draw)
        return img

    def _auto_pilot_switch(self, draw_obj: ImageDraw) -> None:
        """
        Draw rectangle and add text for autopilot channels in correct coordinates.

        :param draw_obj: ImageDraw object form PIL
        """
        for c_rect, c_text, ap_channel, turn_on in (((111, 1, 124, 18), (114, 3), 'B', self.get_bios('AP_BANK_HOLD_LED')),
                                                    ((128, 1, 141, 18), (130, 3), 'P', self.get_bios('AP_PITCH_HOLD_LED')),
                                                    ((145, 1, 158, 18), (147, 3), 'F', self.get_bios('AP_FD_LED')),
                                                    ((111, 22, 124, 39), (114, 24), 'H', self.get_bios('AP_HDG_HOLD_LED')),
                                                    ((128, 22, 141, 39), (130, 24), 'A', self.get_bios('AP_ALT_HOLD_LED'))):
            if turn_on:
                draw_obj.rectangle(c_rect, 1, 1)
                draw_obj.text(c_text, ap_channel, 0, FONT_16)
            else:
                draw_obj.rectangle(c_rect, 0, 1)
                draw_obj.text(c_text, ap_channel, 1, FONT_16)


class F14B(Aircraft):
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        super().__init__(width, height)
        self.bios_data: Dict[str, BIOS_VALUE] = {
            'RIO_CAP_CLEAR': {'class': 'IntegerBuffer', 'args': {'address': 0x12d4, 'mask': 0x1, 'shift_by': 0x0}, 'value': int()},
            'RIO_CAP_SW': {'class': 'IntegerBuffer', 'args': {'address': 0x12d2, 'mask': 0x8000, 'shift_by': 0xf}, 'value': int()},
            'RIO_CAP_NE': {'class': 'IntegerBuffer', 'args': {'address': 0x12d2, 'mask': 0x4000, 'shift_by': 0xe}, 'value': int()},
            'RIO_CAP_ENTER': {'class': 'IntegerBuffer', 'args': {'address': 0x12d4, 'mask': 0x2, 'shift_by': 0x1}, 'value': int()}}

    def button_request(self, button: int, request: str = '\n') -> str:
        """
        Prepare F-14 Tomcat specific DCS-BIOS request for button pressed.

        If button is out of scope new line is return.

        :param button: possible values 1-4
        :type: int
        :param request: valid DCS-BIOS command as string
        :type request: str
        :return: ready to send DCS-BIOS request
        :rtype: str
        """
        action = {1: 'RIO_CAP_CLEAR 1\nRIO_CAP_CLEAR 0\n',
                  2: 'RIO_CAP_SW 1\nRIO_CAP_SW 0\n',
                  3: 'RIO_CAP_NE 1\nRIO_CAP_NE 0\n',
                  4: 'RIO_CAP_ENTER 1\nRIO_CAP_ENTER 0\n'}
        return super().button_request(button, action.get(button, '\n'))

    def prepare_image(self) -> Image.Image:
        """
        Prepare image to bo send to LCD.

        :return: image instance ready display on LCD
        :rtype: Image.Image
        """
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        draw.text((2, 3), 'F-14B Tomcat', 1, FONT_16)
        return img
