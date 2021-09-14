from functools import partial
from logging import getLogger
from string import whitespace
from typing import Dict, Union, Tuple

from PIL import Image, ImageDraw

from dcspy import FONT, lcd_sdk, LcdSize

try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict

BIOS_VALUE = TypedDict('BIOS_VALUE', {'class': str, 'args': Dict[str, int], 'value': Union[int, str]})
LOG = getLogger(__name__)


class Aircraft:
    def __init__(self, lcd_type: LcdSize) -> None:
        """
        Basic constructor.

        :param lcd_type: LCD type
        """
        self.lcd = lcd_type
        self.bios_data: Dict[str, BIOS_VALUE] = {}

    def button_request(self, button: int, request: str = '\n') -> str:
        """
        Prepare aircraft specific DCS-BIOS request for button pressed.

        For G13/G15/G510: 1-4
        For G19 9-15: LEFT = 9, RIGHT = 10, OK = 11, CANCEL = 12, UP = 13, DOWN = 14, MENU = 15

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
        Prepare image to be send to correct type of LCD.

        :return: image instance ready display on LCD
        :rtype: Image.Image
        """
        img_for_lcd = {1: partial(Image.new, mode='1', size=(self.lcd.width, self.lcd.height), color=0),
                       2: partial(Image.new, mode='RGBA', size=(self.lcd.width, self.lcd.height), color=(0, 0, 0, 0))}
        try:
            img = img_for_lcd[self.lcd.type]()
            getattr(self, f'draw_for_lcd_type_{self.lcd.type}')(img)
            # img.save(path.join(environ.get('TEMP', ''), f'{self.__class__.__name__}.png'), 'PNG')
            return img
        except KeyError as err:
            LOG.debug(f'Wrong LCD type: {self.lcd} or key: {err}')

    def set_bios(self, selector: str, value: str) -> None:
        """
        Set value for DCS-BIOS selector.

        :param selector:
        :param value:
        """
        self.bios_data[selector]['value'] = value
        LOG.debug(f'{self.__class__.__name__} {selector} value: "{value}"')
        lcd_image = self.prepare_image()
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

    def draw_for_lcd_type_1(self, img: Image.Image) -> None:
        """Prepare image for Aircraft for Mono LCD."""
        raise NotImplementedError

    def draw_for_lcd_type_2(self, img: Image.Image) -> None:
        """Prepare image for Aircraft for Color LCD."""
        raise NotImplementedError


class FA18Chornet(Aircraft):
    def __init__(self, lcd_type: LcdSize) -> None:
        """
        Basic constructor.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, BIOS_VALUE] = {
            'UFC_SCRATCHPAD_STRING_1_DISPLAY': {'class': 'StringBuffer', 'args': {'address': 0x744e, 'max_length': 2}, 'value': str()},
            'UFC_SCRATCHPAD_STRING_2_DISPLAY': {'class': 'StringBuffer', 'args': {'address': 0x7450, 'max_length': 2}, 'value': str()},
            'UFC_SCRATCHPAD_NUMBER_DISPLAY': {'class': 'StringBuffer', 'args': {'address': 0x7446, 'max_length': 8}, 'value': str()},
            'UFC_OPTION_DISPLAY_1': {'class': 'StringBuffer', 'args': {'address': 0x7432, 'max_length': 4}, 'value': str()},
            'UFC_OPTION_DISPLAY_2': {'class': 'StringBuffer', 'args': {'address': 0x7436, 'max_length': 4}, 'value': str()},
            'UFC_OPTION_DISPLAY_3': {'class': 'StringBuffer', 'args': {'address': 0x743a, 'max_length': 4}, 'value': str()},
            'UFC_OPTION_DISPLAY_4': {'class': 'StringBuffer', 'args': {'address': 0x743e, 'max_length': 4}, 'value': str()},
            'UFC_OPTION_DISPLAY_5': {'class': 'StringBuffer', 'args': {'address': 0x7442, 'max_length': 4}, 'value': str()},
            'UFC_COMM1_DISPLAY': {'class': 'StringBuffer', 'args': {'address': 0x7424, 'max_length': 2}, 'value': str()},
            'UFC_COMM2_DISPLAY': {'class': 'StringBuffer', 'args': {'address': 0x7426, 'max_length': 2}, 'value': str()},
            'UFC_OPTION_CUEING_1': {'class': 'StringBuffer', 'args': {'address': 0x7428, 'max_length': 1}, 'value': str()},
            'UFC_OPTION_CUEING_2': {'class': 'StringBuffer', 'args': {'address': 0x742a, 'max_length': 1}, 'value': str()},
            'UFC_OPTION_CUEING_3': {'class': 'StringBuffer', 'args': {'address': 0x742c, 'max_length': 1}, 'value': str()},
            'UFC_OPTION_CUEING_4': {'class': 'StringBuffer', 'args': {'address': 0x742e, 'max_length': 1}, 'value': str()},
            'UFC_OPTION_CUEING_5': {'class': 'StringBuffer', 'args': {'address': 0x7430, 'max_length': 1}, 'value': str()},
            'IFEI_FUEL_DOWN': {'class': 'StringBuffer', 'args': {'address': 0x748a, 'max_length': 6}, 'value': str()},
            'IFEI_FUEL_UP': {'class': 'StringBuffer', 'args': {'address': 0x7490, 'max_length': 6}, 'value': str()}}

    def _draw_common_data(self, draw: ImageDraw, foreground: Union[int, Tuple[int, int, int, int]],
                          background: Union[int, Tuple[int, int, int, int]], scale: int) -> ImageDraw:
        scratch_1 = self.get_bios("UFC_SCRATCHPAD_STRING_1_DISPLAY")
        scratch_2 = self.get_bios("UFC_SCRATCHPAD_STRING_2_DISPLAY")
        scratch_num = self.get_bios("UFC_SCRATCHPAD_NUMBER_DISPLAY")
        draw.text(xy=(0, 0), fill=foreground, font=FONT[16 * scale],
                  text=f'{scratch_1}{scratch_2}{scratch_num}')
        draw.line(xy=(0, 20 * scale, 115 * scale, 20 * scale), fill=foreground, width=1)

        draw.rectangle(xy=(0, 29 * scale, 20 * scale, 42 * scale), fill=background, outline=foreground)
        draw.text(xy=(2 * scale, 29 * scale), text=self.get_bios('UFC_COMM1_DISPLAY'), fill=foreground, font=FONT[16 * scale])

        offset_comm2 = 44 * scale
        draw.rectangle(xy=(139 * scale - offset_comm2, 29 * scale, 159 * scale - offset_comm2, 42 * scale), fill=background, outline=foreground)
        draw.text(xy=(140 * scale - offset_comm2, 29 * scale), text=self.get_bios('UFC_COMM2_DISPLAY'), fill=foreground, font=FONT[16 * scale])

        for i in range(1, 6):
            offset = (i - 1) * 8 * scale
            draw.text(xy=(120 * scale, offset), fill=foreground, font=FONT[11 * scale],
                      text=f'{i}{self.get_bios(f"UFC_OPTION_CUEING_{i}")}{self.get_bios(f"UFC_OPTION_DISPLAY_{i}")}')

        draw.text(xy=(36 * scale, 29 * scale), text=self.get_bios('IFEI_FUEL_UP'), fill=foreground, font=FONT[16 * scale])
        return draw

    def draw_for_lcd_type_1(self, img: Image.Image) -> None:
        """Prepare image for F/A-18C Hornet for Mono LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), foreground=255, background=0, scale=1)

    def draw_for_lcd_type_2(self, img: Image.Image) -> None:
        """Prepare image for F/A-18C Hornet for Color LCD."""
        # todo: maybe add some public members, do some scaling and extract color to Logitech
        green = (0, 255, 0, 255)
        black = (0, 0, 0, 0)
        draw = self._draw_common_data(draw=ImageDraw.Draw(img), foreground=green, background=black, scale=2)
        draw.text(xy=(72, 100), text=self.get_bios('IFEI_FUEL_DOWN'), fill=green, font=FONT[32])

    def set_bios(self, selector: str, value: str) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        """
        if selector in ('UFC_SCRATCHPAD_STRING_1_DISPLAY', 'UFC_SCRATCHPAD_STRING_2_DISPLAY',
                        'UFC_COMM1_DISPLAY', 'UFC_COMM2_DISPLAY'):
            value = value.replace('`', '1').replace('~', '2')
        super().set_bios(selector, value)

    def button_request(self, button: int, request: str = '\n') -> str:
        """
        Prepare F/A-18 Hornet specific DCS-BIOS request for button pressed.

        For G13/G15/G510: 1-4
        For G19 9-15: LEFT = 9, RIGHT = 10, OK = 11, CANCEL = 12, UP = 13, DOWN = 14, MENU = 15

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
                  4: 'UFC_COMM2_CHANNEL_SELECT INC\n',
                  9: 'UFC_COMM1_CHANNEL_SELECT DEC\n',
                  10: 'UFC_COMM1_CHANNEL_SELECT INC\n',
                  14: 'UFC_COMM2_CHANNEL_SELECT DEC\n',
                  13: 'UFC_COMM2_CHANNEL_SELECT INC\n',
                  15: 'IFEI_DWN_BTN 1\nIFEI_DWN_BTN 0\n',
                  12: 'IFEI_UP_BTN 1\nIFEI_UP_BTN 0\n'}
        return super().button_request(button, action.get(button, '\n'))


class F16C50(Aircraft):
    def __init__(self, lcd_type: LcdSize) -> None:
        """
        Basic constructor.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, BIOS_VALUE] = {
            'DED_LINE_1': {'class': 'StringBuffer', 'args': {'address': 0x4500, 'max_length': 25}, 'value': str()},
            'DED_LINE_2': {'class': 'StringBuffer', 'args': {'address': 0x451a, 'max_length': 25}, 'value': str()},
            'DED_LINE_3': {'class': 'StringBuffer', 'args': {'address': 0x4534, 'max_length': 25}, 'value': str()},
            'DED_LINE_4': {'class': 'StringBuffer', 'args': {'address': 0x454e, 'max_length': 25}, 'value': str()},
            'DED_LINE_5': {'class': 'StringBuffer', 'args': {'address': 0x4568, 'max_length': 25}, 'value': str()}}

    def draw_for_lcd_type_1(self, img: Image.Image) -> None:
        """Prepare image for F-16C Viper for Mono LCD."""
        draw = ImageDraw.Draw(img)
        for i in range(1, 6):
            offset = (i - 1) * 8
            # replace 'o' to degree sign and 'a' with up-down arrow
            text = str(self.get_bios(f'DED_LINE_{i}')).replace('o', '\u00b0').replace('a', '\u2195')
            draw.text(xy=(0, offset), text=text, fill=255, font=FONT[11])

    def draw_for_lcd_type_2(self, img: Image.Image) -> None:
        """Prepare image for F-16C Viper for Color LCD."""
        draw = ImageDraw.Draw(img)
        green = (0, 255, 0, 255)
        for i in range(1, 6):
            offset = (i - 1) * 16
            # replace 'o' to degree sign and 'a' with up-down arrow
            text = str(self.get_bios(f'DED_LINE_{i}')).replace('o', '\u00b0').replace('a', '\u2195')
            draw.text(xy=(0, offset), text=text, fill=green, font=FONT[22])


class Ka50(Aircraft):
    def __init__(self, lcd_type: LcdSize) -> None:
        """
        Basic constructor.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, BIOS_VALUE] = {
            'PVI_LINE1_APOSTROPHE1': {'class': 'StringBuffer', 'args': {'address': 0x1934, 'max_length': 1}, 'value': str()},
            'PVI_LINE1_APOSTROPHE2': {'class': 'StringBuffer', 'args': {'address': 0x1936, 'max_length': 1}, 'value': str()},
            'PVI_LINE1_POINT': {'class': 'StringBuffer', 'args': {'address': 0x1930, 'max_length': 1}, 'value': str()},
            'PVI_LINE1_SIGN': {'class': 'StringBuffer', 'args': {'address': 0x1920, 'max_length': 1}, 'value': str()},
            'PVI_LINE1_TEXT': {'class': 'StringBuffer', 'args': {'address': 0x1924, 'max_length': 6}, 'value': str()},
            'PVI_LINE2_APOSTROPHE1': {'class': 'StringBuffer', 'args': {'address': 0x1938, 'max_length': 1}, 'value': str()},
            'PVI_LINE2_APOSTROPHE2': {'class': 'StringBuffer', 'args': {'address': 0x193a, 'max_length': 1}, 'value': str()},
            'PVI_LINE2_POINT': {'class': 'StringBuffer', 'args': {'address': 0x1932, 'max_length': 1}, 'value': str()},
            'PVI_LINE2_SIGN': {'class': 'StringBuffer', 'args': {'address': 0x1922, 'max_length': 1}, 'value': str()},
            'PVI_LINE2_TEXT': {'class': 'StringBuffer', 'args': {'address': 0x192a, 'max_length': 6}, 'value': str()},
            'AP_ALT_HOLD_LED': {'class': 'IntegerBuffer', 'args': {'address': 0x1936, 'mask': 0x8000, 'shift_by': 0xf}, 'value': int()},
            'AP_BANK_HOLD_LED': {'class': 'IntegerBuffer', 'args': {'address': 0x1936, 'mask': 0x200, 'shift_by': 0x9}, 'value': int()},
            'AP_FD_LED': {'class': 'IntegerBuffer', 'args': {'address': 0x1938, 'mask': 0x200, 'shift_by': 0x9}, 'value': int()},
            'AP_HDG_HOLD_LED': {'class': 'IntegerBuffer', 'args': {'address': 0x1936, 'mask': 0x800, 'shift_by': 0xb}, 'value': int()},
            'AP_PITCH_HOLD_LED': {'class': 'IntegerBuffer', 'args': {'address': 0x1936, 'mask': 0x2000, 'shift_by': 0xd}, 'value': int()}}

    def button_request(self, button: int, request: str = '\n') -> str:
        """
        Prepare Ka-50 Black Shark specific DCS-BIOS request for button pressed.

        For G13/G15/G510: 1-4
        For G19 9-15: LEFT = 9, RIGHT = 10, OK = 11, CANCEL = 12, UP = 13, DOWN = 14, MENU = 15

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
                  4: 'PVI_TARGETS_BTN 1\nPVI_TARGETS_BTN 0\n',
                  9: 'PVI_WAYPOINTS_BTN 1\nPVI_WAYPOINTS_BTN 0\n',
                  10: 'PVI_FIXPOINTS_BTN 1\nPVI_FIXPOINTS_BTN 0\n',
                  14: 'PVI_AIRFIELDS_BTN 1\nPVI_AIRFIELDS_BTN 0\n',
                  13: 'PVI_TARGETS_BTN 1\nPVI_TARGETS_BTN 0\n'}
        return super().button_request(button, action.get(button, '\n'))

    def _auto_pilot_switch_1(self, draw_obj: ImageDraw) -> None:
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
                draw_obj.rectangle(c_rect, fill=255, outline=255)
                draw_obj.text(xy=c_text, text=ap_channel, fill=0, font=FONT[16])
            else:
                draw_obj.rectangle(xy=c_rect, fill=0, outline=255)
                draw_obj.text(xy=c_text, text=ap_channel, fill=255, font=FONT[16])

    def _auto_pilot_switch_2(self, draw_obj: ImageDraw) -> None:
        """
        Draw rectangle and add text for autopilot channels in correct coordinates.

        :param draw_obj: ImageDraw object form PIL
        """
        green = (0, 255, 0, 255)
        black = (0, 0, 0, 0)
        for c_rect, c_text, ap_channel, turn_on in (((222, 2, 248, 36), (228, 6), 'B', self.get_bios('AP_BANK_HOLD_LED')),
                                                    ((256, 2, 282, 36), (260, 6), 'P', self.get_bios('AP_PITCH_HOLD_LED')),
                                                    ((290, 2, 316, 36), (294, 6), 'F', self.get_bios('AP_FD_LED')),
                                                    ((222, 44, 248, 78), (228, 48), 'H', self.get_bios('AP_HDG_HOLD_LED')),
                                                    ((256, 44, 282, 78), (260, 48), 'A', self.get_bios('AP_ALT_HOLD_LED'))):
            if turn_on:
                draw_obj.rectangle(c_rect, fill=green, outline=green)
                draw_obj.text(xy=c_text, text=ap_channel, fill=black, font=FONT[32])
            else:
                draw_obj.rectangle(xy=c_rect, fill=black, outline=green)
                draw_obj.text(xy=c_text, text=ap_channel, fill=green, font=FONT[32])

    def draw_for_lcd_type_1(self, img: Image.Image) -> None:
        """Prepare image for Ka-50 Black Shark for Mono LCD."""
        draw = ImageDraw.Draw(img)
        for rect_xy in [(0, 1, 85, 18), (0, 22, 85, 39), (88, 1, 103, 18), (88, 22, 103, 39)]:
            draw.rectangle(xy=rect_xy, fill=0, outline=255)
        line1, line2 = self._generate_pvi_lines()
        draw.text(xy=(2, 3), text=line1, fill=255, font=FONT[16])
        draw.text(xy=(2, 24), text=line2, fill=255, font=FONT[16])
        self._auto_pilot_switch_1(draw)

    def draw_for_lcd_type_2(self, img: Image.Image) -> None:
        """Prepare image for Ka-50 Black Shark for Mono LCD."""
        draw = ImageDraw.Draw(img)
        green = (0, 255, 0, 255)
        black = (0, 0, 0, 0)
        for rect_xy in [(0, 2, 170, 36), (0, 44, 170, 78), (176, 2, 206, 36), (176, 44, 203, 78)]:
            draw.rectangle(xy=rect_xy, fill=black, outline=green)
        line1, line2 = self._generate_pvi_lines()
        draw.text(xy=(4, 6), text=line1, fill=green, font=FONT[32])
        draw.text(xy=(4, 48), text=line2, fill=green, font=FONT[32])
        self._auto_pilot_switch_2(draw)

    def _generate_pvi_lines(self) -> Tuple[str, str]:
        text1, text2 = '', ''
        line1_text = str(self.get_bios('PVI_LINE1_TEXT'))
        line2_text = str(self.get_bios('PVI_LINE2_TEXT'))
        if line1_text:
            l1_apostr1 = self.get_bios("PVI_LINE1_APOSTROPHE1")
            l1_apostr2 = self.get_bios("PVI_LINE1_APOSTROPHE2")
            text1 = f'{line1_text[-6:-3]}{l1_apostr1}{line1_text[-3:-1]}{l1_apostr2}{line1_text[-1]}'
        if line2_text:
            l2_apostr1 = self.get_bios("PVI_LINE2_APOSTROPHE1")
            l2_apostr2 = self.get_bios("PVI_LINE2_APOSTROPHE2")
            text2 = f'{line2_text[-6:-3]}{l2_apostr1}{line2_text[-3:-1]}{l2_apostr2}{line2_text[-1]}'
        line1 = f'{self.get_bios("PVI_LINE1_SIGN")}{text1} {self.get_bios("PVI_LINE1_POINT")}'
        line2 = f'{self.get_bios("PVI_LINE2_SIGN")}{text2} {self.get_bios("PVI_LINE2_POINT")}'
        return line1, line2


class F14B(Aircraft):
    def __init__(self, lcd_type: LcdSize) -> None:
        """
        Basic constructor.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, BIOS_VALUE] = {
            'RIO_CAP_CLEAR': {'class': 'IntegerBuffer', 'args': {'address': 0x12c4, 'mask': 0x4000, 'shift_by': 0xe}, 'value': int()},
            'RIO_CAP_SW': {'class': 'IntegerBuffer', 'args': {'address': 0x12c4, 'mask': 0x2000, 'shift_by': 0xd}, 'value': int()},
            'RIO_CAP_NE': {'class': 'IntegerBuffer', 'args': {'address': 0x12c4, 'mask': 0x1000, 'shift_by': 0xc}, 'value': int()},
            'RIO_CAP_ENTER': {'class': 'IntegerBuffer', 'args': {'address': 0x12c4, 'mask': 0x8000, 'shift_by': 0xf}, 'value': int()}}

    def button_request(self, button: int, request: str = '\n') -> str:
        """
        Prepare F-14 Tomcat specific DCS-BIOS request for button pressed.

        For G13/G15/G510: 1-4
        For G19 9-15: LEFT = 9, RIGHT = 10, OK = 11, CANCEL = 12, UP = 13, DOWN = 14, MENU = 15

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
                  4: 'RIO_CAP_ENTER 1\nRIO_CAP_ENTER 0\n',
                  9: 'RIO_CAP_CLEAR 1\nRIO_CAP_CLEAR 0\n',
                  10: 'RIO_CAP_SW 1\nRIO_CAP_SW 0\n',
                  14: 'RIO_CAP_NE 1\nRIO_CAP_NE 0\n',
                  13: 'RIO_CAP_ENTER 1\nRIO_CAP_ENTER 0\n'}
        return super().button_request(button, action.get(button, '\n'))

    def draw_for_lcd_type_1(self, img: Image.Image) -> None:
        """Prepare image for F-14B Tomcat for Mono LCD."""
        draw = ImageDraw.Draw(img)
        draw.text(xy=(2, 3), text='F-14B Tomcat', fill=255, font=FONT[16])

    def draw_for_lcd_type_2(self, img: Image.Image) -> None:
        """Prepare image for F-14B Tomcat for Color LCD."""
        draw = ImageDraw.Draw(img)
        green = (0, 255, 0, 255)
        draw.text(xy=(2, 3), text='F-14B Tomcat', fill=green, font=FONT[32])
