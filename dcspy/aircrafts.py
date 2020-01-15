from logging import debug, warning
from typing import Dict

from PIL import Image, ImageDraw

from dcspy import FONT_11, FONT_16
from dcspy.sdk import lcd_sdk

try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict


BIOS_VALUE = TypedDict('BIOS_VALUE', {'addr': int, 'len': int, 'val': str})


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

    def button_request(self, button: int) -> str:
        """
        Prepare specific DCS-BIOS request for button pressed.

        If button is out of scope new line is return.

        :param button: possible values 1-4
        :type: int
        :return: ready to send DCS-BIOS request
        :rtype: str
        """
        debug(f'{self.__class__.__name__} Button: {button}')
        return '\n'

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
        self.bios_data[selector]['val'] = value
        debug(f'{self.__class__.__name__} {selector} value: "{value}"')
        lcd_image = self.prepare_image()
        if update:
            self.update_display(lcd_image)

    def get_bios(self, selector: str) -> str:
        """
        Get value for DCS-BIOS selector.

        :param selector:
        """
        try:
            return self.bios_data[selector]['val']
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
            'ScratchpadStr1': {'addr': 0x744e, 'len': 2, 'val': ''},
            'ScratchpadStr2': {'addr': 0x7450, 'len': 2, 'val': ''},
            'ScratchpadNum': {'addr': 0x7446, 'len': 8, 'val': ''},
            'OptionDisplay1': {'addr': 0x7432, 'len': 4, 'val': ''},
            'OptionDisplay2': {'addr': 0x7436, 'len': 4, 'val': ''},
            'OptionDisplay3': {'addr': 0x743a, 'len': 4, 'val': ''},
            'OptionDisplay4': {'addr': 0x743e, 'len': 4, 'val': ''},
            'OptionDisplay5': {'addr': 0x7442, 'len': 4, 'val': ''},
            'COMM1': {'addr': 0x7424, 'len': 2, 'val': ''},
            'COMM2': {'addr': 0x7426, 'len': 2, 'val': ''},
            'OptionCueing1': {'addr': 0x7428, 'len': 1, 'val': ''},
            'OptionCueing2': {'addr': 0x742a, 'len': 1, 'val': ''},
            'OptionCueing3': {'addr': 0x742c, 'len': 1, 'val': ''},
            'OptionCueing4': {'addr': 0x742e, 'len': 1, 'val': ''},
            'OptionCueing5': {'addr': 0x7430, 'len': 1, 'val': ''},
            'FuelTotal': {'addr': 0x748a, 'len': 6, 'val': ''}}

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

    def button_request(self, button: int) -> str:
        """
        Prepare specific DCS-BIOS request for button pressed.

        If button is out of scope new line is return.

        :param button: possible values 1-4
        :type: int
        :return: ready to send DCS-BIOS request
        :rtype: str
        """
        action = {1: 'UFC_COMM1_CHANNEL_SELECT DEC',
                  2: 'UFC_COMM1_CHANNEL_SELECT INC',
                  3: 'UFC_COMM2_CHANNEL_SELECT DEC',
                  4: 'UFC_COMM2_CHANNEL_SELECT INC'}
        debug(f'{self.__class__.__name__} Button: {button}')
        try:
            debug(f'Request: {action[button]}')
            return f'{action[button]}\n'
        except KeyError:
            warning(f'{self.__class__.__name__} Wrong key, return empty request with new line')
            return f'\n'


class F16C50(Aircraft):
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        super().__init__(width, height)
        self.bios_data: Dict[str, BIOS_VALUE] = {
            'DEDLine1': {'addr': 0x44fc, 'len': 50, 'val': ''},
            'DEDLine2': {'addr': 0x452e, 'len': 50, 'val': ''},
            'DEDLine3': {'addr': 0x4560, 'len': 50, 'val': ''},
            'DEDLine4': {'addr': 0x4592, 'len': 50, 'val': ''},
            'DEDLine5': {'addr': 0x45c4, 'len': 50, 'val': ''}}

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
            draw.text((0, offset), self.get_bios(f'DEDLine{i}'), 1, FONT_11)
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
            'l1_apostr1': {'addr': 0x1934, 'len': 1, 'val': ''},
            'l1_apostr2': {'addr': 0x1936, 'len': 1, 'val': ''},
            'l1_point': {'addr': 0x1930, 'len': 1, 'val': ''},
            'l1_sign': {'addr': 0x1920, 'len': 1, 'val': ''},
            'l1_text': {'addr': 0x1924, 'len': 6, 'val': ''},
            'l2_apostr1': {'addr': 0x1938, 'len': 1, 'val': ''},
            'l2_apostr2': {'addr': 0x193a, 'len': 1, 'val': ''},
            'l2_point': {'addr': 0x1932, 'len': 1, 'val': ''},
            'l2_sign': {'addr': 0x1922, 'len': 1, 'val': ''},
            'l2_text': {'addr': 0x192a, 'len': 6, 'val': ''}}
        # todo: add handling IntegerBuffer to fetch data from BIOS
        # 'AP_ALT_HOLD_LED': {'addr': 0x1936, 'len': 1, 'val': ''},
        # 'AP_BANK_HOLD_LED': {'addr': 0x1936, 'len': 1, 'val': ''},
        # 'AP_FD_LED': {'addr': 0x1936, 'len': 1, 'val': ''},
        # 'AP_HDG_HOLD_LED': {'addr': 0x1936, 'len': 1, 'val': ''},
        # 'AP_PITCH_HOLD_LED': {'addr': 0x1936, 'len': 1, 'val': ''}}

    def button_request(self, button: int) -> str:
        """
        Prepare specific DCS-BIOS request for button pressed.

        If button is out of scope new line is return.

        :param button: possible values 1-4
        :type: int
        :return: ready to send DCS-BIOS request
        :rtype: str
        """
        action = {1: 'PVI_WAYPOINTS_BTN 1\nPVI_WAYPOINTS_BTN 0\n',
                  2: 'PVI_FIXPOINTS_BTN 1\nPVI_FIXPOINTS_BTN 0\n',
                  3: 'PVI_AIRFIELDS_BTN 1\nPVI_AIRFIELDS_BTN 0\n',
                  4: 'PVI_TARGETS_BTN 1\nPVI_TARGETS_BTN 0\n'}
        debug(f'{self.__class__.__name__} Button: {button}')
        try:
            request = action[button].replace('\n', ' ')
            debug(f'Request: {request}')
            return f'{action[button]}'
        except KeyError:
            warning(f'{self.__class__.__name__} Wrong key, return empty request with new line')
            return f'\n'

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
        l1_text = self.get_bios('l1_text')
        l2_text = self.get_bios('l2_text')
        if l1_text:
            text1 = f'{l1_text[-6:-3]}{self.get_bios("l1_apostr1")}{l1_text[-3:-1]}{self.get_bios("l1_apostr2")}{l1_text[-1]}'
        if l2_text:
            text2 = f'{l2_text[-6:-3]}{self.get_bios("l2_apostr1")}{l2_text[-3:-1]}{self.get_bios("l2_apostr2")}{l2_text[-1]}'
        line1 = f'{self.get_bios("l1_sign")}{text1} {self.get_bios("l1_point")}'
        line2 = f'{self.get_bios("l2_sign")}{text2} {self.get_bios("l2_point")}'
        draw.text((2, 3), line1, 1, FONT_16)
        draw.text((2, 24), line2, 1, FONT_16)
        return img
