from sys import platform

from PIL import ImageFont

__version__ = '0.9.1'
SUPPORTED_CRAFTS = ('FA-18C_hornet', 'Ka-50', 'F-16C_50')

if platform == 'win32':
    FONT_11 = ImageFont.truetype('consola.ttf', 11)
    FONT_16 = ImageFont.truetype('consola.ttf', 16)
else:
    FONT_11 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
    FONT_16 = ImageFont.truetype('DejaVuSansMono.ttf', 16)
