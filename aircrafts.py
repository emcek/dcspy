from abc import abstractmethod
from logging import basicConfig, DEBUG, debug, warning

from dcsbios import StringBuffer

basicConfig(format='%(asctime)s | %(levelname)-6s | %(message)s / %(filename)s:%(lineno)d', level=DEBUG)


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
        request = ''
        if button_pressed == 1:
            request = 'UFC_COMM1_CHANNEL_SELECT DEC'
        elif button_pressed == 2:
            request = 'UFC_COMM1_CHANNEL_SELECT INC'
        elif button_pressed == 3:
            request = 'UFC_COMM2_CHANNEL_SELECT DEC'
        elif button_pressed == 4:
            request = 'UFC_COMM2_CHANNEL_SELECT INC'
        debug(f'{self.__class__.__name__} Button: {button_pressed}')
        debug(f'Request: {request}')
        return f'{request}\n'

    def update_display(self) -> None:
        """Update display."""
        self.g13.draw.rectangle((0, 0, self.g13.width, self.g13.height), 0, 0)  # clear bitmap

    @abstractmethod
    def set_data(self, selector, value, update=True) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        :param update:
        """
        pass


class FA18Handler(AircraftHandler):
    def __init__(self, display_handler) -> None:
        """
        Basic constructor.

        :param display_handler:
        :type display_handler: G13Handler
        """
        super().__init__(display_handler)
        self.ScratchpadString1Display = ''
        self.ScratchpadString2Display = ''
        self.ScratchpadNumberDisplay = ''
        self.OptionDisplay1 = ''
        self.OptionDisplay2 = ''
        self.OptionDisplay3 = ''
        self.OptionDisplay4 = ''
        self.OptionDisplay5 = ''
        self.COMM1Display = ''
        self.COMM2Display = ''
        self.OptionCueing1 = ''
        self.OptionCueing2 = ''
        self.OptionCueing3 = ''
        self.OptionCueing4 = ''
        self.OptionCueing5 = ''
        self.FuelTotal = ''

        self.bufferScratchpadString1Display = StringBuffer(self.g13.parser, 0x744e, 2, lambda s: self.set_data(1, s))
        self.bufferScratchpadString2Display = StringBuffer(self.g13.parser, 0x7450, 2, lambda s: self.set_data(2, s))
        self.bufferScratchpadNumberDisplay = StringBuffer(self.g13.parser, 0x7446, 8, lambda s: self.set_data(3, s))
        self.bufferOptionDisplay1 = StringBuffer(self.g13.parser, 0x7432, 4, lambda s: self.set_data(11, s))
        self.bufferOptionDisplay2 = StringBuffer(self.g13.parser, 0x7436, 4, lambda s: self.set_data(12, s))
        self.bufferOptionDisplay3 = StringBuffer(self.g13.parser, 0x743a, 4, lambda s: self.set_data(13, s))
        self.bufferOptionDisplay4 = StringBuffer(self.g13.parser, 0x743e, 4, lambda s: self.set_data(14, s))
        self.bufferOptionDisplay5 = StringBuffer(self.g13.parser, 0x7442, 4, lambda s: self.set_data(15, s))
        self.bufferCOMM1Display = StringBuffer(self.g13.parser, 0x7424, 2, lambda s: self.set_data(21, s))
        self.bufferCOMM2Display = StringBuffer(self.g13.parser, 0x7426, 2, lambda s: self.set_data(22, s))
        self.bufferOptionCueing1 = StringBuffer(self.g13.parser, 0x7428, 1, lambda s: self.set_data(31, s))
        self.bufferOptionCueing2 = StringBuffer(self.g13.parser, 0x742a, 1, lambda s: self.set_data(32, s))
        self.bufferOptionCueing3 = StringBuffer(self.g13.parser, 0x742c, 1, lambda s: self.set_data(33, s))
        self.bufferOptionCueing4 = StringBuffer(self.g13.parser, 0x742e, 1, lambda s: self.set_data(34, s))
        self.bufferOptionCueing5 = StringBuffer(self.g13.parser, 0x7430, 1, lambda s: self.set_data(35, s))
        self.bufferFuelTotal = StringBuffer(self.g13.parser, 0x748a, 6, lambda s: self.set_data(40, s))

    def update_display(self) -> None:
        """Update display."""
        super().update_display()

        # Scrachpad
        self.g13.draw.text((0, 0),
                           self.ScratchpadString1Display + self.ScratchpadString2Display + self.ScratchpadNumberDisplay,
                           1,
                           self.g13.font2)
        self.g13.draw.line((0, 20, 115, 20), 1, 1)

        # comm1
        self.g13.draw.rectangle((0, 29, 20, 42), 0, 1)
        self.g13.draw.text((2, 29), self.COMM1Display, 1, self.g13.font2)

        # comm2
        offset_comm2 = 44
        self.g13.draw.rectangle((139 - offset_comm2, 29, 159 - offset_comm2, 42), 0, 1)
        self.g13.draw.text((140 - offset_comm2, 29), self.COMM2Display, 1, self.g13.font2)

        # option display 1..5 with cueing
        for i in range(1, 6):
            offset = (i - 1) * 8
            self.g13.draw.text((120, offset),
                               f'{i}{getattr(self, f"OptionCueing{i}")}{getattr(self, f"OptionDisplay{i}")}',
                               1, self.g13.font1)

        # Fuel Totaliser
        self.g13.draw.text((36, 29), self.FuelTotal, 1, self.g13.font2)

        self.g13.update_display(self.g13.img)

    def set_data(self, selector: int, value: str, update=True) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        :param update:
        """
        # programming noob here, but it's pretty clear how to use this monster
        if selector == 1:
            self.ScratchpadString1Display = value.replace('`', '1').replace('~', '2')
        elif selector == 2:
            self.ScratchpadString2Display = value.replace('`', '1').replace('~', '2')
        elif selector == 3:
            self.ScratchpadNumberDisplay = value
        elif selector == 11:
            self.OptionDisplay1 = value
        elif selector == 12:
            self.OptionDisplay2 = value
        elif selector == 13:
            self.OptionDisplay3 = value
        elif selector == 14:
            self.OptionDisplay4 = value
        elif selector == 15:
            self.OptionDisplay5 = value
        elif selector == 21:
            # for unknown reason dcs_bios returns symbols instead '1' and '2'
            # from comm channel display, so here we can correct this
            self.COMM1Display = value.replace('`', '1').replace('~', '2')
        elif selector == 22:
            self.COMM2Display = value.replace('`', '1').replace('~', '2')
        elif selector == 31:
            self.OptionCueing1 = value
        elif selector == 32:
            self.OptionCueing2 = value
        elif selector == 33:
            self.OptionCueing3 = value
        elif selector == 34:
            self.OptionCueing4 = value
        elif selector == 35:
            self.OptionCueing5 = value
        elif selector == 40:
            self.FuelTotal = value
        else:
            warning(f'No such selector: {selector}')
        debug(f'value: {value}')
        if update:
            self.update_display()


class F16Handler(AircraftHandler):
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

    def set_data(self, selector: str, value: str, update=True) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        :param update:
        """
        # programming noob here, but it's pretty clear how to use this monster
        if selector == 'DEDLine1':
            self.DEDLine1 = value
        elif selector == 'DEDLine2':
            self.DEDLine2 = value
        elif selector == 'DEDLine3':
            self.DEDLine3 = value
        elif selector == 'DEDLine4':
            self.DEDLine4 = value
        elif selector == 'DEDLine5':
            self.DEDLine5 = value
        else:
            warning(f'No such selector: {selector}')
        debug(f'value: {value}')
        if update:
            self.update_display()


class Ka50Handler(AircraftHandler):
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
        self.l2_apostrophe1 = ''
        self.l2_apostrophe2 = ''
        self.l2_point = ''
        self.l2_sign = ''
        self.l2_text = ''

        self.buffer_l1_apostr1 = StringBuffer(self.g13.parser, 0x1934, 1, lambda s: self.set_data('l1_apostr1', s))
        self.buffer_l1_apostr2 = StringBuffer(self.g13.parser, 0x1936, 1, lambda s: self.set_data('l1_apostr2', s))
        self.buffer_l1_point = StringBuffer(self.g13.parser, 0x1930, 1, lambda s: self.set_data('l1_point', s))
        self.buffer_l1_sign = StringBuffer(self.g13.parser, 0x1920, 1, lambda s: self.set_data('l1_sign', s))
        self.buffer_l1_text = StringBuffer(self.g13.parser, 0x1924, 6, lambda s: self.set_data('l1_text', s))
        self.buffer_l2_apostrophe1 = StringBuffer(self.g13.parser, 0x1938, 1, lambda s: self.set_data('l2_apostrophe1', s))
        self.buffer_l2_apostrophe2 = StringBuffer(self.g13.parser, 0x193a, 1, lambda s: self.set_data('l2_apostrophe2', s))
        self.buffer_l2_point = StringBuffer(self.g13.parser, 0x1932, 1, lambda s: self.set_data('l2_point', s))
        self.buffer_l2_sign = StringBuffer(self.g13.parser, 0x1922, 1, lambda s: self.set_data('l2_sign', s))
        self.buffer_l2_text = StringBuffer(self.g13.parser, 0x192a, 6, lambda s: self.set_data('l2_text', s))

    def button_handle_specific_ac(self, button_pressed: int) -> str:
        debug(f'{self.__class__.__name__} Button: {button_pressed}')
        return '\n'

    def set_data(self, selector, value, update=True) -> None:
        if selector == 'l1_apostr1':
            self.l1_apostr1 = value
        elif selector == 'l1_apostr2':
            self.l1_apostr2 = value
        elif selector == 'l1_point':
            self.l1_point = value
        elif selector == 'l1_sign':
            self.l1_sign = value
        elif selector == 'l1_text':
            self.l1_text = value
        elif selector == 'l2_apostrophe1':
            self.l2_apostrophe1 = value
        elif selector == 'l2_apostrophe2':
            self.l2_apostrophe2 = value
        elif selector == 'l2_point':
            self.l2_point = value
        elif selector == 'l2_sign':
            self.l2_sign = value
        elif selector == 'l2_text':
            self.l2_text = value
        else:
            warning(f'No such selector: {selector}')
        debug(f'value: {value}')
        if update:
            self.update_display()

    def update_display(self) -> None:
        """Update display."""
        super().update_display()
        text1, text2 = '', ''
        if self.l1_text:
            text1 = f' {self.l1_text[-5:-3]}{self.l1_apostr1}{self.l1_text[-3:-1]}{self.l1_apostr2}{self.l1_text[-1]}'
        if self.l2_text:
            text2 = f'{self.l2_text[-6:-3]}{self.l2_apostrophe1}{self.l2_text[-3:-1]}{self.l2_apostrophe2}{self.l2_text[-1]}'
        line1 = self.l1_sign + text1 + self.l1_point
        line2 = self.l2_sign + text2 + self.l2_point
        self.g13.draw.text((0, 0), line1, 1, self.g13.font1)
        self.g13.draw.text((0, 8), line2, 1, self.g13.font1)
        self.g13.update_display(self.g13.img)
