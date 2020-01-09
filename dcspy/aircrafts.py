from logging import basicConfig, DEBUG, debug, warning

from PIL import Image, ImageDraw

from dcspy import FONT_11, FONT_16
from dcspy.sdk import lcd_sdk

basicConfig(format='%(asctime)s | %(levelname)-7s | %(message)s / %(filename)s:%(lineno)d', level=DEBUG)


class Aircraft:
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        self.width = width
        self.height = height
        self.bios_data = {}

    def button_handle_specific_ac(self, button_pressed: int) -> str:
        """
        Button handler for spacific aircraft.

        :param button_pressed:
        :return:
        """
        debug(f'{self.__class__.__name__} Button: {button_pressed}')
        return '\n'

    def update_display(self) -> None:
        """Update display."""
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
        if update:
            self.update_display()

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
        self.bios_data = {
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

    def update_display(self) -> None:
        """Update display."""
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        # Scrachpad
        draw.text((0, 0),
                  f'{self.get_bios("ScratchpadStr1")}{self.get_bios("ScratchpadStr2")}{self.get_bios("ScratchpadNum")}',
                  1, FONT_16)
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
            draw.text((120, offset),
                      f'{i}{self.get_bios(f"OptionCueing{i}")}{self.get_bios(f"OptionDisplay{i}")}',
                      1, FONT_11)

        # Fuel Totaliser
        draw.text((36, 29), self.get_bios('FuelTotal'), 1, FONT_16)
        lcd_sdk.update_display(img)

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

    def button_handle_specific_ac(self, button_pressed: int) -> str:
        """
        Button handler for spacific aircraft.

        :param button_pressed:
        :return:
        """
        action = {1: 'UFC_COMM1_CHANNEL_SELECT DEC',
                  2: 'UFC_COMM1_CHANNEL_SELECT INC',
                  3: 'UFC_COMM2_CHANNEL_SELECT DEC',
                  4: 'UFC_COMM2_CHANNEL_SELECT INC'}
        debug(f'{self.__class__.__name__} Button: {button_pressed}')
        try:
            debug(f'Request: {action[button_pressed]}')
            return f'{action[button_pressed]}\n'
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
        self.bios_data = {
            'DEDLine1': {'addr': 0x44fc, 'len': 50, 'val': ''},
            'DEDLine2': {'addr': 0x452e, 'len': 50, 'val': ''},
            'DEDLine3': {'addr': 0x4560, 'len': 50, 'val': ''},
            'DEDLine4': {'addr': 0x4592, 'len': 50, 'val': ''},
            'DEDLine5': {'addr': 0x45c4, 'len': 50, 'val': ''}}

    def update_display(self) -> None:
        """Update display."""
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        for i in range(1, 6):
            offset = (i - 1) * 8
            draw.text((0, offset), self.get_bios(f'DEDLine{i}'), 1, FONT_11)
        lcd_sdk.update_display(img)


class Ka50(Aircraft):
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        super().__init__(width, height)
        self.bios_data = {
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

    def button_handle_specific_ac(self, button_pressed: int) -> str:
        """
        Button handler for spacific aircraft.

        :param button_pressed:
        :return:
        """
        debug(f'{self.__class__.__name__} Button: {button_pressed}')
        return '\n'

    def update_display(self) -> None:
        """Update display."""
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        text1, text2 = '', ''
        l1_text = self.get_bios('l1_text')
        l2_text = self.get_bios('l2_text')
        if l1_text:
            text1 = f' {l1_text[-5:-3]}{self.get_bios("l1_apostr1")}{l1_text[-3:-1]}{self.get_bios("l1_apostr2")}{l1_text[-1]}'
        if l2_text:
            text2 = f'{l2_text[-6:-3]}{self.get_bios("l2_apostr1")}{l2_text[-3:-1]}{self.get_bios("l2_apostr2")}{l2_text[-1]}'
        line1 = f'{self.get_bios("l1_sign")} {text1} {self.get_bios("l1_point")}'
        line2 = f'{self.get_bios("l2_sign")} {text2} {self.get_bios("l2_point")}'
        draw.text((0, 0), line1, 1, FONT_11)
        draw.text((0, 8), line2, 1, FONT_11)
        lcd_sdk.update_display(img)
