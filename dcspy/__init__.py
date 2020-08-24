from logging import getLogger
from os import name, path
from platform import architecture, uname, python_implementation, python_version
from sys import platform, prefix
from typing import NamedTuple

from PIL import ImageFont

from dcspy.log import config_logger

__version__ = '1.1.1'
SUPPORTED_CRAFTS = {'FA18Chornet': 'FA-18C_hornet', 'Ka50': 'Ka-50', 'F16C50': 'F-16C_50', 'F14B': 'F-14B'}
SEND_ADDR = ('127.0.0.1', 7778)
RECV_ADDR = ('', 5010)
MULTICAST_IP = '239.255.50.10'
LcdSize = NamedTuple('lcd_size', [('width', int), ('height', int)])
LCD_TYPES = {'G19': 'KeyboardColor', 'G510': 'KeyboardMono', 'G15 v1/v2': 'KeyboardMono', 'G13': 'KeyboardMono'}
LOG = getLogger(__name__)
config_logger(LOG)

LOG.debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
LOG.debug(f'Python: {python_implementation()}-{python_version()}')
LOG.debug(f'{uname()}')

if platform == 'win32':
    DEDFONT_11 = ImageFont.truetype(path.join(prefix, 'dcspy_data', 'falconded.ttf'), 11)
    FONT_11 = ImageFont.truetype('consola.ttf', 11)
    FONT_16 = ImageFont.truetype('consola.ttf', 16)
else:
    FONT_11 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
    FONT_16 = ImageFont.truetype('DejaVuSansMono.ttf', 16)
