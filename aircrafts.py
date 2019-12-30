from abc import abstractmethod
from logging import basicConfig, DEBUG, debug, warning
from typing import Any

from PIL import Image, ImageFont, ImageDraw

from lcd_sdk import MONO_HEIGHT, MONO_WIDTH
from dcsbios import ProtocolParser, StringBuffer

basicConfig(format='%(asctime)s | %(levelname)-6s | %(message)s / %(filename)s:%(lineno)d', level=DEBUG)


class AircraftHandler:
    def __init__(self, display_handler, parser: ProtocolParser) -> None:
        """
        Basic constructor.

        :param display_handler:
        :type display_handler: G13Handler
        :param parser:
        :type parser: ProtocolParser
        """
        self.g13 = display_handler
        self.parser = parser
        self.width = MONO_WIDTH
        self.height = MONO_HEIGHT
        self.img = Image.new('1', (self.width, self.height), 0)
        self.draw = ImageDraw.Draw(self.img)
        self.font1 = ImageFont.truetype('consola.ttf', 11)
        self.font2 = ImageFont.truetype('consola.ttf', 16)

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
        debug(f'Button: {button_pressed} Request: {request}')
        return f'{request}\n'

    def update_display(self) -> None:
        """Update display."""
        self.draw.rectangle((0, 0, self.width, self.height), 0, 0)  # clear bitmap

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
    def __init__(self, display_handler, parser: ProtocolParser) -> None:
        """
        Basic constructor.

        :param display_handler:
        :type display_handler: G13Handler
        :param parser:
        :type parser: ProtocolParser
        """
        super().__init__(display_handler, parser)
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

        self.bufferScratchpadString1Display = StringBuffer(parser, 0x744e, 2, lambda s: self.set_data(1, s))
        self.bufferScratchpadString2Display = StringBuffer(parser, 0x7450, 2, lambda s: self.set_data(2, s))
        self.bufferScratchpadNumberDisplay = StringBuffer(parser, 0x7446, 8, lambda s: self.set_data(3, s))
        self.bufferOptionDisplay1 = StringBuffer(parser, 0x7432, 4, lambda s: self.set_data(11, s))
        self.bufferOptionDisplay2 = StringBuffer(parser, 0x7436, 4, lambda s: self.set_data(12, s))
        self.bufferOptionDisplay3 = StringBuffer(parser, 0x743a, 4, lambda s: self.set_data(13, s))
        self.bufferOptionDisplay4 = StringBuffer(parser, 0x743e, 4, lambda s: self.set_data(14, s))
        self.bufferOptionDisplay5 = StringBuffer(parser, 0x7442, 4, lambda s: self.set_data(15, s))
        self.bufferCOMM1Display = StringBuffer(parser, 0x7424, 2, lambda s: self.set_data(21, s))
        self.bufferCOMM2Display = StringBuffer(parser, 0x7426, 2, lambda s: self.set_data(22, s))
        self.bufferOptionCueing1 = StringBuffer(parser, 0x7428, 1, lambda s: self.set_data(31, s))
        self.bufferOptionCueing2 = StringBuffer(parser, 0x742a, 1, lambda s: self.set_data(32, s))
        self.bufferOptionCueing3 = StringBuffer(parser, 0x742c, 1, lambda s: self.set_data(33, s))
        self.bufferOptionCueing4 = StringBuffer(parser, 0x742e, 1, lambda s: self.set_data(34, s))
        self.bufferOptionCueing5 = StringBuffer(parser, 0x7430, 1, lambda s: self.set_data(35, s))
        self.bufferFuelTotal = StringBuffer(parser, 0x748a, 6, lambda s: self.set_data(40, s))

    def update_display(self) -> None:
        """Update display."""
        super().update_display()

        # Scrachpad
        self.draw.text((0, 0),
                       self.ScratchpadString1Display + self.ScratchpadString2Display + self.ScratchpadNumberDisplay,
                       1,
                       self.font2)
        self.draw.line((0, 20, 115, 20), 1, 1)

        # comm1
        self.draw.rectangle((0, 29, 20, 42), 0, 1)
        self.draw.text((2, 29), self.COMM1Display, 1, self.font2)

        # comm2
        offset_comm2 = 44
        self.draw.rectangle((139 - offset_comm2, 29, 159 - offset_comm2, 42), 0, 1)
        self.draw.text((140 - offset_comm2, 29), self.COMM2Display, 1, self.font2)

        # option display 1..5 with cueing
        pos = 0
        offset = 8
        self.draw.text((120, pos), '1' + self.OptionCueing1 + self.OptionDisplay1, 1, self.font1)
        pos += offset
        self.draw.text((120, pos), '2' + self.OptionCueing2 + self.OptionDisplay2, 1, self.font1)
        pos += offset
        self.draw.text((120, pos), '3' + self.OptionCueing3 + self.OptionDisplay3, 1, self.font1)
        pos += offset
        self.draw.text((120, pos), '4' + self.OptionCueing4 + self.OptionDisplay4, 1, self.font1)
        pos += offset
        self.draw.text((120, pos), '5' + self.OptionCueing5 + self.OptionDisplay5, 1, self.font1)

        # Fuel Totaliser
        self.draw.text((36, 29), self.FuelTotal, 1, self.font2)

        # make it array and set proper values
        pixels = list(self.img.getdata())
        for i in range(0, len(pixels)):
            pixels[i] *= 128

        self.g13.update_display(pixels)

    def set_data(self, selector: int, value: Any, update=True) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        :param update:
        """
        # programming noob here, but it's pretty clear how to use this monster
        if selector == 1:
            modified_string = value
            modified_string = modified_string.replace('`', '1')
            modified_string = modified_string.replace('~', '2')
            self.ScratchpadString1Display = modified_string
        elif selector == 2:
            modified_string = value
            modified_string = modified_string.replace('`', '1')
            modified_string = modified_string.replace('~', '2')
            self.ScratchpadString2Display = modified_string
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
            modified_string = value
            modified_string = modified_string.replace('`', '1')
            modified_string = modified_string.replace('~', '2')
            self.COMM1Display = modified_string
        elif selector == 22:
            modified_string = value
            modified_string = modified_string.replace('`', '1')
            modified_string = modified_string.replace('~', '2')
            self.COMM2Display = modified_string
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
    def __init__(self, display_handler, parser: ProtocolParser) -> None:
        """
        Basic constructor.

        :param display_handler:
        :type display_handler: G13Handler
        :param parser:
        :type parser: ProtocolParser
        """
        super().__init__(display_handler, parser)
        self.DEDLine1 = ""
        self.DEDLine2 = ""
        self.DEDLine3 = ""
        self.DEDLine4 = ""
        self.DEDLine5 = ""

        self.bufferDEDLine1 = StringBuffer(parser, 0x44fc, 50, lambda s: self.set_data('DEDLine1', s))
        self.bufferDEDLine2 = StringBuffer(parser, 0x452e, 50, lambda s: self.set_data('DEDLine2', s))
        self.bufferDEDLine3 = StringBuffer(parser, 0x4560, 50, lambda s: self.set_data('DEDLine3', s))
        self.bufferDEDLine4 = StringBuffer(parser, 0x4592, 50, lambda s: self.set_data('DEDLine4', s))
        self.bufferDEDLine5 = StringBuffer(parser, 0x45c4, 50, lambda s: self.set_data('DEDLine5', s))

    def update_display(self) -> None:
        """Update display."""
        super().update_display()

        pos = 0
        offsetpos = 8
        self.draw.text((0, pos), self.DEDLine1, 1, self.font1)
        pos = pos + offsetpos
        self.draw.text((0, pos), self.DEDLine2, 1, self.font1)
        pos = pos + offsetpos
        self.draw.text((0, pos), self.DEDLine3, 1, self.font1)
        pos = pos + offsetpos
        self.draw.text((0, pos), self.DEDLine4, 1, self.font1)
        pos = pos + offsetpos
        self.draw.text((0, pos), self.DEDLine5, 1, self.font1)

        # make it array and set proper values
        pixels = list(self.img.getdata())
        for i in range(0, len(pixels)):
            pixels[i] *= 128

        self.g13.update_display(pixels)

    def set_data(self, selector: str, value: Any, update=True) -> None:
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
