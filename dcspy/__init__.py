from logging import getLogger
from os import name
from pathlib import Path
from platform import architecture, python_implementation, python_version, uname
from sys import executable, platform
from typing import Union

from dcspy.log import config_logger
from dcspy.models import LOCAL_APPDATA
from dcspy.utils import check_dcs_ver, get_default_yaml, load_yaml, set_defaults

try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

__version__ = '3.0.0'

default_yaml = get_default_yaml(local_appdata=LOCAL_APPDATA)
config = set_defaults(load_yaml(full_path=default_yaml), filename=default_yaml)
LCD_TYPES = {
    'G19': {'klass': 'G19', 'icon': 'G19.png'},
    'G510': {'klass': 'G510', 'icon': 'G510.png'},
    'G15 v1': {'klass': 'G15v1', 'icon': 'G15v1.png'},
    'G15 v2': {'klass': 'G15v2', 'icon': 'G15v2.png'},
    'G13': {'klass': 'G13', 'icon': 'G13.png'},
}
LOG = getLogger(__name__)
config_logger(LOG, config['verbose'])

LOG.debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
LOG.debug(f'Python: {python_implementation()}-{python_version()}')
LOG.debug(f'Python exec: {executable}')
LOG.debug(f'{uname()}')
LOG.debug(f'Configuration: {config} from: {default_yaml}')
LOG.info(f'dcspy {__version__} https://github.com/emcek/dcspy')
dcs_type, dcs_ver = check_dcs_ver(Path(str(config['dcs'])))
LOG.info(f'DCS {dcs_type} ver: {dcs_ver}')


class IntBuffArgs(TypedDict):
    address: int
    mask: int
    shift_by: int


class StrBuffArgs(TypedDict):
    address: int
    max_length: int


class BiosValue(TypedDict):
    klass: str
    args: Union[StrBuffArgs, IntBuffArgs]
    value: Union[int, str]
    max_value: NotRequired[int]
