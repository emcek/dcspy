from __future__ import annotations

from logging import getLogger
from os import name
from pathlib import Path
from platform import architecture, python_implementation, python_version, uname
from sys import executable, platform

from dcspy.log import config_logger
from dcspy.migration import migrate
from dcspy.models import DCSPY_REPO_NAME, LOCAL_APPDATA, ConfigValue
from dcspy.utils import check_dcs_ver, get_default_yaml, load_yaml, save_yaml

LOG = getLogger(__name__)
__version__ = '3.6.1'

default_yaml = get_default_yaml(local_appdata=LOCAL_APPDATA)
_start_cfg = load_yaml(full_path=default_yaml)
config_logger(LOG, _start_cfg.get('verbose', False))
_config = migrate(_start_cfg)
save_yaml(data=_config, full_path=default_yaml)

LOG.debug(f'Arch: {name} / {platform} / {" / ".join(architecture())}')
LOG.debug(f'Python: {python_implementation()}-{python_version()}')
LOG.debug(f'Python exec: {executable}')
LOG.debug(f'{uname()}')
LOG.debug(f'Configuration: {_config} from: {default_yaml}')
LOG.info(f'dcspy {__version__} https://github.com/{DCSPY_REPO_NAME}')
dcs_type, dcs_ver = check_dcs_ver(Path(str(_config['dcs'])))
LOG.info(f'DCS {dcs_type} ver: {dcs_ver}')


def get_config_yaml_item(key: str, /, default: ConfigValue | None = None) -> ConfigValue:
    """
    Get item from a configuration YAML file.

    :param key: Key to get
    :param default: Default value if key not found
    :return: Value from configuration
    """
    return load_yaml(full_path=default_yaml).get(key, default)
