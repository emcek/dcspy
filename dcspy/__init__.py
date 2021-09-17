from logging import getLogger
from os import name
from platform import architecture, uname, python_implementation, python_version
from sys import platform
from typing import NamedTuple

from PIL import ImageFont

from dcspy import lcd_sdk
from dcspy.log import config_logger
from dcspy.utils import load_cfg, set_defaults

SUPPORTED_CRAFTS = {'FA18Chornet': 'FA-18C_hornet', 'Ka50': 'Ka-50', 'F16C50': 'F-16C_50', 'F14B': 'F-14B'}
SEND_ADDR = ('127.0.0.1', 7778)
RECV_ADDR = ('', 5010)
MULTICAST_IP = '239.255.50.10'
LcdSize = NamedTuple('LcdSize', [('width', int), ('height', int), ('type', int)])
LcdMono = LcdSize(width=lcd_sdk.MONO_WIDTH, height=lcd_sdk.MONO_HEIGHT, type=lcd_sdk.TYPE_MONO)
LcdColor = LcdSize(width=lcd_sdk.COLOR_WIDTH, height=lcd_sdk.COLOR_HEIGHT, type=lcd_sdk.TYPE_COLOR)
LCD_TYPES = {'G19': 'KeyboardColor', 'G510': 'KeyboardMono', 'G15 v1/v2': 'KeyboardMono', 'G13': 'KeyboardMono'}
LOG = getLogger(__name__)
config_logger(LOG)

LOG.debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
LOG.debug(f'Python: {python_implementation()}-{python_version()}')
LOG.debug(f'{uname()}')

config = set_defaults(load_cfg())
FONT_NAME = 'DejaVuSansMono.ttf'
if platform == 'win32':
    FONT_NAME = config['fontname']
FONT = {size: ImageFont.truetype(FONT_NAME, size) for size in config['fontsize']}
LOG.info(f'Configuration: {config}')
