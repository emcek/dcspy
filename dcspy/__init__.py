from logging import getLogger
from os import name
from platform import architecture, uname, python_implementation, python_version
from sys import platform
from typing import NamedTuple, Union, Sequence

from PIL import ImageFont

from dcspy import lcd_sdk
from dcspy.log import config_logger
from dcspy.utils import load_cfg, set_defaults, default_yaml

SUPPORTED_CRAFTS = {'FA18Chornet': 'FA-18C_hornet', 'Ka50': 'Ka-50', 'F16C50': 'F-16C_50',
                    'A10C': 'A-10C', 'A10C2': 'A-10C_2', 'F14B': 'F-14B'}
SEND_ADDR = ('127.0.0.1', 7778)
RECV_ADDR = ('', 5010)
MULTICAST_IP = '239.255.50.10'
LcdInfo = NamedTuple('LcdInfo', [('width', int), ('height', int), ('type', int),
                                 ('fg', Union[int, Sequence[int]]), ('bg', Union[int, Sequence[int]])])
LcdMono = LcdInfo(width=lcd_sdk.MONO_WIDTH, height=lcd_sdk.MONO_HEIGHT, type=lcd_sdk.TYPE_MONO, fg=255, bg=0)
LcdColor = LcdInfo(width=lcd_sdk.COLOR_WIDTH, height=lcd_sdk.COLOR_HEIGHT, type=lcd_sdk.TYPE_COLOR, fg=(0, 255, 0, 255), bg=(0, 0, 0, 0))
LCD_TYPES = {'G19': 'KeyboardColor', 'G510': 'KeyboardMono', 'G15 v1/v2': 'KeyboardMono', 'G13': 'KeyboardMono'}
LOG = getLogger(__name__)
config_logger(LOG)

LOG.debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
LOG.debug(f'Python: {python_implementation()}-{python_version()}')
LOG.debug(f'{uname()}')

config = set_defaults(load_cfg())
FONT_NAME = 'DejaVuSansMono.ttf'
if platform == 'win32':
    FONT_NAME = 'consola.ttf'
FONT = {size: ImageFont.truetype(FONT_NAME, size) for size in (11, 16, 22, 32)}
LOG.info(f'Configuration: {config} from: {default_yaml}')
