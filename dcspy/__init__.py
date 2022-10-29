from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from os import name
from platform import architecture, uname, python_implementation, python_version
from sys import platform
from typing import Union, Sequence

from PIL import ImageFont

from dcspy.log import config_logger
from dcspy.sdk import lcd_sdk
from dcspy.utils import load_cfg, set_defaults, default_yaml

SUPPORTED_CRAFTS = {'FA18Chornet': {'name': 'F/A-18C Hornet', 'bios': 'FA-18C_hornet'},
                    'Ka50': {'name': 'Ka-50 Black Shark', 'bios': 'Ka-50'},
                    'F16C50': {'name': 'F-16C Viper', 'bios': 'F-16C_50'},
                    'AH64DBLKII': {'name': 'AH-64D Apache', 'bios': 'AH-64D'},
                    'A10C': {'name': 'A-10C Warthog', 'bios': 'A-10C'},
                    'A10C2': {'name': 'A-10C II Tank Killer', 'bios': 'A-10C2'},
                    'F14A135GR': {'name': 'F-14A Tomcat', 'bios': 'F14'},
                    'F14B': {'name': 'F-14B Tomcat', 'bios': 'F-14'},
                    'AV8BNA': {'name': 'AV-8B N/A Harrier', 'bios': 'AV8BNA'}}
SEND_ADDR = ('127.0.0.1', 7778)
RECV_ADDR = ('', 5010)
MULTICAST_IP = '239.255.50.10'


class LcdType(Enum):
    """LCD Type."""
    MONO = lcd_sdk.TYPE_MONO
    COLOR = lcd_sdk.TYPE_COLOR


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
class LcdInfo:
    """LCD info."""
    width: int
    height: int
    type: LcdType
    buttons: Sequence[LcdButton]
    foreground: Union[int, Sequence[int]]
    background: Union[int, Sequence[int]]
    mode: str
    font_xs: ImageFont.FreeTypeFont
    font_s: ImageFont.FreeTypeFont
    font_l: ImageFont.FreeTypeFont


config = set_defaults(load_cfg())

LcdMono = LcdInfo(width=lcd_sdk.MONO_WIDTH, height=lcd_sdk.MONO_HEIGHT, type=LcdType.MONO, foreground=255,
                  buttons=(LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR),
                  background=0, mode='1', font_s=ImageFont.truetype(config['font_name'], config['font_mono_s']),
                  font_l=ImageFont.truetype(config['font_name'], config['font_mono_l']),
                  font_xs=ImageFont.truetype(config['font_name'], config['font_mono_xs']))
LcdColor = LcdInfo(width=lcd_sdk.COLOR_WIDTH, height=lcd_sdk.COLOR_HEIGHT, type=LcdType.COLOR, foreground=(0, 255, 0, 255),
                   buttons=(LcdButton.LEFT, LcdButton.RIGHT, LcdButton.UP, LcdButton.DOWN, LcdButton.OK, LcdButton.CANCEL, LcdButton.MENU),
                   background=(0, 0, 0, 0), mode='RGBA', font_s=ImageFont.truetype(config['font_name'], config['font_color_s']),
                   font_l=ImageFont.truetype(config['font_name'], config['font_color_l']),
                   font_xs=ImageFont.truetype(config['font_name'], config['font_color_xs']))

LCD_TYPES = {'G19': 'KeyboardColor', 'G510': 'KeyboardMono', 'G15 v1/v2': 'KeyboardMono', 'G13': 'KeyboardMono'}
LOG = getLogger(__name__)
config_logger(LOG, config['verbose'])

LOG.debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
LOG.debug(f'Python: {python_implementation()}-{python_version()}')
LOG.debug(f'{uname()}')
LOG.info(f'Configuration: {config} from: {default_yaml}')
