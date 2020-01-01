from logging import basicConfig, DEBUG, debug

from dcspy.dcsbios import StringBuffer

basicConfig(format='%(asctime)s | %(levelname)-7s | %(message)s / %(filename)s:%(lineno)d', level=DEBUG)


class AircraftHandler:
    def __init__(self, display_handler) -> None:
        """
        Basic constructor.

        :param display_handler:
        :type display_handler: G13Handler
        """
        self.g13 = display_handler

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
        self.g13.draw.rectangle((0, 0, self.g13.width, self.g13.height), 0, 0)  # clear bitmap

    def set_data(self, selector: str, value: str, update=True) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        :param update:
        """
        setattr(self, selector, value)
        debug(f'value: {value}')
        if update:
            self.update_display()


class FA18Chornet(AircraftHandler):
    def __init__(self, display_handler) -> None:
        """
        Basic constructor.

        :param display_handler:
        :type display_handler: G13Handler
        """
        super().__init__(display_handler)
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

        self.bufferScratchpadStr1 = StringBuffer(self.g13.parser, 0x744e, 2, lambda s: self.set_data('ScratchpadStr1', s))
        self.bufferScratchpadStr2 = StringBuffer(self.g13.parser, 0x7450, 2, lambda s: self.set_data('ScratchpadStr2', s))
        self.bufferScratchpadNum = StringBuffer(self.g13.parser, 0x7446, 8, lambda s: self.set_data('ScratchpadNum', s))
        self.bufferOptionDisplay1 = StringBuffer(self.g13.parser, 0x7432, 4, lambda s: self.set_data('OptionDisplay1', s))
        self.bufferOptionDisplay2 = StringBuffer(self.g13.parser, 0x7436, 4, lambda s: self.set_data('OptionDisplay2', s))
        self.bufferOptionDisplay3 = StringBuffer(self.g13.parser, 0x743a, 4, lambda s: self.set_data('OptionDisplay3', s))
        self.bufferOptionDisplay4 = StringBuffer(self.g13.parser, 0x743e, 4, lambda s: self.set_data('OptionDisplay4', s))
        self.bufferOptionDisplay5 = StringBuffer(self.g13.parser, 0x7442, 4, lambda s: self.set_data('OptionDisplay5', s))
        self.bufferCOMM1 = StringBuffer(self.g13.parser, 0x7424, 2, lambda s: self.set_data('COMM1', s))
        self.bufferCOMM2 = StringBuffer(self.g13.parser, 0x7426, 2, lambda s: self.set_data('COMM2', s))
        self.bufferOptionCueing1 = StringBuffer(self.g13.parser, 0x7428, 1, lambda s: self.set_data('OptionCueing1', s))
        self.bufferOptionCueing2 = StringBuffer(self.g13.parser, 0x742a, 1, lambda s: self.set_data('OptionCueing2', s))
        self.bufferOptionCueing3 = StringBuffer(self.g13.parser, 0x742c, 1, lambda s: self.set_data('OptionCueing3', s))
        self.bufferOptionCueing4 = StringBuffer(self.g13.parser, 0x742e, 1, lambda s: self.set_data('OptionCueing4', s))
        self.bufferOptionCueing5 = StringBuffer(self.g13.parser, 0x7430, 1, lambda s: self.set_data('OptionCueing5', s))
        self.bufferFuelTotal = StringBuffer(self.g13.parser, 0x748a, 6, lambda s: self.set_data('FuelTotal', s))

    def update_display(self) -> None:
        """Update display."""
        super().update_display()

        # Scrachpad
        self.g13.draw.text((0, 0),
                           self.ScratchpadStr1 + self.ScratchpadStr2 + self.ScratchpadNum,
                           1, self.g13.font2)
        self.g13.draw.line((0, 20, 115, 20), 1, 1)

        # comm1
        self.g13.draw.rectangle((0, 29, 20, 42), 0, 1)
        self.g13.draw.text((2, 29), self.COMM1, 1, self.g13.font2)

        # comm2
        offset_comm2 = 44
        self.g13.draw.rectangle((139 - offset_comm2, 29, 159 - offset_comm2, 42), 0, 1)
        self.g13.draw.text((140 - offset_comm2, 29), self.COMM2, 1, self.g13.font2)

        # option display 1..5 with cueing
        for i in range(1, 6):
            offset = (i - 1) * 8
            self.g13.draw.text((120, offset),
                               f'{i}{getattr(self, f"OptionCueing{i}")}{getattr(self, f"OptionDisplay{i}")}',
                               1, self.g13.font1)

        # Fuel Totaliser
        self.g13.draw.text((36, 29), self.FuelTotal, 1, self.g13.font2)

        self.g13.update_display(self.g13.img)

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
    def __init__(self, display_handler) -> None:
        """
        Basic constructor.

        :param display_handler:
        :type display_handler: G13Handler
        """
        super().__init__(display_handler)
        self.DEDLine1 = ''
        self.DEDLine2 = ''
        self.DEDLine3 = ''
        self.DEDLine4 = ''
        self.DEDLine5 = ''

        self.bufferDEDLine1 = StringBuffer(self.g13.parser, 0x44fc, 50, lambda s: self.set_data('DEDLine1', s))
        self.bufferDEDLine2 = StringBuffer(self.g13.parser, 0x452e, 50, lambda s: self.set_data('DEDLine2', s))
        self.bufferDEDLine3 = StringBuffer(self.g13.parser, 0x4560, 50, lambda s: self.set_data('DEDLine3', s))
        self.bufferDEDLine4 = StringBuffer(self.g13.parser, 0x4592, 50, lambda s: self.set_data('DEDLine4', s))
        self.bufferDEDLine5 = StringBuffer(self.g13.parser, 0x45c4, 50, lambda s: self.set_data('DEDLine5', s))

    def update_display(self) -> None:
        """Update display."""
        super().update_display()

        for i in range(1, 6):
            offset = (i - 1) * 8
            self.g13.draw.text((0, offset), getattr(self, f'DEDLine{i}'), 1, self.g13.font1)
        self.g13.update_display(self.g13.img)


class Ka50(AircraftHandler):
    def __init__(self, display_handler):
        """
        Basic constructor.

        :param display_handler:
        :type display_handler: G13Handler
        """
        super().__init__(display_handler)
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

        self.buffer_l1_apostr1 = StringBuffer(self.g13.parser, 0x1934, 1, lambda s: self.set_data('l1_apostr1', s))
        self.buffer_l1_apostr2 = StringBuffer(self.g13.parser, 0x1936, 1, lambda s: self.set_data('l1_apostr2', s))
        self.buffer_l1_point = StringBuffer(self.g13.parser, 0x1930, 1, lambda s: self.set_data('l1_point', s))
        self.buffer_l1_sign = StringBuffer(self.g13.parser, 0x1920, 1, lambda s: self.set_data('l1_sign', s))
        self.buffer_l1_text = StringBuffer(self.g13.parser, 0x1924, 6, lambda s: self.set_data('l1_text', s))
        self.buffer_l2_apostr1 = StringBuffer(self.g13.parser, 0x1938, 1, lambda s: self.set_data('l2_apostr1', s))
        self.buffer_l2_apostr2 = StringBuffer(self.g13.parser, 0x193a, 1, lambda s: self.set_data('l2_apostr2', s))
        self.buffer_l2_point = StringBuffer(self.g13.parser, 0x1932, 1, lambda s: self.set_data('l2_point', s))
        self.buffer_l2_sign = StringBuffer(self.g13.parser, 0x1922, 1, lambda s: self.set_data('l2_sign', s))
        self.buffer_l2_text = StringBuffer(self.g13.parser, 0x192a, 6, lambda s: self.set_data('l2_text', s))

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
        super().update_display()
        text1, text2 = '', ''
        if self.l1_text:
            text1 = f' {self.l1_text[-5:-3]}{self.l1_apostr1}{self.l1_text[-3:-1]}{self.l1_apostr2}{self.l1_text[-1]}'
        if self.l2_text:
            text2 = f'{self.l2_text[-6:-3]}{self.l2_apostr1}{self.l2_text[-3:-1]}{self.l2_apostr2}{self.l2_text[-1]}'
        line1 = f'{self.l1_sign} {text1} {self.l1_point}'
        line2 = f'{self.l2_sign} {text2} {self.l2_point}'
        self.g13.draw.text((0, 0), line1, 1, self.g13.font1)
        self.g13.draw.text((0, 8), line2, 1, self.g13.font1)
        self.g13.update_display(self.g13.img)
