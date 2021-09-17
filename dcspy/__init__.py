from logging import getLogger
from os import name
from platform import architecture, uname, python_implementation, python_version
from sys import platform, prefix
from typing import NamedTuple, Mapping, Union

from yaml import load, FullLoader, dump, parser
from PIL import ImageFont

from dcspy import lcd_sdk
from dcspy.log import config_logger

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

FONT_NAME = 'DejaVuSansMono.ttf'
if platform == 'win32':
    FONT_NAME = 'consola.ttf'
FONT = {size: ImageFont.truetype(FONT_NAME, size) for size in (11, 16, 22, 32)}


def load_cfg(filename=f'{prefix}/dcspy_data/config.yaml') -> Mapping[str, Union[str, int]]:
    """
    Load configuration form yaml filename.

    In case of any problems default values will be used.
    :param filename: path to yam file - default dcspy_data/config.yaml
    :return: configuration dict
    """
    cfg_dict = {'keyboard': 'G13', 'dcsbios': ''}
    try:
        with open(filename) as yaml_file:
            cfg_dict = load(yaml_file, Loader=FullLoader)
    except (FileNotFoundError, parser.ParserError) as err:
        LOG.warning(f'{err.__class__.__name__}: {filename} . Default configuration will be used.')
        LOG.debug(f'{err}')
    return cfg_dict


def save_cfg(cfg_dict: Mapping[str, Union[str, int]], filename=f'{prefix}/dcspy_data/config.yaml') -> None:
    """
    Update yaml file with dict.

    :param cfg_dict: configuration dict
    :param filename: path to yam file - default dcspy_data/config.yaml
    """
    curr_dict = load_cfg(filename)
    curr_dict.update(cfg_dict)
    with open(filename, 'w') as yaml_file:
        dump(curr_dict, yaml_file)


config = load_cfg()
LOG.debug(f'Configuration: {config}')
