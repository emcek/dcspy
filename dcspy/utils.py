from os import path
from sys import prefix

from PIL import ImageFont

DEDFONT_11 = ImageFont.truetype(path.join(prefix, 'dcspy_data', 'falconded.ttf'), 11)
FONT_11 = ImageFont.truetype('consola.ttf', 11)
FONT_16 = ImageFont.truetype('consola.ttf', 16)
