from logging import getLogger
from os import name
from pathlib import Path
from platform import architecture, python_implementation, python_version, uname
from sys import executable, platform
from typing import Optional, Union

from dcspy.log import config_logger
from dcspy.migration import migrate
from dcspy.models import LOCAL_APPDATA
from dcspy.utils import check_dcs_ver, get_default_yaml, load_yaml, save_yaml

__version__ = '3.1.0'

default_yaml = get_default_yaml(local_appdata=LOCAL_APPDATA)
_config = migrate(load_yaml(full_path=default_yaml))
save_yaml(data=_config, full_path=default_yaml)
LOG = getLogger(__name__)
config_logger(LOG, _config['verbose'])

LOG.debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
LOG.debug(f'Python: {python_implementation()}-{python_version()}')
LOG.debug(f'Python exec: {executable}')
LOG.debug(f'{uname()}')
LOG.debug(f'Configuration: {_config} from: {default_yaml}')
LOG.info(f'dcspy {__version__} https://github.com/emcek/dcspy')
dcs_type, dcs_ver = check_dcs_ver(Path(str(_config['dcs'])))
LOG.info(f'DCS {dcs_type} ver: {dcs_ver}')


def get_config_yaml_item(key: str, /, default: Optional[Union[str, int]] = None) -> Union[str, int]:
    """
    Get item from configuration YAML file.

    :param key: key to get
    :param default: default value if key not found
    :return: value from configuration
    """
    return load_yaml(full_path=default_yaml).get(key, default)
