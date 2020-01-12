from collections import namedtuple
from logging import basicConfig, DEBUG, debug
from os import name
from platform import architecture, uname, python_implementation, python_version
from sys import platform

from PIL import ImageFont

basicConfig(format='%(asctime)s | %(levelname)-7s | %(message)s / %(filename)s:%(lineno)d', level=DEBUG)
__version__ = '0.9.2'
SUPPORTED_CRAFTS = {'FA18Chornet': 'FA-18C_hornet', 'Ka50': 'Ka-50', 'F16C50': 'F-16C_50'}
LCD_SIZE = namedtuple('lcd_size', ['width', 'height'])

debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
debug(f'Python: {python_implementation()}-{python_version()}')
debug(f'{uname()}')


if platform == 'win32':
    FONT_11 = ImageFont.truetype('consola.ttf', 11)
    FONT_16 = ImageFont.truetype('consola.ttf', 16)
else:
    FONT_11 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
    FONT_16 = ImageFont.truetype('DejaVuSansMono.ttf', 16)
