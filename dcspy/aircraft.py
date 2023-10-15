from enum import Enum
from itertools import chain, cycle
from logging import getLogger
from pathlib import Path
from pprint import pformat
from re import search, sub
from string import whitespace
from tempfile import gettempdir
from typing import Dict, List, Sequence, Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from dcspy import default_yaml, load_yaml
from dcspy.models import CycleButton, Gkey, LcdButton, LcdInfo, LcdType
from dcspy.sdk import lcd_sdk

LOG = getLogger(__name__)


class MetaAircraft(type):
    """Meta class for all BasicAircraft."""
    def __new__(mcs, name, bases, namespace):
        """
        Create new instance of any plane as BasicAircraft.

        You can crate instance of any plane:
        f22a = MetaAircraft('F-22A', (BasicAircraft,), {})(lcd_type: LcdInfo)

        :param name:
        :param bases:
        :param namespace:
        """
        return super().__new__(mcs, name, bases, namespace)

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
        self.cycle_buttons: Dict[Union[LcdButton, Gkey], CycleButton] = {}
        self.button_actions: Dict[Union[LcdButton, Gkey], str] = {}
        self._load_plane_yaml()

    def _load_plane_yaml(self) -> None:
        """Load plane's YAML file with configuration and apply."""
        bios_data, cycle_buttons, button_actions = {}, {}, {}
        plane_yaml = load_yaml(full_path=default_yaml.parent / f'{self.bios_name}.yaml')
        for gkey_str, request in plane_yaml.items():
            if request:
                gkey = Gkey.from_yaml(gkey_str)
                if 'CYCLE' in request:
                    selector = request.split(' ')[0]
                    bios_data[selector] = ''  # int or str maybe set as None
                    cycle_buttons[gkey] = CycleButton(ctrl_name=selector)
                else:
                    button_actions[gkey] = f'{request}\n'

        self.bios_data.update(bios_data)
        self.cycle_buttons.update(cycle_buttons)
        self.button_actions.update(button_actions)

    def button_request(self, button: Union[LcdButton, Gkey]) -> str:
        """
        Prepare aircraft specific DCS-BIOS request for button pressed.

        For G13/G15/G510: 1-4
        For G19 9-15: LEFT = 9, RIGHT = 10, OK = 11, CANCEL = 12, UP = 13, DOWN = 14, MENU = 15
        Or any G-Key 1 to 29

        :param button: LcdButton or Gkey
        :return: ready to send DCS-BIOS request
        """
        LOG.debug(f'{type(self).__name__} Button: {button}')
        if button in self.cycle_buttons:
            self.button_actions[button] = self._get_cycle_request(button)
        request = self.button_actions.get(button, '\n')
        LOG.debug(f'Request: {request.replace(whitespace[2], " ")}')
        return request

    def set_bios(self, selector: str, value: Union[str, int]) -> None:
        """
        Set value for DCS-BIOS selector.

        :param selector:
        :param value:
        """
        self.bios_data[selector]['value'] = value
        LOG.debug(f'{type(self).__name__} {selector} value: "{value}"')

    def get_bios(self, selector: str) -> Union[str, int]:
        """
        Get value for DCS-BIOS selector.

        :param selector:
        """
        try:
            return self.bios_data[selector]['value']
        except KeyError:
            return ''

    def _get_next_value_for_button(self, button: Union[LcdButton, Gkey]) -> int:
        """
        Get next int value (cycle fore and back) for button name.

        :param button: LcdButton Enum
        """
        if not isinstance(self.cycle_buttons[button].iter, cycle):
            bios = self.cycle_buttons[button].ctrl_name
            curr_val = int(self.get_bios(bios))
            max_val = self.bios_data[bios]['max_value']
            step = 1
            range_inc = list(range(0, max_val + step, step))
            range_dec = list(range(max_val - step, 0, -step))
            full_seed = range_inc + range_dec + range_inc
            seed = full_seed[curr_val//step + 1:2 * (len(range_inc) - 1) + curr_val//step + 1]
            LOG.debug(f'{type(self).__name__} {bios} full_seed: {full_seed} seed: {seed} curr_val: {curr_val}')
            self.cycle_buttons[button].iter = cycle(chain(seed))
        return next(self.cycle_buttons[button].iter)

    def _get_cycle_request(self, button: Union[LcdButton, Gkey]) -> str:
        """
        Get request for cycle button.

        :param button: LcdButton Enum
        :return: ready to send DCS-BIOS request
        """
        button_bios_name = self.cycle_buttons[button].ctrl_name
        settings = self._get_next_value_for_button(button)
        return f'{button_bios_name} {settings}\n'

    def __repr__(self) -> str:
        return f'{super().__repr__()} with: {pformat(self.__dict__)}'


class AdvancedAircraft(BasicAircraft):
    """Advanced Aircraft."""
    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create advanced aircraft.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type=lcd_type)
        self._debug_img = cycle(chain([f'{x:02}' for x in range(10)], range(10, 99)))

    def button_request(self, button: Union[LcdButton, Gkey]) -> str:
        """
        Prepare aircraft specific DCS-BIOS request for button pressed.

        For G13/G15/G510: 1-4
        For G19 9-15: LEFT = 9, RIGHT = 10, OK = 11, CANCEL = 12, UP = 13, DOWN = 14, MENU = 15
        Or any G-Key 1 to 29

        :param button: LcdButton or Gkey
        :return: ready to send DCS-BIOS request
        """
        LOG.debug(f'{type(self).__name__} Button: {button}')
        if button in self.cycle_buttons:
            self.button_actions[button] = self._get_cycle_request(button)
        request = self.button_actions.get(button, '\n')
        LOG.debug(f'Request: {request.replace(whitespace[2], " ")}')
        return request

    def set_bios(self, selector: str, value: Union[str, int]) -> None:
        """
        Set value for DCS-BIOS selector and update LCD with image.

        :param selector:
        :param value:
        """
        super().set_bios(selector=selector, value=value)
        lcd_sdk.update_display(self.prepare_image())

    def prepare_image(self) -> Image.Image:
        """
        Prepare image to be sent to correct type of LCD.

        :return: image instance ready display on LCD
        """
        img = Image.new(mode=self.lcd.mode.value, size=(self.lcd.width, self.lcd.height), color=self.lcd.background)
        getattr(self, f'draw_for_lcd_{self.lcd.type.name.lower()}')(img)
        if self.cfg.get('save_lcd', False):
            img.save(Path(gettempdir()) / f'{type(self).__name__}_{next(self._debug_img)}.png', 'PNG')
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

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create F/A-18C Hornet.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, Union[str, int]] = {
            'UFC_SCRATCHPAD_STRING_1_DISPLAY': '',
            'UFC_SCRATCHPAD_STRING_2_DISPLAY': '',
            'UFC_SCRATCHPAD_NUMBER_DISPLAY':  '',
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
        self.cycle_buttons = {
            LcdButton.OK: CycleButton(ctrl_name='HUD_ATT_SW'),
            LcdButton.MENU: CycleButton(ctrl_name='IFEI_DWN_BTN'),
            LcdButton.CANCEL: CycleButton(ctrl_name='IFEI_UP_BTN'),
        }
        self.button_actions = {
            LcdButton.ONE: 'UFC_COMM1_CHANNEL_SELECT DEC\n',
            LcdButton.TWO: 'UFC_COMM1_CHANNEL_SELECT INC\n',
            LcdButton.THREE: 'UFC_COMM2_CHANNEL_SELECT DEC\n',
            LcdButton.FOUR: 'UFC_COMM2_CHANNEL_SELECT INC\n',
            LcdButton.LEFT: 'UFC_COMM1_CHANNEL_SELECT DEC\n',
            LcdButton.RIGHT: 'UFC_COMM1_CHANNEL_SELECT INC\n',
            LcdButton.DOWN: 'UFC_COMM2_CHANNEL_SELECT DEC\n',
            LcdButton.UP: 'UFC_COMM2_CHANNEL_SELECT INC\n',
            Gkey(1, 1): 'UFC_COMM1_CHANNEL_SELECT DEC\n',
            Gkey(8, 1): 'UFC_COMM1_CHANNEL_SELECT INC\n',
            Gkey(2, 1): 'UFC_COMM2_CHANNEL_SELECT DEC\n',
            Gkey(9, 1): 'UFC_COMM2_CHANNEL_SELECT INC\n',
        }

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

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create F-16C Viper.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.font = self.lcd.font_s
        self.ded_font = self.cfg.get('f16_ded_font', True)
        if self.ded_font and self.lcd.type == LcdType.COLOR:
            self.font = ImageFont.truetype(str((Path(__file__) / '..' / 'resources' / 'falconded.ttf').resolve()), 25)
        self.bios_data: Dict[str, Union[str, int]] = {
            'DED_LINE_1': '',
            'DED_LINE_2': '',
            'DED_LINE_3': '',
            'DED_LINE_4': '',
            'DED_LINE_5': '',
            'IFF_MASTER_KNB':  int(),
            'IFF_ENABLE_SW': int(),
            'IFF_M4_CODE_SW': int(),
            'IFF_M4_REPLY_SW': int(),
        }
        self.cycle_buttons = {
            LcdButton.ONE: CycleButton(ctrl_name='IFF_MASTER_KNB'),
            LcdButton.TWO: CycleButton(ctrl_name='IFF_ENABLE_SW'),
            LcdButton.THREE: CycleButton(ctrl_name='IFF_M4_CODE_SW'),
            LcdButton.FOUR: CycleButton(ctrl_name='IFF_M4_REPLY_SW'),
            LcdButton.LEFT: CycleButton(ctrl_name='IFF_MASTER_KNB'),
            LcdButton.RIGHT: CycleButton(ctrl_name='IFF_ENABLE_SW'),
            LcdButton.DOWN: CycleButton(ctrl_name='IFF_M4_CODE_SW'),
            LcdButton.UP: CycleButton(ctrl_name='IFF_M4_REPLY_SW'),
        }

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
            for character in ['A\x10\x04', '\x82', '\x03', '\x02', '\x80', '\x08', '\x10', '\x07', '\x0f', '\xfe', '\xfc', '\x03', '\xff', '\xc0']:
                value = value.replace(character, '')  # List page
            if value and value[-1] == '@':
                value = value.replace('@', '')  # List - 6
            if self.lcd.type == LcdType.MONO:
                value = value.replace('o', '\u00b0')  # 'o' to degree sign
                value = value.replace('a', '\u2666')  # 'a' to up-down arrow 2195 or black diamond 2666
                value = value.replace('*', '\u25d9')  # INVERSE WHITE CIRCLE
            elif self.ded_font and self.lcd.type == LcdType.COLOR:
                value = value.replace('o', '\u005e')  # replace 'o' to degree sign
                value = value.replace('a', '\u0040')  # fix up-down triangle arrow
                value = value.replace('*', '\u00d7')  # fix to inverse star
                value = sub(r'1DEST\s2BNGO\s3VIP\s{2}RINTG', '\u00c1DEST \u00c2BNGO \u00c3VIP  \u0072INTG', value)
                value = sub(r'4NAV\s{2}5MAN\s{2}6INS\s{2}EDLNK', '\u00c4NAV  \u00c5MAN  \u00c6INS  \u0065DLNK', value)
                value = sub(r'7CMDS\s8MODE\s9VRP\s{2}0MISC', '\u00c7CMDS \u00c8MODE \u00c9VRP  \u00c0MISC', value)
                value = sub(r'1CORR\s2MAGV\s3OFP\s{2}RHMCS', '\u00c1CORR \u00c2MAGV \u00c3OFP  \u0072HMCS', value)
                value = sub(r'4INSM\s5LASR\s6GPS\s{2}E', '\u00c4INSM \u00c5LASR \u00c6GPS  \u0065', value)
                value = sub(r'7DRNG\s8BULL\s9\s{5}0', '\u00c7DRNG \u00c8BULL \u00c9     \u00c0', value)
                value = sub(r'(M1\s:\d+\s+)M4(\s+\(\d\).*)', r'\1mÄ\2', value)
                value = sub(r'M1(\s:\d+\s+)M4(\s+:\s+\(\d\).*)', r'mÁ\1mÄ\2', value)
                value = sub(r'M3(\s+:\d+\s+×\s+\d×[A-Z]+\(\d\).*)', r'mÃ\1', value)
                value = sub(r'(\s[\s|×])HUD BLNK([×|\s]\s+)', r'\1hud blnk\2', value)
                value = sub(r'(\s[\s|×])CKPT BLNK([×|\s]\s+)', r'\1ckpt blnk\2', value)
        super().set_bios(selector, value)


class F15ESE(AdvancedAircraft):
    """F-15ESE Eagle."""
    bios_name: str = 'F-15ESE'

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create F-15ESE Egle.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, Union[str, int]] = {
            'F_UFC_LINE1_DISPLAY': '',
            'F_UFC_LINE2_DISPLAY': '',
            'F_UFC_LINE3_DISPLAY': '',
            'F_UFC_LINE4_DISPLAY': '',
            'F_UFC_LINE5_DISPLAY': '',
            'F_UFC_LINE6_DISPLAY': '',
        }
        self.button_actions = {
            LcdButton.ONE: 'F_UFC_PRE_CHAN_L_SEL -3200\n',
            LcdButton.TWO: 'F_UFC_PRE_CHAN_L_SEL 3200\n',
            LcdButton.THREE: 'F_UFC_PRE_CHAN_R_SEL -3200\n',
            LcdButton.FOUR: 'F_UFC_PRE_CHAN_R_SEL 3200\n',
            LcdButton.LEFT: 'F_UFC_PRE_CHAN_L_SEL -3200\n',
            LcdButton.RIGHT: 'F_UFC_PRE_CHAN_L_SEL 3200\n',
            LcdButton.DOWN: 'F_UFC_PRE_CHAN_R_SEL -3200\n',
            LcdButton.UP: 'F_UFC_PRE_CHAN_R_SEL 3200\n',
            LcdButton.MENU: 'F_UFC_KEY_L_GUARD 1\n|F_UFC_KEY_L_GUARD 0\n',
            LcdButton.CANCEL: 'F_UFC_KEY_R_GUARD 1\n|F_UFC_KEY_R_GUARD 0\n',
        }

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for F-15ESE Eagle for Mono LCD."""
        draw = ImageDraw.Draw(img)
        for i in range(1, 6):
            offset = (i - 1) * 8
            draw.text(xy=(0, offset), text=str(self.get_bios(f'F_UFC_LINE{i}_DISPLAY')), fill=self.lcd.foreground, font=self.lcd.font_s)
        mat = search(r'\s*([0-9G]{1,2})\s+([0-9GV]{1,2})\s+', str(self.get_bios('F_UFC_LINE6_DISPLAY')))
        if mat:
            uhf, v_uhf = mat.groups()
            draw.text(xy=(130, 30), text=f'{uhf:>2} {v_uhf:>2}', fill=self.lcd.foreground, font=self.lcd.font_s)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for F-15ESE Eagle for Color LCD."""
        draw = ImageDraw.Draw(img)
        for i in range(1, 7):
            offset = (i - 1) * 24
            # todo: fix custom font for Color LCD
            draw.text(xy=(0, offset), text=str(self.get_bios(f'F_UFC_LINE{i}_DISPLAY')), fill=self.lcd.foreground, font=ImageFont.truetype('consola.ttf', 29))


class Ka50(AdvancedAircraft):
    """Ka-50 Black Shark."""
    bios_name: str = 'Ka-50'

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create Ka-50 Black Shark.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, Union[str, int]] = {
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
        self.button_actions = {
            LcdButton.ONE: 'PVI_WAYPOINTS_BTN 1\n|PVI_WAYPOINTS_BTN 0\n',
            LcdButton.TWO: 'PVI_FIXPOINTS_BTN 1\n|PVI_FIXPOINTS_BTN 0\n',
            LcdButton.THREE: 'PVI_AIRFIELDS_BTN 1\n|PVI_AIRFIELDS_BTN 0\n',
            LcdButton.FOUR: 'PVI_TARGETS_BTN 1\n|PVI_TARGETS_BTN 0\n',
            LcdButton.LEFT: 'PVI_WAYPOINTS_BTN 1\n|PVI_WAYPOINTS_BTN 0\n',
            LcdButton.RIGHT: 'PVI_FIXPOINTS_BTN 1\n|PVI_FIXPOINTS_BTN 0\n',
            LcdButton.DOWN: 'PVI_AIRFIELDS_BTN 1\n|PVI_AIRFIELDS_BTN 0\n',
            LcdButton.UP: 'PVI_TARGETS_BTN 1\n|PVI_TARGETS_BTN 0\n',
        }

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
        line1_text = str(self.get_bios('PVI_LINE1_TEXT'))
        line2_text = str(self.get_bios('PVI_LINE2_TEXT'))
        if line1_text:
            l1_apostr1 = self.get_bios('PVI_LINE1_APOSTROPHE1')
            l1_apostr2 = self.get_bios('PVI_LINE1_APOSTROPHE2')
            text1 = f'{line1_text[-6:-3]}{l1_apostr1}{line1_text[-3:-1]}{l1_apostr2}{line1_text[-1]}'
        if line2_text:
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
                ((111 * scale, 1 * scale, 124 * scale, 18 * scale), (113 * scale, 3 * scale), 'B', self.get_bios('AP_BANK_HOLD_LED')),
                ((128 * scale, 1 * scale, 141 * scale, 18 * scale), (130 * scale, 3 * scale), 'P', self.get_bios('AP_PITCH_HOLD_LED')),
                ((145 * scale, 1 * scale, 158 * scale, 18 * scale), (147 * scale, 3 * scale), 'F', self.get_bios('AP_FD_LED')),
                ((111 * scale, 22 * scale, 124 * scale, 39 * scale), (113 * scale, 24 * scale), 'H', self.get_bios('AP_HDG_HOLD_LED')),
                ((128 * scale, 22 * scale, 141 * scale, 39 * scale), (130 * scale, 24 * scale), 'A', self.get_bios('AP_ALT_HOLD_LED')),
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

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create Mi-8MTV2 Magnificent Eight.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, Union[str, int]] = {
            'LMP_AP_HDG_ON': int(),
            'LMP_AP_PITCH_ROLL_ON': int(),
            'LMP_AP_HEIGHT_ON': int(),
            'R863_CNL_SEL': int(),
            'R863_MOD': int(),
            'R863_FREQ': '',
            'R828_PRST_CHAN_SEL': int(),
            'YADRO1A_FREQ': '',
        }

    def _draw_common_data(self, draw: ImageDraw.ImageDraw, scale: int) -> None:
        """
        Draw common part (based on scale) for Mono and Color LCD.

        :param draw: ImageDraw instance
        :param scale: scaling factor (Mono 1, Color 2)
        """
        for c_rect, c_text, ap_channel, turn_on in (
                ((111 * scale, 1 * scale, 124 * scale, 18 * scale), (113 * scale, 3 * scale), 'H', self.get_bios('LMP_AP_HDG_ON')),
                ((128 * scale, 1 * scale, 141 * scale, 18 * scale), (130 * scale, 3 * scale), 'P', self.get_bios('LMP_AP_PITCH_ROLL_ON')),
                ((145 * scale, 1 * scale, 158 * scale, 18 * scale), (147 * scale, 3 * scale), 'A', self.get_bios('LMP_AP_HEIGHT_ON')),
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
        try:
            r863_freq = float(self.get_bios('R863_FREQ'))
        except ValueError:
            r863_freq = 0.0
        try:
            yadro_freq = float(self.get_bios('YADRO1A_FREQ'))
        except ValueError:
            yadro_freq = 0.0
        r863 = f'Ch:{int(self.get_bios("R863_CNL_SEL")) + 1:>2} {r863_mod} {r863_freq:.3f}'
        r828 = f'Ch:{int(self.get_bios("R828_PRST_CHAN_SEL")) + 1:>2}'
        yadro = f'{yadro_freq:>7.1f}'
        return r863, r828, yadro


class Mi24P(AdvancedAircraft):
    """Mi-24P Hind."""
    bios_name: str = 'Mi-24P'

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create Mi-24P Hind.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, Union[str, int]] = {
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

    def _draw_common_data(self, draw: ImageDraw.ImageDraw, scale: int) -> None:
        """
        Draw common part (based on scale) for Mono and Color LCD.

        :param draw: ImageDraw instance
        :param scale: scaling factor (Mono 1, Color 2)
        """
        for c_rect, c_text, ap_channel, turn_on in (
                ((111 * scale, 1 * scale, 124 * scale, 18 * scale), (113 * scale, 3 * scale), 'H', self.get_bios('PLT_SAU_HOVER_MODE_ON_L')),
                ((128 * scale, 1 * scale, 141 * scale, 18 * scale), (130 * scale, 3 * scale), 'R', self.get_bios('PLT_SAU_ROUTE_MODE_ON_L')),
                ((145 * scale, 1 * scale, 158 * scale, 18 * scale), (147 * scale, 3 * scale), 'A', self.get_bios('PLT_SAU_ALT_MODE_ON_L')),
                ((94 * scale, 22 * scale, 107 * scale, 39 * scale), (96 * scale, 24 * scale), 'Y', self.get_bios('PLT_SAU_H_ON_L')),
                ((111 * scale, 22 * scale, 124 * scale, 39 * scale), (113 * scale, 24 * scale), 'R', self.get_bios('PLT_SAU_K_ON_L')),
                ((128 * scale, 22 * scale, 141 * scale, 39 * scale), (130 * scale, 24 * scale), 'P', self.get_bios('PLT_SAU_T_ON_L')),
                ((145 * scale, 22 * scale, 158 * scale, 39 * scale), (147 * scale, 24 * scale), 'A', self.get_bios('PLT_SAU_B_ON_L')),
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
        try:
            yadro_freq = float(self.get_bios('JADRO_FREQ'))
        except ValueError:
            yadro_freq = 0.0
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

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create AH-64D Apache.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.mode = ApacheEufdMode.IDM
        self.warning_line = 1
        self.bios_data: Dict[str, Union[str, int]] = {
            'PLT_EUFD_LINE1': '',
            'PLT_EUFD_LINE2': '',
            'PLT_EUFD_LINE3': '',
            'PLT_EUFD_LINE4': '',
            'PLT_EUFD_LINE5': '',
            'PLT_EUFD_LINE6': '',
            'PLT_EUFD_LINE7': '',
            'PLT_EUFD_LINE8': '',
            'PLT_EUFD_LINE9': '',
            'PLT_EUFD_LINE10': '',
            'PLT_EUFD_LINE11': '',
            'PLT_EUFD_LINE12': '',
        }
        self.button_actions = {
            LcdButton.TWO: 'PLT_EUFD_RTS 0\n|PLT_EUFD_RTS 1\n',
            LcdButton.THREE: 'PLT_EUFD_PRESET 0\n|PLT_EUFD_PRESET 1\n',
            LcdButton.FOUR: 'PLT_EUFD_ENT 0\n|PLT_EUFD_ENT 1\n',
            LcdButton.RIGHT: 'PLT_EUFD_RTS 0\n|PLT_EUFD_RTS 1\n',
            LcdButton.DOWN: 'PLT_EUFD_PRESET 0\n|PLT_EUFD_PRESET 1\n',
            LcdButton.UP: 'PLT_EUFD_ENT 0\n|PLT_EUFD_ENT 1\n',
        }

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for AH-64D Apache for Mono LCD."""
        LOG.debug(f'Mode: {self.mode}')
        kwargs = {'draw': ImageDraw.Draw(img), 'scale': 1}
        mode = self.mode.name.lower()
        if mode == 'pre':
            kwargs['xcords'] = [0] * 5 + [80] * 5
            kwargs['ycords'] = [j * 8 for j in range(0, 5)] * 2
            kwargs['font'] = self.lcd.font_xs
            del kwargs['scale']
        getattr(self, f'_draw_for_{mode}')(**kwargs)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for AH-64D Apache for Color LCD."""
        LOG.debug(f'Mode: {self.mode}')
        kwargs = {'draw': ImageDraw.Draw(img), 'scale': 2}
        mode = self.mode.name.lower()
        if mode == 'pre':
            kwargs['xcords'] = [0] * 10
            kwargs['ycords'] = [j * 24 for j in range(0, 10)]
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
            mat = search(r'(.*\*)\s+(\d+)([.\dULCA]+)[-\sA-Z]*(\d+)([.\dULCA]+)[\s-]+', str(self.get_bios(f'PLT_EUFD_LINE{i}')))
            if mat:
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
            mat = search(r'(.*)\|(.*)\|(.*)', str(self.get_bios(f'PLT_EUFD_LINE{i}')))
            if mat:
                warn.extend([w for w in [mat.group(1).strip(), mat.group(2).strip(), mat.group(3).strip()] if w])
        return warn

    def _draw_for_pre(self, draw: ImageDraw.ImageDraw, xcords: List[int], ycords: List[int], font: ImageFont.FreeTypeFont) -> None:
        """
        Draw image for PRE mode.

        :param draw: ImageDraw instance
        :param xcords: list of X coordinates
        :param ycords: list of Y coordinates
        :param font: font instance
        """
        match_dict = {
            2: r'.*\|.*\|([\u2192\s]CO CMD)\s*([\d\.]*)\s+',
            3: r'.*\|.*\|([\u2192\s][A-Z\d\/]*)\s*([\d\.]*)\s+',
            4: r'.*\|.*\|([\u2192\s][A-Z\d\/]*)\s*([\d\.]*)\s+',
            5: r'.*\|.*\|([\u2192\s][A-Z\d\/]*)\s*([\d\.]*)\s+',
            6: r'\s*\|([\u2192\s][A-Z\d\/]*)\s*([\d\.]*)\s+',
            7: r'\s*\|([\u2192\s][A-Z\d\/]*)\s*([\d\.]*)\s+',
            8: r'\s*\|([\u2192\s][A-Z\d\/]*)\s*([\d\.]*)\s+',
            9: r'\s*\|([\u2192\s][A-Z\d\/]*)\s*([\d\.]*)\s+',
            10: r'\s*\|([\u2192\s][A-Z\d\/]*)\s*([\d\.]*)\s+',
            11: r'\s*\|([\u2192\s][A-Z\d\/]*)\s*([\d\.]*)\s+',
        }
        for i, xcord, ycord in zip(range(2, 12), xcords, ycords):
            mat = search(match_dict[i], str(self.get_bios(f'PLT_EUFD_LINE{i}')))
            if mat:
                draw.text(xy=(xcord, ycord), text=f'{mat.group(1):<9}{mat.group(2):>7}',
                          fill=self.lcd.foreground, font=font)

    def set_bios(self, selector: str, value: Union[str, int]) -> None:
        """
        Set new data.

        :param selector:
        :param value:
        """
        if selector == 'PLT_EUFD_LINE1':
            match = search(r'.*\|.*\|(PRESET TUNE)\s\w+', str(value))
            self.mode = ApacheEufdMode.IDM
            if match:
                self.mode = ApacheEufdMode.PRE
        if selector in ('PLT_EUFD_LINE8', 'PLT_EUFD_LINE9', 'PLT_EUFD_LINE10', 'PLT_EUFD_LINE11', 'PLT_EUFD_LINE12'):
            LOG.debug(f'{type(self).__name__} {selector} original: "{value}"')
            value = str(value).replace(']', '\u2666').replace('[', '\u25ca').replace('~', '\u25a0'). \
                replace('>', '\u25b8').replace('<', '\u25c2').replace('=', '\u2219')
        if 'PLT_EUFD_LINE' in selector:
            LOG.debug(f'{type(self).__name__} {selector} original: "{value}"')
            value = str(value).replace('!', '\u2192')  # replace ! with ->
        super().set_bios(selector, value)

    def button_request(self, button: Union[LcdButton, Gkey]) -> str:
        """
        Prepare AH-64D Apache specific DCS-BIOS request for button pressed.

        For G13/G15/G510: 1-4
        For G19 9-15: LEFT = 9, RIGHT = 10, OK = 11, CANCEL = 12, UP = 13, DOWN = 14, MENU = 15
        Or any G-Key 1 to 29

        :param button: LcdButton Enum
        :return: ready to send DCS-BIOS request
        """
        wca_or_idm = 'PLT_EUFD_WCA 0\n|PLT_EUFD_WCA 1\n'
        if self.mode == ApacheEufdMode.IDM:
            wca_or_idm = 'PLT_EUFD_IDM 0\n|PLT_EUFD_IDM 1\n'

        if button in (LcdButton.FOUR, LcdButton.UP) and self.mode == ApacheEufdMode.IDM:
            self.mode = ApacheEufdMode.WCA
        elif button in (LcdButton.FOUR, LcdButton.UP) and self.mode != ApacheEufdMode.IDM:
            self.mode = ApacheEufdMode.IDM

        if button in (LcdButton.ONE, LcdButton.LEFT) and self.mode == ApacheEufdMode.WCA:
            self.warning_line += 1

        self.button_actions[LcdButton.ONE] = wca_or_idm
        self.button_actions[LcdButton.LEFT] = wca_or_idm
        return super().button_request(button)


class A10C(AdvancedAircraft):
    """A-10C Warthog."""
    bios_name: str = 'A-10C'

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create A-10C Warthog or A-10C II Tank Killer.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, Union[str, int]] = {
            'VHFAM_FREQ1': '',
            'VHFAM_FREQ2': int(),
            'VHFAM_FREQ3': int(),
            'VHFAM_FREQ4': '',
            'VHFAM_PRESET': '',
            'VHFFM_FREQ1': '',
            'VHFFM_FREQ2': int(),
            'VHFFM_FREQ3': int(),
            'VHFFM_FREQ4': '',
            'VHFFM_PRESET': '',
            'UHF_100MHZ_SEL': '',
            'UHF_10MHZ_SEL': int(),
            'UHF_1MHZ_SEL': int(),
            'UHF_POINT1MHZ_SEL': int(),
            'UHF_POINT25_SEL': '',
            'UHF_PRESET': '',
            'ARC210_FREQUENCY': '',
            'ARC210_PREV_MANUAL_FREQ': '',
        }

    def _generate_freq_values(self) -> Sequence[str]:
        """
        Generate frequency for all 3 radios (ARC AM, VHF AM, VHF FM and UHF).

        :return: All 4 frequency settings as strings
        """
        vhfam = f'{self.get_bios("VHFAM_FREQ1")}{self.get_bios("VHFAM_FREQ2")}.' \
                f'{self.get_bios("VHFAM_FREQ3")}{self.get_bios("VHFAM_FREQ4")} ({self.get_bios("VHFAM_PRESET")})'
        vhffm = f'{self.get_bios("VHFFM_FREQ1")}{self.get_bios("VHFFM_FREQ2")}.' \
                f'{self.get_bios("VHFFM_FREQ3")}{self.get_bios("VHFFM_FREQ4")} ({self.get_bios("VHFFM_PRESET")})'
        uhf = f'{self.get_bios("UHF_100MHZ_SEL")}{self.get_bios("UHF_10MHZ_SEL")}{self.get_bios("UHF_1MHZ_SEL")}.' \
              f'{self.get_bios("UHF_POINT1MHZ_SEL")}{self.get_bios("UHF_POINT25_SEL")} ({self.get_bios("UHF_PRESET")})'
        arc = f'{self.get_bios("ARC210_FREQUENCY")} ({self.get_bios("ARC210_PREV_MANUAL_FREQ")})'
        return uhf, vhfam, vhffm, arc

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for A-10C Warthog for Mono LCD."""
        draw = ImageDraw.Draw(img)
        uhf, vhfam, vhffm, _ = self._generate_freq_values()
        for i, line in enumerate(['      *** RADIOS ***', f' AM: {vhfam}', f'UHF: {uhf}', f' FM: {vhffm}']):
            offset = i * 10
            draw.text(xy=(0, offset), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for A-10C Warthog for Color LCD."""
        draw = ImageDraw.Draw(img)
        uhf, vhfam, vhffm, _ = self._generate_freq_values()
        for i, line in enumerate(['      *** RADIOS ***', f' AM: {vhfam}', f'UHF: {uhf}', f' FM: {vhffm}']):
            offset = i * 20
            draw.text(xy=(0, offset), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)


class A10C2(A10C):
    """A-10C II Tank Killer."""
    bios_name: str = 'A-10C_2'

    def draw_for_lcd_mono(self, img: Image.Image) -> None:
        """Prepare image for A-10C II Tank Killer for Mono LCD."""
        draw = ImageDraw.Draw(img)
        uhf, _, vhffm, arc = self._generate_freq_values()
        for i, line in enumerate(['      *** RADIOS ***', f' AM: {arc}', f'UHF: {uhf}', f' FM: {vhffm}']):
            offset = i * 10
            draw.text(xy=(0, offset), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)

    def draw_for_lcd_color(self, img: Image.Image) -> None:
        """Prepare image for A-10C II Tank Killer for Color LCD."""
        draw = ImageDraw.Draw(img)
        uhf, _, vhffm, arc = self._generate_freq_values()
        for i, line in enumerate(['      *** RADIOS ***', f' AM: {arc}', f'UHF: {uhf}', f' FM: {vhffm}']):
            offset = i * 20
            draw.text(xy=(0, offset), text=line, fill=self.lcd.foreground, font=self.lcd.font_s)


class F14B(AdvancedAircraft):
    """F-14B Tomcat."""
    bios_name: str = 'F-14B'

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create F-14B Tomcat.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, Union[str, int]] = {
            'RIO_CAP_CLEAR': int(),
            'RIO_CAP_SW': int(),
            'RIO_CAP_NE': int(),
            'RIO_CAP_ENTER': int(),
        }
        self.button_actions = {
            LcdButton.ONE: 'RIO_CAP_CLEAR 1\n|RIO_CAP_CLEAR 0\n',
            LcdButton.TWO: 'RIO_CAP_SW 1\n|RIO_CAP_SW 0\n',
            LcdButton.THREE: 'RIO_CAP_NE 1\n|RIO_CAP_NE 0\n',
            LcdButton.FOUR: 'RIO_CAP_ENTER 1\n|RIO_CAP_ENTER 0\n',
            LcdButton.LEFT: 'RIO_CAP_CLEAR 1\n|RIO_CAP_CLEAR 0\n',
            LcdButton.RIGHT: 'RIO_CAP_SW 1\n|RIO_CAP_SW 0\n',
            LcdButton.DOWN: 'RIO_CAP_NE 1\n|RIO_CAP_NE 0\n',
            LcdButton.UP: 'RIO_CAP_ENTER 1\n|RIO_CAP_ENTER 0\n',
        }

    def _draw_common_data(self, draw: ImageDraw.ImageDraw) -> None:
        """
        Draw common part for Mono and Color LCD.

        :param draw: ImageDraw instance
        """
        draw.text(xy=(2, 3), text=f'{SUPPORTED_CRAFTS[type(self).__name__]["name"]}', fill=self.lcd.foreground, font=self.lcd.font_l)

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

    def __init__(self, lcd_type: LcdInfo) -> None:
        """
        Create AV-8B Night Attack.

        :param lcd_type: LCD type
        """
        super().__init__(lcd_type)
        self.bios_data: Dict[str, Union[str, int]] = {
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
        self.button_actions = {
            LcdButton.ONE: 'UFC_COM1_SEL -3200\n',
            LcdButton.TWO: 'UFC_COM1_SEL 3200\n',
            LcdButton.THREE: 'UFC_COM2_SEL -3200\n',
            LcdButton.FOUR: 'UFC_COM2_SEL 3200\n',
            LcdButton.LEFT: 'UFC_COM1_SEL -3200\n',
            LcdButton.RIGHT: 'UFC_COM1_SEL 3200\n',
            LcdButton.DOWN: 'UFC_COM2_SEL -3200\n',
            LcdButton.UP: 'UFC_COM2_SEL 3200\n',
        }

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
                            turn_on: Union[str, int]) -> None:
    """
    Draw rectangles with background for autopilot channels.

    :param lcd: instance of LCD
    :param ap_channel: channel name
    :param c_rect: coordinates for rectangle
    :param c_text: coordinates for name
    :param draw_obj: ImageDraw instance
    :param turn_on: channel on/off, fill on/off
    """
    if turn_on:
        draw_obj.rectangle(c_rect, fill=lcd.foreground, outline=lcd.foreground)
        draw_obj.text(xy=c_text, text=ap_channel, fill=lcd.background, font=lcd.font_l)
    else:
        draw_obj.rectangle(xy=c_rect, fill=lcd.background, outline=lcd.foreground)
        draw_obj.text(xy=c_text, text=ap_channel, fill=lcd.foreground, font=lcd.font_l)
