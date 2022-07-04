from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from os import name
from platform import architecture, uname, python_implementation, python_version
from sys import platform
from typing import Union, Sequence

from PIL import ImageFont

from dcspy.sdk import lcd_sdk
from dcspy.log import config_logger
from dcspy.utils import load_cfg, set_defaults, default_yaml

SUPPORTED_CRAFTS = {'FA18Chornet': 'FA-18C_hornet', 'Ka50': 'Ka-50', 'F16C50': 'F-16C_50', 'AH64DBLKII': 'AH-64D',
                    'A10C': 'A-10C', 'A10C2': 'A-10C_2', 'F14B': 'F-14B', 'AV8BNA': 'AV8BNA'}
SEND_ADDR = ('127.0.0.1', 7778)
RECV_ADDR = ('', 5010)
MULTICAST_IP = '239.255.50.10'


class LcdType(Enum):
    mono = lcd_sdk.TYPE_MONO
    color = lcd_sdk.TYPE_COLOR


class LcdButton(Enum):
    none = 0x0
    one = 0x1
    two = 0x2
    three = 0x4
    four = 0x8
    left = 0x100
    right = 0x200
    ok = 0x400
    cancel = 0x800
    up = 0x1000
    down = 0x2000
    menu = 0x4000


@dataclass
class LcdInfo:
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

LcdMono = LcdInfo(width=lcd_sdk.MONO_WIDTH, height=lcd_sdk.MONO_HEIGHT, type=LcdType.mono, foreground=255,
                  buttons=(LcdButton.one, LcdButton.two, LcdButton.three, LcdButton.four),
                  background=0, mode='1', font_s=ImageFont.truetype(config['font_name'], config['font_mono_s']),
                  font_l=ImageFont.truetype(config['font_name'], config['font_mono_l']),
                  font_xs=ImageFont.truetype(config['font_name'], config['font_mono_xs']))
LcdColor = LcdInfo(width=lcd_sdk.COLOR_WIDTH, height=lcd_sdk.COLOR_HEIGHT, type=LcdType.color, foreground=(0, 255, 0, 255),
                   buttons=(LcdButton.left, LcdButton.right, LcdButton.up, LcdButton.down, LcdButton.ok, LcdButton.cancel, LcdButton.menu),
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
