from dataclasses import dataclass
from enum import Enum, auto
from logging import getLogger
from os import name
from pathlib import Path
from platform import architecture, python_implementation, python_version, uname
from sys import platform
from typing import Sequence, Tuple, Union

from PIL import ImageFont

from dcspy.log import config_logger
from dcspy.utils import get_default_yaml, load_cfg, set_defaults

try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


SUPPORTED_CRAFTS = {
    'FA18Chornet': {'name': 'F/A-18C Hornet', 'bios': 'FA-18C_hornet'},
    'Ka50': {'name': 'Ka-50 Black Shark II', 'bios': 'Ka-50'},
    'Ka503': {'name': 'Ka-50 Black Shark III', 'bios': 'Ka-50_3'},
    'Mi8MT': {'name': 'Mi-8MTV2 Magnificent Eight', 'bios': 'Mi-8MT'},
    'Mi24P': {'name': 'Mi-24P Hind', 'bios': 'Mi-24P'},
    'F16C50': {'name': 'F-16C Viper', 'bios': 'F-16C_50'},
    'F15ESE': {'name': 'F-15ESE Eagle', 'bios': 'F-15ESE'},
    'AH64DBLKII': {'name': 'AH-64D Apache', 'bios': 'AH-64D_BLK_II'},
    'A10C': {'name': 'A-10C Warthog', 'bios': 'A-10C'},
    'A10C2': {'name': 'A-10C II Tank Killer', 'bios': 'A-10C_2'},
    'F14A135GR': {'name': 'F-14A Tomcat', 'bios': 'F-14A-135-GR'},
    'F14B': {'name': 'F-14B Tomcat', 'bios': 'F-14B'},
    'AV8BNA': {'name': 'AV-8B N/A Harrier', 'bios': 'AV8BNA'},
}
SEND_ADDR = ('127.0.0.1', 7778)
RECV_ADDR = ('', 5010)
MULTICAST_IP = '239.255.50.10'
LOCAL_APPDATA = True

# LCD types
TYPE_MONO = 1
TYPE_COLOR = 2

# LCD Monochrome size
MONO_WIDTH = 160
MONO_HEIGHT = 43

# LCD Color size
COLOR_WIDTH = 320
COLOR_HEIGHT = 240


# LED constants
LOGI_LED_DURATION_INFINITE = 0
LOGI_DEVICETYPE_MONOCHROME = 1
LOGI_DEVICETYPE_RGB = 2
LOGI_DEVICETYPE_ALL = LOGI_DEVICETYPE_MONOCHROME | LOGI_DEVICETYPE_RGB

# G Key
LOGITECH_MAX_GKEYS = 30
LOGITECH_MAX_M_STATES = 4


class LcdType(Enum):
    """LCD Type."""
    MONO = TYPE_MONO
    COLOR = TYPE_COLOR


class LcdButton(Enum):
    """LCD Buttons."""
    NONE = 0x0
    ONE = 0x1
    TWO = 0x2
    THREE = 0x4
    FOUR = 0x8
    LEFT = 0x100
    RIGHT = 0x200
    OK = 0x400
    CANCEL = 0x800
    UP = 0x1000
    DOWN = 0x2000
    MENU = 0x4000


class LcdGkey(Enum):
    G1_M1 = 11
    G2_M1 = 21
    G3_M1 = 31
    G4_M1 = 41
    G5_M1 = 51
    G6_M1 = 61
    G7_M1 = 71
    G8_M1 = 81
    G9_M1 = 91
    G10_M1 = 101
    G11_M1 = 111
    G12_M1 = 121
    G13_M1 = 131
    G14_M1 = 141
    G15_M1 = 151
    G16_M1 = 161
    G17_M1 = 171
    G18_M1 = 181
    G19_M1 = 191
    G20_M1 = 201
    G21_M1 = 211
    G22_M1 = 221
    G23_M1 = 231
    G24_M1 = 241
    G25_M1 = 251
    G26_M1 = 261
    G27_M1 = 271
    G28_M1 = 281
    G29_M1 = 291
    G1_M2 = 12
    G2_M2 = 22
    G3_M2 = 32
    G4_M2 = 42
    G5_M2 = 52
    G6_M2 = 62
    G7_M2 = 72
    G8_M2 = 82
    G9_M2 = 92
    G10_M2 = 102
    G11_M2 = 112
    G12_M2 = 122
    G13_M2 = 132
    G14_M2 = 142
    G15_M2 = 152
    G16_M2 = 162
    G17_M2 = 172
    G18_M2 = 182
    G19_M2 = 192
    G20_M2 = 202
    G21_M2 = 212
    G22_M2 = 222
    G23_M2 = 232
    G24_M2 = 242
    G25_M2 = 252
    G26_M2 = 262
    G27_M2 = 272
    G28_M2 = 282
    G29_M2 = 292
    G1_M3 = 13
    G2_M3 = 23
    G3_M3 = 33
    G4_M3 = 43
    G5_M3 = 53
    G6_M3 = 63
    G7_M3 = 73
    G8_M3 = 83
    G9_M3 = 93
    G10_M3 = 103
    G11_M3 = 113
    G12_M3 = 123
    G13_M3 = 133
    G14_M3 = 143
    G15_M3 = 153
    G16_M3 = 163
    G17_M3 = 173
    G18_M3 = 183
    G19_M3 = 193
    G20_M3 = 203
    G21_M3 = 213
    G22_M3 = 223
    G23_M3 = 233
    G24_M3 = 243
    G25_M3 = 253
    G26_M3 = 263
    G27_M3 = 273
    G28_M3 = 283
    G29_M3 = 293
    NONE = ''


class LcdMode(Enum):
    """LCD Mode."""
    BLACK_WHITE = '1'
    TRUE_COLOR = 'RGBA'


@dataclass
class LcdInfo:
    """LCD info."""
    width: int
    height: int
    type: LcdType
    buttons: Sequence[LcdButton]
    gkey: Sequence[LcdGkey]
    foreground: Union[int, Tuple[int, int, int, int]]
    background: Union[int, Tuple[int, int, int, int]]
    mode: LcdMode
    font_xs: ImageFont.FreeTypeFont
    font_s: ImageFont.FreeTypeFont
    font_l: ImageFont.FreeTypeFont


default_yaml = get_default_yaml(local_appdata=LOCAL_APPDATA)
config = set_defaults(load_cfg(filename=default_yaml), filename=default_yaml)
LcdMono = LcdInfo(width=MONO_WIDTH, height=MONO_HEIGHT, type=LcdType.MONO, foreground=255,
                  buttons=(LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR),
                  gkey=(LcdGkey.G1_M1, LcdGkey.G2_M1, LcdGkey.G8_M1, LcdGkey.G9_M1),
                  background=0, mode=LcdMode.BLACK_WHITE, font_s=ImageFont.truetype(str(config['font_name']), int(config['font_mono_s'])),
                  font_l=ImageFont.truetype(str(config['font_name']), int(config['font_mono_l'])),
                  font_xs=ImageFont.truetype(str(config['font_name']), int(config['font_mono_xs'])))
LcdColor = LcdInfo(width=COLOR_WIDTH, height=COLOR_HEIGHT, type=LcdType.COLOR, foreground=(0, 255, 0, 255),
                   buttons=(LcdButton.LEFT, LcdButton.RIGHT, LcdButton.UP, LcdButton.DOWN, LcdButton.OK, LcdButton.CANCEL, LcdButton.MENU),
                   gkey=(LcdGkey.G1_M1, LcdGkey.G2_M1, LcdGkey.G8_M1, LcdGkey.G9_M1),
                   background=(0, 0, 0, 0), mode=LcdMode.TRUE_COLOR, font_s=ImageFont.truetype(str(config['font_name']), int(config['font_color_s'])),
                   font_l=ImageFont.truetype(str(config['font_name']), int(config['font_color_l'])),
                   font_xs=ImageFont.truetype(str(config['font_name']), int(config['font_color_xs'])))
DED_FONT = ImageFont.truetype(str(Path(__file__).resolve().with_name('falconded.ttf')), 25)
LCD_TYPES = {
    'G19': {'type': 'KeyboardColor', 'icon': 'G19.png'},
    'G510': {'type': 'KeyboardMono', 'icon': 'G510.png'},
    'G15 v1': {'type': 'KeyboardMono', 'icon': 'G15v1.png'},
    'G15 v2': {'type': 'KeyboardMono', 'icon': 'G15v2.png'},
    'G13': {'type': 'KeyboardMono', 'icon': 'G13.png'},
}
LOG = getLogger(__name__)
config_logger(LOG, config['verbose'])

LOG.debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
LOG.debug(f'Python: {python_implementation()}-{python_version()}')
LOG.debug(f'{uname()}')
LOG.info(f'Configuration: {config} from: {default_yaml}')


class IntBuffArgs(TypedDict):
    address: int
    mask: int
    shift_by: int


class StrBuffArgs(TypedDict):
    address: int
    max_length: int


class BiosValue(TypedDict):
    klass: str
    args: Union[StrBuffArgs, IntBuffArgs]
    value: Union[int, str]
    max_value: NotRequired[int]
