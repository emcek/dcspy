from os import path
from sys import platform, prefix

from PIL import ImageFont


if platform == 'win32':
    DEDFONT_11 = ImageFont.truetype(path.join(prefix, 'dcspy_data', 'falconded.ttf'), 11)
    FONT_11 = ImageFont.truetype('consola.ttf', 11)
    FONT_16 = ImageFont.truetype('consola.ttf', 16)
else:
    FONT_11 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
    FONT_16 = ImageFont.truetype('DejaVuSansMono.ttf', 16)
