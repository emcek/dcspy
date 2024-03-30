from enum import Enum
from itertools import cycle
from logging import getLogger
from pathlib import Path
from pprint import pformat
from re import search
from tempfile import gettempdir
from typing import Dict, List, Sequence, Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from dcspy import default_yaml, load_yaml
from dcspy.models import DEFAULT_FONT_NAME, NO_OF_LCD_SCREENSHOTS, Gkey, LcdButton, LcdInfo, LcdType, MouseButton, RequestModel, RequestType
from dcspy.utils import KeyRequest, replace_symbols, substitute_symbols

LOG = getLogger(__name__)


class MetaAircraft(type):
    """Metaclass for all BasicAircraft."""
    def __new__(cls, name, bases, namespace):
        """
        Create new instance of any plane as BasicAircraft.

        You can crate instance of any plane:
        f22a = MetaAircraft('F-22A', (BasicAircraft,), {})(lcd_type: LcdInfo)

        :param name:
        :param bases:
        :param namespace:
        """
        return super().__new__(cls, name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        """
        Create new instance of any BasicAircraft.

        :param args:
        :param kwargs:
        """
        LOG.debug(f'Creating {cls.__name__} with: {args[0].type}')
        return super().__call__(*args, **kwargs)


class BasicAircraft:
    """Basic Aircraft."""
    bios_name: str = ''

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create basic aircraft.

        :param lcd_type: LCD type
        """
        self.lcd = lcd_type
        self.cfg = load_yaml(full_path=default_yaml)
        self.bios_data: Dict[str, Union[str, int]] = {}
        if self.bios_name:
            self.key_req = KeyRequest(yaml_path=default_yaml.parent / f'{self.bios_name}.yaml', get_bios_fn=self.get_bios)
            self.bios_data.update(self.key_req.cycle_button_ctrl_name)

    def button_request(self, button: Union[LcdButton, Gkey, MouseButton]) -> RequestModel:
        """
        Prepare aircraft specific DCS-BIOS request for button pressed.

        :param button: LcdButton, Gkey or MouseButton
        :return: ready to send DCS-BIOS request
        """
        LOG.debug(f'{type(self).__name__} Button: {button}')
        request = self.key_req.get_request(button)
        LOG.debug(f'Request: {request}')
        return request

    def set_bios(self, selector: str, value: Union[str, int]) -> None:
        """
        Set value for DCS-BIOS selector.

        :param selector:
        :param value:
        """
        self.bios_data[selector] = value
        LOG.debug(f'{type(self).__name__} {selector} value: "{value}" ({type(value).__name__})')

    def get_bios(self, selector: str, default: Union[str, int, float] = '') -> Union[str, int, float]:
        """
        Get value for DCS-BIOS selector.

        :param selector: name of selector
        :param default: return this when fetch fail
        """
        try:
            return type(default)(self.bios_data[selector])
        except (KeyError, ValueError):
            return default

    def __repr__(self) -> str:
        return f'{super().__repr__()} with: {pformat(self.__dict__)}'


class AdvancedAircraft(BasicAircraft):
    """Advanced Aircraft."""
    def __init__(self, lcd_type: LcdInfo, **kwargs) -> None:
        """
        Create advanced aircraft.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type=lcd_type)
        self.update_display = kwargs.get('update_display', None)
        if self.update_display:
            self.bios_data.update(kwargs.get('bios_data', {}))
        self._debug_img = cycle([f'{x:03}' for x in range(NO_OF_LCD_SCREENSHOTS)])

    def set_bios(self, selector: str, value: Union[str, int]) -> None:
        """
        Set value for DCS-BIOS selector and update LCD with image.

        :param selector:
        :param value:
        """
        super().set_bios(selector=selector, value=value)
        if self.update_display:
            self.update_display(self.prepare_image())

    def prepare_image(self) -> Image.Image:
        """
        Prepare image to be sent to correct type of LCD.

        :return: image instance ready display on LCD
        """
        img = Image.new(mode=self.lcd.mode.value, size=(self.lcd.width.value, self.lcd.height.value), color=self.lcd.background)
        getattr(self, f'draw_for_lcd_{self.lcd.type.name.lower()}')(img)
        if self.cfg.get('save_lcd', False):
            screen_shot_file = f'{type(self).__name__}_{next(self._debug_img)}.png'
            img.save(Path(gettempdir()) / screen_shot_file, 'PNG')
            LOG.debug(f'Save screenshot: {screen_shot_file}')
        return img

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for Aircraft for Mono LCD."""
        raise NotImplementedError

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for Aircraft for Color LCD."""
        raise NotImplementedError


class FA18Chornet(AdvancedAircraft):
    """F/A-18C Hornet."""
    bios_name: str = 'FA-18C_hornet'

    def __init__(self, lcd_type: LcdInfo, **kwargs) -> None:
        """
        Create F/A-18C Hornet.

        :param lcd_type: LCD type
        """
        bios_data = {
            'UFC_SCRATCHPAD_STRING_1_DISPLAY': '',
            'UFC_SCRATCHPAD_STRING_2_DISPLAY': '',
            'UFC_SCRATCHPAD_NUMBER_DISPLAY': '',
            'UFC_OPTION_DISPLAY_1': '',
            'UFC_OPTION_DISPLAY_2': '',
            'UFC_OPTION_DISPLAY_3': '',
            'UFC_OPTION_DISPLAY_4': '',
            'UFC_OPTION_DISPLAY_5': '',
            'UFC_COMM1_DISPLAY': '',
            'UFC_COMM2_DISPLAY': '',
            'UFC_OPTION_CUEING_1': '',
            'UFC_OPTION_CUEING_2': '',
            'UFC_OPTION_CUEING_3': '',
            'UFC_OPTION_CUEING_4': '',
            'UFC_OPTION_CUEING_5': '',
            'IFEI_FUEL_DOWN': '',
            'IFEI_FUEL_UP': '',
            'HUD_ATT_SW': int(),
            'IFEI_DWN_BTN': int(),
            'IFEI_UP_BTN': int(),
        }
        super().__init__(lcd_type=lcd_type, bios_data=bios_data, **kwargs)

    def _draw_common_data(self, draw: ImageDraw.ImageDraw, scale: int) -> ImageDraw.ImageDraw:
        """
        Draw common part (based on scale) for Mono and Color LCD.

        :param draw: ImageDraw instance
        :param scale: scaling factor (Mono 1, Color 2)
        :return: updated image to draw
        """
        scratch_1 = self.get_bios('UFC_SCRATCHPAD_STRING_1_DISPLAY')
        scratch_2 = self.get_bios('UFC_SCRATCHPAD_STRING_2_DISPLAY')
        scratch_num = self.get_bios('UFC_SCRATCHPAD_NUMBER_DISPLAY')
        draw.text(xy=(0, 0), fill=self.lcd.foreground, font=self.lcd.font_l,
                  text=f'{scratch_1}{scratch_2}{scratch_num}')
        draw.line(xy=(0, 20 * scale, 115 * scale, 20 * scale), fill=self.lcd.foreground, width=1)

        draw.rectangle(xy=(0, 29 * scale, 20 * scale, 42 * scale), fill=self.lcd.background, outline=self.lcd.foreground)
        draw.text(xy=(2 * scale, 29 * scale), text=str(self.get_bios('UFC_COMM1_DISPLAY')), fill=self.lcd.foreground, font=self.lcd.font_l)

        offset = 44 * scale
        draw.rectangle(xy=(139 * scale - offset, 29 * scale, 159 * scale - offset, 42 * scale), fill=self.lcd.background, outline=self.lcd.foreground)
        draw.text(xy=(140 * scale - offset, 29 * scale), text=str(self.get_bios('UFC_COMM2_DISPLAY')), fill=self.lcd.foreground, font=self.lcd.font_l)

        for i in range(1, 6):
            offset = (i - 1) * 8 * scale
            draw.text(xy=(120 * scale, offset), fill=self.lcd.foreground, font=self.lcd.font_s,
                      text=f'{i}{self.get_bios(f"UFC_OPTION_CUEING_{i}")}{self.get_bios(f"UFC_OPTION_DISPLAY_{i}")}')

        draw.text(xy=(36 * scale, 29 * scale), text=str(self.get_bios('IFEI_FUEL_UP')), fill=self.lcd.foreground, font=self.lcd.font_l)
        return draw

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for F/A-18C Hornet for Mono LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), scale=1)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for F/A-18C Hornet for Color LCD."""
        draw = self._draw_common_data(draw=ImageDraw.Draw(img), scale=2)
        draw.text(xy=(72, 100), text=str(self.get_bios('IFEI_FUEL_DOWN')), fill=self.lcd.foreground, font=self.lcd.font_l)

    def set_bios(self, selector: str, value: Union[str, int]) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        """
        if selector in ('UFC_SCRATCHPAD_STRING_1_DISPLAY', 'UFC_SCRATCHPAD_STRING_2_DISPLAY',
                        'UFC_COMM1_DISPLAY', 'UFC_COMM2_DISPLAY'):
            value = str(value).replace('`', '1').replace('~', '2')
        super().set_bios(selector, value)


class F16C50(AdvancedAircraft):
    """F-16C Viper."""
    bios_name: str = 'F-16C_50'
    # List page
    COMMON_SYMBOLS_TO_REPLACE = (
        ('A\x10\x04', ''), ('\x82', ''), ('\x03', ''), ('\x02', ''), ('\x80', ''), ('\x08', ''), ('\x10', ''),
        ('\x07', ''), ('\x0f', ''), ('\xfe', ''), ('\xfc', ''), ('\x03', ''), ('\xff', ''), ('\xc0', '')
    )
    # degree sign, 'a' to up-down arrow 2195 or black diamond 2666, INVERSE WHITE CIRCLE
    MONO_SYMBOLS_TO_REPLACE = (('o', '\u00b0'), ('a', '\u2666'), ('*', '\u25d9'))
    # degree sign, fix up-down triangle arrow, fix to inverse star
    COLOR_SYMBOLS_TO_REPLACE = (('o', '\u005e'), ('a', '\u0040'), ('*', '\u00d7'))
    COLOR_SYMBOLS_TO_SUBSTITUTE = (
        (r'1DEST\s2BNGO\s3VIP\s{2}RINTG', '\u00c1DEST \u00c2BNGO \u00c3VIP  \u0072INTG'),
        (r'4NAV\s{2}5MAN\s{2}6INS\s{2}EDLNK', '\u00c4NAV  \u00c5MAN  \u00c6INS  \u0065DLNK'),
        (r'7CMDS\s8MODE\s9VRP\s{2}0MISC', '\u00c7CMDS \u00c8MODE \u00c9VRP  \u00c0MISC'),
        (r'1CORR\s2MAGV\s3OFP\s{2}RHMCS', '\u00c1CORR \u00c2MAGV \u00c3OFP  \u0072HMCS'),
        (r'4INSM\s5LASR\s6GPS\s{2}E', '\u00c4INSM \u00c5LASR \u00c6GPS  \u0065'),
        (r'7DRNG\s8BULL\s9\s{5}0', '\u00c7DRNG \u00c8BULL \u00c9     \u00c0'),
        (r'(M1\s:\d+\s+)M4(\s+\(\d\).*)', r'\1mÄ\2'),
        (r'M1(\s:\d+\s+)M4(\s+:\s+\(\d\).*)', r'mÁ\1mÄ\2'),
        (r'M3(\s+:\d+\s+×\s+\d×[A-Z]+\(\d\).*)', r'mÃ\1'),
        (r'(\s[\s|×])HUD BLNK([×|\s]\s+)', r'\1hud blnk\2'),
        (r'(\s[\s|×])CKPT BLNK([×|\s]\s+)', r'\1ckpt blnk\2')
    )

    def __init__(self, lcd_type: LcdInfo, **kwargs) -> None:
        """
        Create F-16C Viper.

        :param lcd_type: LCD type
        """
        bios_data = {f'DED_LINE_{i}': '' for i in range(1, 6)}
        super().__init__(lcd_type=lcd_type, bios_data=bios_data, **kwargs)
        self.font = self.lcd.font_s
        self.ded_font = self.cfg.get('f16_ded_font', True)
        if self.ded_font and self.lcd.type == LcdType.COLOR:
            self.font = ImageFont.truetype(str((Path(__file__) / '..' / 'resources' / 'falconded.ttf').resolve()), 25)

    def _draw_common_data(self, draw: ImageDraw.ImageDraw, separation: int) -> None:
        """
        Draw common part (based on scale) for Mono and Color LCD.

        :param draw: ImageDraw instance
        :param separation: between lines in pixels
        """
        for i in range(1, 6):
            offset = (i - 1) * separation
            draw.text(xy=(0, offset), text=str(self.get_bios(f'DED_LINE_{i}')), fill=self.lcd.foreground, font=self.font)

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for F-16C Viper for Mono LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), separation=8)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for F-16C Viper for Color LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), separation=24)

    def set_bios(self, selector: str, value: Union[str, int]) -> None:
        """
        Catch BIOS changes and remove garbage characters and replace with correct ones.

        :param selector: selector name
        :param value: value form DCS-BIOS
        """
        if 'DED_LINE_' in selector:
            value = str(value)
            LOG.debug(f'{type(self).__name__} {selector} org  : "{value}"')
            value = self._clean_and_replace(value)
        super().set_bios(selector, value)

    def _clean_and_replace(self, value: str) -> str:
        """
        Clean and replace garbage characters before print to LCD.

        :param value: The string value to be cleaned and replaced.
        :return: The cleaned and replaced string value.
        """
        value = replace_symbols(value, self.COMMON_SYMBOLS_TO_REPLACE)
        if value and value[-1] == '@':
            value = value.replace('@', '')  # List - 6
        if self.lcd.type == LcdType.MONO:
            value = self._replace_symbols_for_mono_lcd(value)
        elif self.ded_font and self.lcd.type == LcdType.COLOR:
            value = self._replace_symbols_for_color_lcd(value)
        return value

    def _replace_symbols_for_mono_lcd(self, value: str) -> str:
        """
        Clean and replace garbage characters for Mono LCD.

        :param value: The input string that needs to be modified.
        :return: The modified string after replacing symbols based on the MONO_SYMBOLS_TO_REPLACE dictionary.
        """
        return replace_symbols(value, self.MONO_SYMBOLS_TO_REPLACE)

    def _replace_symbols_for_color_lcd(self, value: str) -> str:
        """
        Clean and replace garbage characters for Color LCD.

        :param value: The input string value.
        :return: The modified string with replaced symbols.
        """
        value = replace_symbols(value, self.COLOR_SYMBOLS_TO_REPLACE)
        value = substitute_symbols(value, self.COLOR_SYMBOLS_TO_SUBSTITUTE)
        return value


class F15ESE(AdvancedAircraft):
    """F-15ESE Eagle."""
    bios_name: str = 'F-15ESE'

    def __init__(self, lcd_type: LcdInfo, **kwargs) -> None:
        """
        Create F-15ESE Egle.

        :param lcd_type: LCD type
        """
        bios_data = {f'F_UFC_LINE{i}_DISPLAY': '' for i in range(1, 7)}
        super().__init__(lcd_type=lcd_type, bios_data=bios_data, **kwargs)

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for F-15ESE Eagle for Mono LCD."""
        draw = ImageDraw.Draw(img)
        for i in range(1, 6):
            offset = (i - 1) * 8
            draw.text(xy=(0, offset), text=str(self.get_bios(f'F_UFC_LINE{i}_DISPLAY')), fill=self.lcd.foreground, font=self.lcd.font_s)
        if mat := search(r'\s*([0-9G]{1,2})\s+([0-9GV]{1,2})\s+', str(self.get_bios('F_UFC_LINE6_DISPLAY'))):
            uhf, v_uhf = mat.groups()
            draw.text(xy=(130, 30), text=f'{uhf:>2} {v_uhf:>2}', fill=self.lcd.foreground, font=self.lcd.font_s)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for F-15ESE Eagle for Color LCD."""
        draw = ImageDraw.Draw(img)
        for i in range(1, 7):
            offset = (i - 1) * 24
            # todo: fix custom font for Color LCD
            draw.text(xy=(0, offset),
                      text=str(self.get_bios(f'F_UFC_LINE{i}_DISPLAY')),
                      fill=self.lcd.foreground,
                      font=ImageFont.truetype(DEFAULT_FONT_NAME, 29))


class Ka50(AdvancedAircraft):
    """Ka-50 Black Shark."""
    bios_name: str = 'Ka-50'

    def __init__(self, lcd_type: LcdInfo, **kwargs) -> None:
        """
        Create Ka-50 Black Shark.

        :param lcd_type: LCD type
        """
        bios_data = {
            'PVI_LINE1_APOSTROPHE1': '',
            'PVI_LINE1_APOSTROPHE2': '',
            'PVI_LINE1_POINT': '',
            'PVI_LINE1_SIGN': '',
            'PVI_LINE1_TEXT': '',
            'PVI_LINE2_APOSTROPHE1': '',
            'PVI_LINE2_APOSTROPHE2': '',
            'PVI_LINE2_POINT': '',
            'PVI_LINE2_SIGN': '',
            'PVI_LINE2_TEXT': '',
            'AP_ALT_HOLD_LED': int(),
            'AP_BANK_HOLD_LED': int(),
            'AP_FD_LED': int(),
            'AP_HDG_HOLD_LED': int(),
            'AP_PITCH_HOLD_LED': int(),
        }
        super().__init__(lcd_type=lcd_type, bios_data=bios_data, **kwargs)

    def _draw_common_data(self, draw: ImageDraw.ImageDraw, scale: int) -> None:
        """
        Draw common part (based on scale) for Mono and Color LCD.

        :param draw: ImageDraw instance
        :param scale: scaling factor (Mono 1, Color 2)
        """
        for rect_xy in [
            (0 * scale, 1 * scale, 85 * scale, 18 * scale),
            (0 * scale, 22 * scale, 85 * scale, 39 * scale),
            (88 * scale, 1 * scale, 103 * scale, 18 * scale),
            (88 * scale, 22 * scale, 103 * scale, 39 * scale),
        ]:
            draw.rectangle(xy=rect_xy, fill=self.lcd.background, outline=self.lcd.foreground)
        line1, line2 = self._generate_pvi_lines()
        draw.text(xy=(2 * scale, 3 * scale), text=line1, fill=self.lcd.foreground, font=self.lcd.font_l)
        draw.text(xy=(2 * scale, 24 * scale), text=line2, fill=self.lcd.foreground, font=self.lcd.font_l)
        self._auto_pilot_switch(draw, scale)

    def _generate_pvi_lines(self) -> Sequence[str]:
        """
        Generate coordinate strings.

        :return: tuple of string
        """
        text1, text2 = '', ''
        if line1_text := str(self.get_bios('PVI_LINE1_TEXT')):
            l1_apostr1 = self.get_bios('PVI_LINE1_APOSTROPHE1')
            l1_apostr2 = self.get_bios('PVI_LINE1_APOSTROPHE2')
            text1 = f'{line1_text[-6:-3]}{l1_apostr1}{line1_text[-3:-1]}{l1_apostr2}{line1_text[-1]}'
        if line2_text := str(self.get_bios('PVI_LINE2_TEXT')):
            l2_apostr1 = self.get_bios('PVI_LINE2_APOSTROPHE1')
            l2_apostr2 = self.get_bios('PVI_LINE2_APOSTROPHE2')
            text2 = f'{line2_text[-6:-3]}{l2_apostr1}{line2_text[-3:-1]}{l2_apostr2}{line2_text[-1]}'
        line1 = f'{self.get_bios("PVI_LINE1_SIGN")}{text1} {self.get_bios("PVI_LINE1_POINT")}'
        line2 = f'{self.get_bios("PVI_LINE2_SIGN")}{text2} {self.get_bios("PVI_LINE2_POINT")}'
        return line1, line2

    def _auto_pilot_switch(self, draw_obj: ImageDraw.ImageDraw, scale: int) -> None:
        """
        Draw rectangle and add text for autopilot channels in correct coordinates.

        :param draw_obj: ImageDraw object form PIL
        :param scale: scaling factor (Mono 1, Color 2)
        """
        for c_rect, c_text, ap_channel, turn_on in (
                ((111 * scale, 1 * scale, 124 * scale, 18 * scale), (113 * scale, 3 * scale), 'B', self.get_bios('AP_BANK_HOLD_LED', 0)),
                ((128 * scale, 1 * scale, 141 * scale, 18 * scale), (130 * scale, 3 * scale), 'P', self.get_bios('AP_PITCH_HOLD_LED', 0)),
                ((145 * scale, 1 * scale, 158 * scale, 18 * scale), (147 * scale, 3 * scale), 'F', self.get_bios('AP_FD_LED', 0)),
                ((111 * scale, 22 * scale, 124 * scale, 39 * scale), (113 * scale, 24 * scale), 'H', self.get_bios('AP_HDG_HOLD_LED', 0)),
                ((128 * scale, 22 * scale, 141 * scale, 39 * scale), (130 * scale, 24 * scale), 'A', self.get_bios('AP_ALT_HOLD_LED', 0)),
        ):
            draw_autopilot_channels(self.lcd, ap_channel, c_rect, c_text, draw_obj, turn_on)

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for Ka-50 Black Shark for Mono LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), scale=1)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for Ka-50 Black Shark for Mono LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), scale=2)


class Ka503(Ka50):
    """Ka-50 Black Shark III."""
    bios_name: str = 'Ka-50_3'


class Mi8MT(AdvancedAircraft):
    """Mi-8MTV2 Magnificent Eight."""
    bios_name: str = 'Mi-8MT'

    def __init__(self, lcd_type: LcdInfo, **kwargs) -> None:
        """
        Create Mi-8MTV2 Magnificent Eight.

        :param lcd_type: LCD type
        """
        bios_data = {
            'LMP_AP_HDG_ON': int(),
            'LMP_AP_PITCH_ROLL_ON': int(),
            'LMP_AP_HEIGHT_ON': int(),
            'R863_CNL_SEL': int(),
            'R863_MOD': int(),
            'R863_FREQ': '',
            'R828_PRST_CHAN_SEL': int(),
            'YADRO1A_FREQ': '',
        }
        super().__init__(lcd_type=lcd_type, bios_data=bios_data, **kwargs)

    def _draw_common_data(self, draw: ImageDraw.ImageDraw, scale: int) -> None:
        """
        Draw common part (based on scale) for Mono and Color LCD.

        :param draw: ImageDraw instance
        :param scale: scaling factor (Mono 1, Color 2)
        """
        for c_rect, c_text, ap_channel, turn_on in (
                ((111 * scale, 1 * scale, 124 * scale, 18 * scale), (113 * scale, 3 * scale), 'H', self.get_bios('LMP_AP_HDG_ON', 0)),
                ((128 * scale, 1 * scale, 141 * scale, 18 * scale), (130 * scale, 3 * scale), 'P', self.get_bios('LMP_AP_PITCH_ROLL_ON', 0)),
                ((145 * scale, 1 * scale, 158 * scale, 18 * scale), (147 * scale, 3 * scale), 'A', self.get_bios('LMP_AP_HEIGHT_ON', 0)),
        ):
            draw_autopilot_channels(self.lcd, ap_channel, c_rect, c_text, draw, turn_on)

        r863, r828, yadro = self._generate_radio_values()
        for i, line in enumerate([f'R828 {r828}', f'YADRO1 {yadro}', f'R863 {r863}'], 1):
            offset = i * 10 * scale
            draw.text(xy=(0, offset), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for Mi-8MTV2 Magnificent Eight for Mono LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), scale=1)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for Mi-8MTV2 Magnificent Eight for Color LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), scale=2)

    def _generate_radio_values(self) -> Sequence[str]:
        """
        Generate string data about Hip R863, R828, YADRO1A radios settings.

        :return: All 3 radios settings as strings
        """
        r863_mod = 'FM' if int(self.get_bios('R863_MOD')) else 'AM'
        r863_freq = float(self.get_bios('R863_FREQ', 0.0))
        yadro_freq = float(self.get_bios('YADRO1A_FREQ', 0.0))
        r863 = f'Ch:{int(self.get_bios("R863_CNL_SEL")) + 1:>2} {r863_mod} {r863_freq:.3f}'
        r828 = f'Ch:{int(self.get_bios("R828_PRST_CHAN_SEL")) + 1:>2}'
        yadro = f'{yadro_freq:>7.1f}'
        return r863, r828, yadro


class Mi24P(AdvancedAircraft):
    """Mi-24P Hind."""
    bios_name: str = 'Mi-24P'

    def __init__(self, lcd_type: LcdInfo, **kwargs) -> None:
        """
        Create Mi-24P Hind.

        :param lcd_type: LCD type
        """
        bios_data = {
            'PLT_R863_CHAN': int(),
            'PLT_R863_MODUL': int(),
            'PLT_R828_CHAN': int(),
            'JADRO_FREQ': '',
            'PLT_SAU_HOVER_MODE_ON_L': int(),
            'PLT_SAU_ROUTE_MODE_ON_L': int(),
            'PLT_SAU_ALT_MODE_ON_L': int(),
            'PLT_SAU_H_ON_L': int(),
            'PLT_SAU_K_ON_L': int(),
            'PLT_SAU_T_ON_L': int(),
            'PLT_SAU_B_ON_L': int(),
        }
        super().__init__(lcd_type=lcd_type, bios_data=bios_data, **kwargs)

    def _draw_common_data(self, draw: ImageDraw.ImageDraw, scale: int) -> None:
        """
        Draw common part (based on scale) for Mono and Color LCD.

        :param draw: ImageDraw instance
        :param scale: scaling factor (Mono 1, Color 2)
        """
        for c_rect, c_text, ap_channel, turn_on in (
                ((111 * scale, 1 * scale, 124 * scale, 18 * scale), (113 * scale, 3 * scale), 'H', self.get_bios('PLT_SAU_HOVER_MODE_ON_L', 0)),
                ((128 * scale, 1 * scale, 141 * scale, 18 * scale), (130 * scale, 3 * scale), 'R', self.get_bios('PLT_SAU_ROUTE_MODE_ON_L', 0)),
                ((145 * scale, 1 * scale, 158 * scale, 18 * scale), (147 * scale, 3 * scale), 'A', self.get_bios('PLT_SAU_ALT_MODE_ON_L', 0)),
                ((94 * scale, 22 * scale, 107 * scale, 39 * scale), (96 * scale, 24 * scale), 'Y', self.get_bios('PLT_SAU_H_ON_L', 0)),
                ((111 * scale, 22 * scale, 124 * scale, 39 * scale), (113 * scale, 24 * scale), 'R', self.get_bios('PLT_SAU_K_ON_L', 0)),
                ((128 * scale, 22 * scale, 141 * scale, 39 * scale), (130 * scale, 24 * scale), 'P', self.get_bios('PLT_SAU_T_ON_L', 0)),
                ((145 * scale, 22 * scale, 158 * scale, 39 * scale), (147 * scale, 24 * scale), 'A', self.get_bios('PLT_SAU_B_ON_L', 0)),
        ):
            draw_autopilot_channels(self.lcd, ap_channel, c_rect, c_text, draw, turn_on)

        r863, r828, yadro = self._generate_radio_values()
        for i, line in enumerate([f'R828 {r828}', f'R863 {r863}', f'YADRO1 {yadro}'], 1):
            offset = i * 10 * scale
            draw.text(xy=(0, offset), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for Mi-24P Hind for Mono LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), scale=1)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for Mi-24P Hind for Color LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), scale=2)

    def _generate_radio_values(self) -> Sequence[str]:
        """
        Generate string data about Hind R863, R828, YADRO1I radios settings.

        :return: All 3 radios settings as strings
        """
        r863_mod = 'FM' if int(self.get_bios('PLT_R863_MODUL')) else 'AM'
        yadro_freq = float(self.get_bios('JADRO_FREQ', 0.0))
        r863 = f'Ch:{int(self.get_bios("PLT_R863_CHAN")) + 1:>2} {r863_mod}'
        r828 = f'Ch:{int(self.get_bios("PLT_R828_CHAN")) + 1:>2}'
        yadro = f'{yadro_freq:>7.1f}'
        return r863, r828, yadro


class ApacheEufdMode(Enum):
    """Apache EUFD Mode."""
    IDM = 1
    WCA = 2
    PRE = 4


class AH64DBLKII(AdvancedAircraft):
    """AH-64D Apache."""
    bios_name: str = 'AH-64D_BLK_II'

    def __init__(self, lcd_type: LcdInfo, **kwargs) -> None:
        """
        Create AH-64D Apache.

        :param lcd_type: LCD type
        """
        bios_data = {f'PLT_EUFD_LINE{i}': '' for i in range(1, 15)}
        super().__init__(lcd_type=lcd_type, bios_data=bios_data, **kwargs)
        self.mode = ApacheEufdMode.IDM
        self.warning_line = 1

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for AH-64D Apache for Mono LCD."""
        LOG.debug(f'Mode: {self.mode}')
        kwargs = {'draw': ImageDraw.Draw(img), 'scale': 1}
        if (mode := self.mode.name.lower()) == 'pre':
            kwargs['x_cords'] = [0] * 5 + [80] * 5
            kwargs['y_cords'] = [j * 8 for j in range(0, 5)] * 2
            kwargs['font'] = self.lcd.font_xs
            del kwargs['scale']
        getattr(self, f'_draw_for_{mode}')(**kwargs)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for AH-64D Apache for Color LCD."""
        LOG.debug(f'Mode: {self.mode}')
        kwargs = {'draw': ImageDraw.Draw(img), 'scale': 2}
        if (mode := self.mode.name.lower()) == 'pre':
            kwargs['x_cords'] = [0] * 10
            kwargs['y_cords'] = [j * 24 for j in range(0, 10)]
            kwargs['font'] = self.lcd.font_l
            del kwargs['scale']
        getattr(self, f'_draw_for_{mode}')(**kwargs)

    def _draw_for_idm(self, draw: ImageDraw.ImageDraw, scale: int) -> None:
        """
        Draw image for IDM mode.

        :param draw: ImageDraw instance
        :param scale: scaling factor (Mono 1, Color 2)
        """
        for i in range(8, 13):
            offset = (i - 8) * 8 * scale
            if mat := search(r'(.*\*)\s+(\d+)([.\dULCA]+)[\s\dA-Z]*\s+(\d+)([.\dULCA]+)[\sA-Z]+', str(self.get_bios(f'PLT_EUFD_LINE{i}'))):
                spacer = ' ' * (6 - len(mat.group(3)))
                text = f'{mat.group(1):>7}{mat.group(2):>4}{mat.group(3):5<}{spacer}{mat.group(4):>4}{mat.group(5):5<}'
                draw.text(xy=(0, offset), text=text, fill=self.lcd.foreground, font=self.lcd.font_xs)

    def _draw_for_wca(self, draw: ImageDraw.ImageDraw, scale: int) -> None:
        """
        Draw image for WCA mode.

        :param draw: ImageDraw instance
        :param scale: scaling factor (Mono 1, Color 2)
        """
        warnings = self._fetch_warning_list()
        LOG.debug(f'Warnings: {warnings}')
        try:
            for idx, warn_no in enumerate(range(self.warning_line - 1, self.warning_line + 4)):
                line = idx * 8 * scale
                draw.text(xy=(0, line), text=f'{idx + self.warning_line:2} {warnings[warn_no]}', fill=self.lcd.foreground, font=self.lcd.font_s)
                if self.warning_line >= len(warnings) - 3:
                    self.warning_line = 1
        except IndexError:
            self.warning_line = 1

    def _fetch_warning_list(self) -> List[str]:
        """
        Fetch all warnings and return as list.

        :return: list of warnings (as strings)
        """
        warn = []
        for i in range(1, 8):
            if mat := search(r'(.*)\|(.*)\|(.*)', str(self.get_bios(f'PLT_EUFD_LINE{i}'))):
                warn.extend([w for w in [mat.group(1).strip(), mat.group(2).strip(), mat.group(3).strip()] if w])
        return warn

    def _draw_for_pre(self, draw: ImageDraw.ImageDraw, x_cords: List[int], y_cords: List[int], font: ImageFont.FreeTypeFont) -> None:
        """
        Draw image for PRE mode.

        :param draw: ImageDraw instance
        :param x_cords: list of X coordinates
        :param y_cords: list of Y coordinates
        :param font: font instance
        """
        match_dict = {
            2: r'.*\|.*\|([\u2192\s][A-Z]*\s\d)\s*([\d\.]*)',
            3: r'.*\|.*\|([\u2192\s][A-Z]*\s\d)\s*([\d\.]*)',
            4: r'.*\|.*\|([\u2192\s][A-Z]*\s\d)\s*([\d\.]*)',
            5: r'.*\|.*\|([\u2192\s][A-Z]*\s\d)\s*([\d\.]*)',
            6: r'.*\|.*\|([\u2192\s][A-Z]*\s\d)\s*([\d\.]*)',
            7: r'.*\|.*\|([\u2192\s][A-Z]*\s\d)\s*([\d\.]*)',
            8: r'\s*\|([\u2192\s][A-Z]*\s*\d*)\s*([\d\.]*)',
            9: r'\s*\|([\u2192\s][A-Z]*\s*\d*)\s*([\d\.]*)',
            10: r'\s*\|([\u2192\s][A-Z]*\s*\d*)\s*([\d\.]*)',
            11: r'\s*\|([\u2192\s][A-Z]*\s*\d*)\s*([\d\.]*)',
        }
        for i, x_cord, y_cord in zip(range(2, 12), x_cords, y_cords):
            if mat := search(match_dict[i], str(self.get_bios(f'PLT_EUFD_LINE{i}'))):
                draw.text(xy=(x_cord, y_cord), text=f'{mat.group(1):<9}{mat.group(2):>7}',
                          fill=self.lcd.foreground, font=font)

    def set_bios(self, selector: str, value: Union[str, int]) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        """
        if selector == 'PLT_EUFD_LINE1':
            self.mode = ApacheEufdMode.IDM
            if search(r'.*\|.*\|(PRESET TUNE)\s\w+', str(value)):
                self.mode = ApacheEufdMode.PRE
        if selector in ('PLT_EUFD_LINE8', 'PLT_EUFD_LINE9', 'PLT_EUFD_LINE10', 'PLT_EUFD_LINE11', 'PLT_EUFD_LINE12'):
            LOG.debug(f'{type(self).__name__} {selector} original: "{value}"')
            value = str(value).replace(']', '\u2666').replace('[', '\u25ca').replace('~', '\u25a0'). \
                replace('>', '\u25b8').replace('<', '\u25c2').replace('=', '\u2219')
        if 'PLT_EUFD_LINE' in selector:
            LOG.debug(f'{type(self).__name__} {selector} original: "{value}"')
            value = str(value).replace('!', '\u2192')  # replace ! with ->
        super().set_bios(selector, value)

    def button_request(self, button: Union[LcdButton, Gkey]) -> RequestModel:
        """
        Prepare AH-64D Apache specific DCS-BIOS request for button pressed.

        For G13/G15/G510: 1-4
        For G19 9-15: LEFT = 9, RIGHT = 10, OK = 11, CANCEL = 12, UP = 13, DOWN = 14, MENU = 15
        Or any G-Key 1 to 29

        :param button: LcdButton Enum
        :return: ready to send DCS-BIOS request
        """
        wca_or_idm = f'PLT_EUFD_WCA {RequestType.CUSTOM.value} PLT_EUFD_WCA 0|PLT_EUFD_WCA 1|'
        if self.mode == ApacheEufdMode.IDM:
            wca_or_idm = f'PLT_EUFD_IDM {RequestType.CUSTOM.value} PLT_EUFD_IDM 0|PLT_EUFD_IDM 1|'

        if button in (LcdButton.FOUR, LcdButton.UP) and self.mode == ApacheEufdMode.IDM:
            self.mode = ApacheEufdMode.WCA
        elif button in (LcdButton.FOUR, LcdButton.UP) and self.mode != ApacheEufdMode.IDM:
            self.mode = ApacheEufdMode.IDM

        if button in (LcdButton.ONE, LcdButton.LEFT) and self.mode == ApacheEufdMode.WCA:
            self.warning_line += 1

        self.key_req.set_request(LcdButton.ONE, wca_or_idm)
        self.key_req.set_request(LcdButton.LEFT, wca_or_idm)
        return super().button_request(button)


class A10C(AdvancedAircraft):
    """A-10C Warthog."""
    bios_name: str = 'A-10C'

    def __init__(self, lcd_type: LcdInfo, **kwargs) -> None:
        """
        Create A-10C Warthog or A-10C II Tank Killer.

        :param lcd_type: LCD type
        """
        bios_data = {
            'VHFAM_FREQ1': int(),
            'VHFAM_FREQ2': int(),
            'VHFAM_FREQ3': int(),
            'VHFAM_FREQ4': int(),
            'VHFAM_PRESET': int(),
            'VHFFM_FREQ1': int(),
            'VHFFM_FREQ2': int(),
            'VHFFM_FREQ3': int(),
            'VHFFM_FREQ4': int(),
            'VHFFM_PRESET': int(),
            'UHF_100MHZ_SEL': int(),
            'UHF_10MHZ_SEL': int(),
            'UHF_1MHZ_SEL': int(),
            'UHF_POINT1MHZ_SEL': int(),
            'UHF_POINT25_SEL': int(),
            'UHF_PRESET': '',
            'ARC210_FREQUENCY': '',
            'ARC210_PREV_MANUAL_FREQ': '',
        }
        super().__init__(lcd_type=lcd_type, bios_data=bios_data, **kwargs)

    def _generate_vhf(self, modulation: str) -> str:
        """
        Generate frequency for VHF AM, VHF FM radio.

        :param modulation: 'AM' or 'FM'
        :return: frequency settings as strings
        """
        freq_2 = self.get_bios(f'VHF{modulation}_FREQ2')
        freq_3 = self.get_bios(f'VHF{modulation}_FREQ3')
        freq_1 = int(self.get_bios(f'VHF{modulation}_FREQ1', 0)) + 3
        freq_4 = int(self.get_bios(f'VHF{modulation}_FREQ4', 0)) * 25
        preset = int(self.get_bios(f'VHF{modulation}_PRESET', 0)) + 1
        return f'{freq_1:2}{freq_2}.{freq_3}{freq_4:02} ({preset:2})'

    def _generate_uhf(self) -> str:
        """
        Generate frequency for UHF radio.

        :return: frequency settings as strings
        """
        uhf_10 = self.get_bios('UHF_10MHZ_SEL')
        uhf_1 = self.get_bios('UHF_1MHZ_SEL')
        uhf_01 = self.get_bios('UHF_POINT1MHZ_SEL')
        uhf_preset = self.get_bios('UHF_PRESET')
        uhf_100 = int(self.get_bios('UHF_100MHZ_SEL', 0)) + 2
        uhf_100 = 'A' if uhf_100 == 4 else uhf_100  # type: ignore
        uhf_25 = int(self.get_bios('UHF_POINT25_SEL', 0)) * 25
        return f'{uhf_100}{uhf_10}{uhf_1}.{uhf_01}{uhf_25:02} ({uhf_preset})'

    def _generate_arc(self) -> str:
        """
        Generate frequency for ARC AM radio.

        :return: frequency settings as strings
        """
        return f'{self.get_bios("ARC210_FREQUENCY")} ({str(self.get_bios("ARC210_PREV_MANUAL_FREQ")).strip():>7})'

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for A-10C Warthog for Mono LCD."""
        draw = ImageDraw.Draw(img)
        uhf = self._generate_uhf()
        vhf_am = self._generate_vhf('AM')
        vhf_fm = self._generate_vhf('FM')
        for i, line in enumerate(['      *** RADIOS ***', f' AM: {vhf_am}', f'UHF: {uhf}', f' FM: {vhf_fm}']):
            offset = i * 10
            draw.text(xy=(0, offset), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for A-10C Warthog for Color LCD."""
        draw = ImageDraw.Draw(img)
        uhf = self._generate_uhf()
        vhf_am = self._generate_vhf('AM')
        vhf_fm = self._generate_vhf('FM')
        for i, line in enumerate(['      *** RADIOS ***', f' AM: {vhf_am}', f'UHF: {uhf}', f' FM: {vhf_fm}']):
            offset = i * 20
            draw.text(xy=(0, offset), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)


class A10C2(A10C):
    """A-10C II Tank Killer."""
    bios_name: str = 'A-10C_2'

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for A-10C II Tank Killer for Mono LCD."""
        draw = ImageDraw.Draw(img)
        uhf = self._generate_uhf()
        vhf_fm = self._generate_vhf('FM')
        arc = self._generate_arc()
        for i, line in enumerate(['      *** RADIOS ***', f' AM: {arc}', f'UHF: {uhf}', f' FM: {vhf_fm}']):
            offset = i * 10
            draw.text(xy=(0, offset), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for A-10C II Tank Killer for Color LCD."""
        draw = ImageDraw.Draw(img)
        uhf = self._generate_uhf()
        vhf_fm = self._generate_vhf('FM')
        arc = self._generate_arc()
        for i, line in enumerate(['      *** RADIOS ***', f' AM: {arc}', f'UHF: {uhf}', f' FM: {vhf_fm}']):
            offset = i * 20
            draw.text(xy=(0, offset), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)


class F14B(AdvancedAircraft):
    """F-14B Tomcat."""
    bios_name: str = 'F-14B'

    def _draw_common_data(self, draw: ImageDraw.ImageDraw) -> None:
        """
        Draw common part for Mono and Color LCD.

        :param draw: ImageDraw instance
        """
        draw.text(xy=(2, 3), text=f'{self.bios_name}', fill=self.lcd.foreground, font=self.lcd.font_l)

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for F-14B Tomcat for Mono LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img))

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for F-14B Tomcat for Color LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img))


class F14A135GR(F14B):
    """F-14A-135-GR Tomcat."""
    bios_name: str = 'F-14A-135-GR'


class AV8BNA(AdvancedAircraft):
    """AV-8B Night Attack."""
    bios_name: str = 'AV8BNA'

    def __init__(self, lcd_type: LcdInfo, **kwargs) -> None:
        """
        Create AV-8B Night Attack.

        :param lcd_type: LCD type
        """
        bios_data = {
            'UFC_SCRATCHPAD': '',
            'UFC_COMM1_DISPLAY': '',
            'UFC_COMM2_DISPLAY': '',
            'AV8BNA_ODU_1_SELECT': '',
            'AV8BNA_ODU_1_TEXT': '',
            'AV8BNA_ODU_2_SELECT': '',
            'AV8BNA_ODU_2_TEXT': '',
            'AV8BNA_ODU_3_SELECT': '',
            'AV8BNA_ODU_3_TEXT': '',
            'AV8BNA_ODU_4_SELECT': '',
            'AV8BNA_ODU_4_TEXT': '',
            'AV8BNA_ODU_5_SELECT': '',
            'AV8BNA_ODU_5_TEXT': '',
        }
        super().__init__(lcd_type=lcd_type, bios_data=bios_data, **kwargs)

    def _draw_common_data(self, draw: ImageDraw.ImageDraw, scale: int) -> ImageDraw.ImageDraw:
        """
        Draw common part (based on scale) for Mono and Color LCD.

        :param draw: ImageDraw instance
        :param scale: scaling factor (Mono 1, Color 2)
        :return: updated image to draw
        """
        draw.text(xy=(50 * scale, 0), fill=self.lcd.foreground, font=self.lcd.font_l, text=f'{self.get_bios("UFC_SCRATCHPAD")}')
        draw.line(xy=(50 * scale, 20 * scale, 160 * scale, 20 * scale), fill=self.lcd.foreground, width=1)

        draw.rectangle(xy=(50 * scale, 29 * scale, 70 * scale, 42 * scale), fill=self.lcd.background, outline=self.lcd.foreground)
        draw.text(xy=(52 * scale, 29 * scale), text=str(self.get_bios('UFC_COMM1_DISPLAY')), fill=self.lcd.foreground, font=self.lcd.font_l)

        draw.rectangle(xy=(139 * scale, 29 * scale, 159 * scale, 42 * scale), fill=self.lcd.background, outline=self.lcd.foreground)
        draw.text(xy=(140 * scale, 29 * scale), text=str(self.get_bios('UFC_COMM2_DISPLAY')), fill=self.lcd.foreground, font=self.lcd.font_l)

        for i in range(1, 6):
            offset = (i - 1) * 8 * scale
            draw.text(xy=(0 * scale, offset), fill=self.lcd.foreground, font=self.lcd.font_s,
                      text=f'{i}{self.get_bios(f"AV8BNA_ODU_{i}_SELECT")}{self.get_bios(f"AV8BNA_ODU_{i}_TEXT")}')
        return draw

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for AV-8B N/A for Mono LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), scale=1)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for AV-8B N/A for Color LCD."""
        self._draw_common_data(draw=ImageDraw.Draw(img), scale=2)


def draw_autopilot_channels(lcd: LcdInfo,
                            ap_channel: str,
                            c_rect: Tuple[float, float, float, float],
                            c_text: Tuple[float, float],
                            draw_obj: ImageDraw.ImageDraw,
                            turn_on: Union[str, int, float]) -> None:
    """
    Draw rectangles with a background for autopilot channels.

    :param lcd: instance of LCD
    :param ap_channel: channel name
    :param c_rect: coordinates for rectangle
    :param c_text: coordinates for a name
    :param draw_obj: ImageDraw instance
    :param turn_on: channel on/off, fill on/off
    """
    if turn_on:
        draw_obj.rectangle(c_rect, fill=lcd.foreground, outline=lcd.foreground)
        draw_obj.text(xy=c_text, text=ap_channel, fill=lcd.background, font=lcd.font_l)
    else:
        draw_obj.rectangle(xy=c_rect, fill=lcd.background, outline=lcd.foreground)
        draw_obj.text(xy=c_text, text=ap_channel, fill=lcd.foreground, font=lcd.font_l)
