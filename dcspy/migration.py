from logging import getLogger
from pprint import pformat
from typing import Callable, Iterator, Union

from packaging import version

from dcspy.models import DcspyConfigYaml
from dcspy.utils import defaults_cfg

LOG = getLogger(__name__)
__version__ = '3.0.0-rc2'


def migrate(cfg: DcspyConfigYaml) -> DcspyConfigYaml:
    """
    Perform migration of configuration based on API version.

    If api_ver key do not exist, it is set to 2.3.3.

    :param cfg: configuration dict
    :return: Full migrated dict
    """
    LOG.debug(f'Starting configuration:\n{pformat(cfg)}')
    src_ver = cfg.get('api_ver', '2.3.3')  # do not touch this api_ver!
    LOG.debug(f'Current API version: {src_ver}')
    for migration_func in _filter_api_ver_func(str(src_ver)):
        migration_func(cfg)
        LOG.debug(f'Migration done: {migration_func.__name__}')
    cfg['api_ver'] = __version__
    cfg_with_defaults = {key: cfg.get(key, value) for key, value in defaults_cfg.items()}
    if 'UNKNOWN' in str(cfg_with_defaults['dcsbios']):
        cfg_with_defaults['dcsbios'] = defaults_cfg['dcsbios']
    final_cfg = {**cfg_with_defaults, **cfg}
    LOG.debug(f'Final configuration:\n{pformat(final_cfg)}')
    return final_cfg


def _filter_api_ver_func(cfg_ver: str) -> Iterator[Callable[[DcspyConfigYaml], None]]:
    """
    Filter migration function to call.

    :param cfg_ver: Current version of configuration
    :return: yield list of migration functions
    """
    api_ver_list = sorted([func_name.strip('_api_ver_').replace('_', '.')
                           for func_name in globals()
                           if func_name.startswith('_api_ver_')],
                          key=version.Version)
    for api_ver in api_ver_list:
        if version.Version(api_ver) > version.Version(cfg_ver) <= version.Version(__version__):
            yield globals()['_api_ver_{}'.format(api_ver.replace('.', '_'))]


def _api_ver_3_0_0rc1(cfg: DcspyConfigYaml) -> None:
    """
    Migrate to version 3.0.0.

    :param cfg: Configuration dictionary
    """
    _add_key(cfg, 'completer_items', 20)
    _add_key(cfg, 'current_plane', 'A-10C')
    _add_key(cfg, 'gkeys_area', 2)
    _add_key(cfg, 'gkeys_float', False)
    _add_key(cfg, 'toolbar_style', 0)

    _remove_key(cfg, 'theme_color')
    _remove_key(cfg, 'theme_mode')

    _rename_key_keep_value(cfg, 'font_color_s', 'font_color_m', 22)
    _rename_key_keep_value(cfg, 'font_color_xs', 'font_color_s', 18)
    _rename_key_keep_value(cfg, 'font_mono_s', 'font_mono_m', 11)
    _rename_key_keep_value(cfg, 'font_mono_xs', 'font_mono_s', 9)


def _add_key(cfg: DcspyConfigYaml, key: str, default_value: Union[str, int, bool]) -> None:
    """
    Add key to dictionary if not exists.

    :param cfg: Configuration dictionary
    :param key: key name
    :param default_value: value to set
    """
    if key not in cfg:
        cfg[key] = default_value


def _remove_key(cfg: DcspyConfigYaml, key: str) -> None:
    """
    Remove key from dictionary.

    :param cfg: Configuration dictionary
    :param key: key name
    """
    try:
        del cfg[key]
    except KeyError:
        pass


def _rename_key_keep_value(cfg: DcspyConfigYaml, old_name: str, new_name: str, default_value: Union[str, int, bool]) -> None:
    """
    Rename key in dictionary and keep value.

    :param cfg: Configuration dictionary
    :param old_name: Old key name
    :param new_name: New key name
    :param default_value: default value if old key do not exist
    """
    value = cfg.get(old_name, default_value)
    try:
        del cfg['old_name']
    except KeyError:
        pass
    cfg[new_name] = value
