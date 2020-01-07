from abc import abstractmethod
from logging import basicConfig, DEBUG, debug

from PIL import Image, ImageDraw, ImageFont

import dcspy.sdk.lcd_sdk

basicConfig(format='%(asctime)s | %(levelname)-7s | %(message)s / %(filename)s:%(lineno)d', level=DEBUG)
consolas_11 = ImageFont.truetype('consola.ttf', 11)
consolas_16 = ImageFont.truetype('consola.ttf', 16)


class AircraftHandler:
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

    @abstractmethod
    def update_display(self) -> None:
        """Update display."""
        pass

    def set_data(self, selector: str, value: str, update=True) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        :param update:
        """
        setattr(self, selector, value)
        debug(f'{self.__class__.__name__} {selector} value: "{value}"')
        if update:
            self.update_display()


class FA18Chornet(AircraftHandler):
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        super().__init__(width, height)
        self.ScratchpadStr1 = ''
        self.ScratchpadStr2 = ''
        self.ScratchpadNum = ''
        self.OptionDisplay1 = ''
        self.OptionDisplay2 = ''
        self.OptionDisplay3 = ''
        self.OptionDisplay4 = ''
        self.OptionDisplay5 = ''
        self.COMM1 = ''
        self.COMM2 = ''
        self.OptionCueing1 = ''
        self.OptionCueing2 = ''
        self.OptionCueing3 = ''
        self.OptionCueing4 = ''
        self.OptionCueing5 = ''
        self.FuelTotal = ''

        self.bios_data = {
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

    def update_display(self) -> None:
        """Update display."""
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        # Scrachpad
        draw.text((0, 0),
                  self.ScratchpadStr1 + self.ScratchpadStr2 + self.ScratchpadNum,
                  1, consolas_16)
        draw.line((0, 20, 115, 20), 1, 1)

        # comm1
        draw.rectangle((0, 29, 20, 42), 0, 1)
        draw.text((2, 29), self.COMM1, 1, consolas_16)

        # comm2
        offset_comm2 = 44
        draw.rectangle((139 - offset_comm2, 29, 159 - offset_comm2, 42), 0, 1)
        draw.text((140 - offset_comm2, 29), self.COMM2, 1, consolas_16)

        # option display 1..5 with cueing
        for i in range(1, 6):
            offset = (i - 1) * 8
            draw.text((120, offset),
                      f'{i}{getattr(self, f"OptionCueing{i}")}{getattr(self, f"OptionDisplay{i}")}',
                      1, consolas_11)

        # Fuel Totaliser
        draw.text((36, 29), self.FuelTotal, 1, consolas_16)
        dcspy.sdk.lcd_sdk.update_display(img)

    def set_data(self, selector: str, value: str, update=True) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        :param update:
        """
        if selector in ('ScratchpadStr1', 'ScratchpadStr2', 'COMM1', 'COMM2'):
            value = value.replace('`', '1').replace('~', '2')
        super().set_data(selector, value, update)

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
        debug(f'Request: {action[button_pressed]}')
        return f'{action[button_pressed]}\n'


class F16C50(AircraftHandler):
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        super().__init__(width, height)
        self.DEDLine1 = ''
        self.DEDLine2 = ''
        self.DEDLine3 = ''
        self.DEDLine4 = ''
        self.DEDLine5 = ''
        self.bios_data = {
            'DEDLine1': {'addr': 0x44fc, 'length': 50},
            'DEDLine2': {'addr': 0x452e, 'length': 50},
            'DEDLine3': {'addr': 0x4560, 'length': 50},
            'DEDLine4': {'addr': 0x4592, 'length': 50},
            'DEDLine5': {'addr': 0x45c4, 'length': 50}}

    def update_display(self) -> None:
        """Update display."""
        img = Image.new('1', (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        for i in range(1, 6):
            offset = (i - 1) * 8
            draw.text((0, offset), getattr(self, f'DEDLine{i}'), 1, consolas_11)
        dcspy.sdk.lcd_sdk.update_display(img)


class Ka50(AircraftHandler):
    def __init__(self, width: int, height: int) -> None:
        """
        Basic constructor.

        :param width: LCD width
        :param height: LCD height
        """
        super().__init__(width, height)
        self.l1_apostr1 = ''
        self.l1_apostr2 = ''
        self.l1_point = ''
        self.l1_sign = ''
        self.l1_text = ''
        self.l2_apostr1 = ''
        self.l2_apostr2 = ''
        self.l2_point = ''
        self.l2_sign = ''
        self.l2_text = ''
        self.bios_data = {
            'l1_apostr1': {'addr': 0x1934, 'length': 1},
            'l1_apostr2': {'addr': 0x1936, 'length': 1},
            'l1_point': {'addr': 0x1930, 'length': 1},
            'l1_sign': {'addr': 0x1920, 'length': 1},
            'l1_text': {'addr': 0x1924, 'length': 6},
            'l2_apostr1': {'addr': 0x1938, 'length': 1},
            'l2_apostr2': {'addr': 0x193a, 'length': 1},
            'l2_point': {'addr': 0x1932, 'length': 1},
            'l2_sign': {'addr': 0x1922, 'length': 1},
            'l2_text': {'addr': 0x192a, 'length': 6}}

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
        if self.l1_text:
            text1 = f' {self.l1_text[-5:-3]}{self.l1_apostr1}{self.l1_text[-3:-1]}{self.l1_apostr2}{self.l1_text[-1]}'
        if self.l2_text:
            text2 = f'{self.l2_text[-6:-3]}{self.l2_apostr1}{self.l2_text[-3:-1]}{self.l2_apostr2}{self.l2_text[-1]}'
        line1 = f'{self.l1_sign} {text1} {self.l1_point}'
        line2 = f'{self.l2_sign} {text2} {self.l2_point}'
        draw.text((0, 0), line1, 1, consolas_11)
        draw.text((0, 8), line2, 1, consolas_11)
        dcspy.sdk.lcd_sdk.update_display(img)
