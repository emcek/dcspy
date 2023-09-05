from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from os import name
from pathlib import Path
from platform import architecture, python_implementation, python_version, uname
from sys import executable, platform
from typing import Sequence, Tuple, Union

from PIL import ImageFont

from dcspy.log import config_logger
from dcspy.utils import get_default_yaml, load_cfg, set_defaults, check_dcs_ver

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
__version__ = '2.3.1'

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


@dataclass
class Gkey:
    """Logitech G-Key."""
    key: int
    mode: int

    def __str__(self):
        """Return with format G<i>/M<j>."""
        return f"G{self.key}/M{self.mode}"

    def __bool__(self):
        """Return False when any of value is zero."""
        return all([self.key, self.mode])

    def __hash__(self):
        """Hash will be the same for any two Gkey instances with the same key and mode values."""
        return hash((self.key, self.mode))

    def to_dict(self):
        """
        Convert Gkey into dict.

        :return: ex. {'g_key': 2, 'mode': 1}
        """
        return {'g_key': self.key, 'mode': self.mode}


def generate_gkey(key: int, mode: int) -> Sequence[Gkey]:
    """
    Generate sequence of G-Keys.

    :param key: number of keys
    :param mode: number of modes
    :return:
    """
    return tuple([Gkey(k, m) for k in range(1, key + 1) for m in range(1, mode + 1)])


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
    foreground: Union[int, Tuple[int, int, int, int]]
    background: Union[int, Tuple[int, int, int, int]]
    mode: LcdMode
    font_xs: ImageFont.FreeTypeFont
    font_s: ImageFont.FreeTypeFont
    font_l: ImageFont.FreeTypeFont


default_yaml = get_default_yaml(local_appdata=LOCAL_APPDATA)
config = set_defaults(load_cfg(filename=default_yaml), filename=default_yaml)
LcdMono = LcdInfo(width=MONO_WIDTH, height=MONO_HEIGHT, type=LcdType.MONO, foreground=255,
                  background=0, mode=LcdMode.BLACK_WHITE, font_s=ImageFont.truetype(str(config['font_name']), int(config['font_mono_s'])),
                  font_l=ImageFont.truetype(str(config['font_name']), int(config['font_mono_l'])),
                  font_xs=ImageFont.truetype(str(config['font_name']), int(config['font_mono_xs'])))
LcdColor = LcdInfo(width=COLOR_WIDTH, height=COLOR_HEIGHT, type=LcdType.COLOR, foreground=(0, 255, 0, 255),
                   background=(0, 0, 0, 0), mode=LcdMode.TRUE_COLOR, font_s=ImageFont.truetype(str(config['font_name']), int(config['font_color_s'])),
                   font_l=ImageFont.truetype(str(config['font_name']), int(config['font_color_l'])),
                   font_xs=ImageFont.truetype(str(config['font_name']), int(config['font_color_xs'])))
LCD_TYPES = {
    'G19': {'klass': 'G19', 'icon': 'G19.png'},
    'G510': {'klass': 'G510', 'icon': 'G510.png'},
    'G15 v1': {'klass': 'G15v1', 'icon': 'G15v1.png'},
    'G15 v2': {'klass': 'G15v2', 'icon': 'G15v2.png'},
    'G13': {'klass': 'G13', 'icon': 'G13.png'},
}
LOG = getLogger(__name__)
config_logger(LOG, config['verbose'])

LOG.debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
LOG.debug(f'Python: {python_implementation()}-{python_version()}')
LOG.debug(f'Python exec: {executable}')
LOG.debug(f'{uname()}')
LOG.debug(f'Configuration: {config} from: {default_yaml}')
LOG.info(f'dcspy {__version__} https://github.com/emcek/dcspy')
dcs_type, dcs_ver = check_dcs_ver(Path(str(config["dcs"])))
LOG.info(f'DCS {dcs_type} ver: {dcs_ver}')


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
