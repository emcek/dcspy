from PIL import ImageFont

__version__ = '0.9.1'
SUPPORTED_CRAFTS = ('FA-18C_hornet', 'Ka-50', 'F-16C_50')
# @todo: find better way
try:
    FONT1 = ImageFont.truetype('consola.ttf', 11)
except OSError:
    FONT1 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
try:
    FONT2 = ImageFont.truetype('consola.ttf', 16)
except OSError:
    FONT2 = ImageFont.truetype('DejaVuSansMono.ttf', 16)
