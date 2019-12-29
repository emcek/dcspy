from abc import abstractmethod
from logging import basicConfig, DEBUG, debug

from PIL import Image, ImageFont, ImageDraw

import GLCD_SDK
from dcsbiosParser import ProtocolParser

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
        self.width = GLCD_SDK.MONO_WIDTH
        self.height = GLCD_SDK.MONO_WIDTH
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
            request = 'UFC_COMM1_CHANNEL_SELECT -3200\n'
        elif button_pressed == 2:
            request = 'UFC_COMM1_CHANNEL_SELECT +3200\n'
        elif button_pressed == 3:
            request = 'UFC_COMM2_CHANNEL_SELECT -3200\n'
        elif button_pressed == 4:
            request = 'UFC_COMM2_CHANNEL_SELECT +3200\n'
        debug(f'Button: {button_pressed} Request: {request}')
        return request

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
