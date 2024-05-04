import re
from collections.abc import Iterator
from logging import getLogger
from os import makedirs
from pathlib import Path
from pprint import pformat
from shutil import SameFileError, copy
from typing import Callable, Union

from packaging import version

from dcspy.models import DcspyConfigYaml
from dcspy.utils import DEFAULT_YAML_FILE, defaults_cfg, get_config_yaml_location

LOG = getLogger(__name__)
__version__ = '3.4.1'


def migrate(cfg: DcspyConfigYaml) -> DcspyConfigYaml:
    """
    Perform migration of configuration based on the API version.

    If the api_ver key does not exist, it is set to 2.3.3.

    :param cfg: Configuration dictionary
    :return: Full migrated dictionary
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

    :param cfg_ver: A current version of a configuration
    :return: Yields a migration function from a list
    """
    api_ver_list = sorted([func_name.strip('_api_ver_').replace('_', '.')
                           for func_name in globals()
                           if func_name.startswith('_api_ver_')],
                          key=version.Version)
    for api_ver in api_ver_list:
        if version.Version(api_ver) > version.Version(cfg_ver) <= version.Version(__version__):
            yield globals()['_api_ver_{}'.format(api_ver.replace('.', '_'))]


def _api_ver_3_4_0(cfg: DcspyConfigYaml) -> None:
    """
    Migrate to version 3.4.0.

    :param cfg: Configuration dictionary
    """
    user_appdata = get_config_yaml_location()
    makedirs(name=user_appdata, exist_ok=True)
    _rename_key_keep_value(cfg, 'keyboard', 'device', 'G13')
    cfg['device'] = str(cfg['device']).replace(' ', '')


def _api_ver_3_1_3(cfg: DcspyConfigYaml) -> None:
    """
    Migrate to version 3.1.3.

    :param cfg: Configuration dictionary
    """
    user_appdata = get_config_yaml_location()
    makedirs(name=user_appdata, exist_ok=True)
    _remove_key(cfg, 'font_mono_xs')
    _remove_key(cfg, 'font_color_xs')


def _api_ver_3_1_1(cfg: DcspyConfigYaml) -> None:
    """
    Migrate to version 3.1.1.

    :param cfg: Configuration dictionary
    """
    user_appdata = get_config_yaml_location()
    makedirs(name=user_appdata, exist_ok=True)
    _copy_file(filename='AH-64D_BLK_II.yaml', to_path=user_appdata, force=True)


def _api_ver_3_1_0(cfg: DcspyConfigYaml) -> None:
    """
    Migrate to version 3.1.0.

    :param cfg: Configuration dictionary
    """
    user_appdata = get_config_yaml_location()
    makedirs(name=user_appdata, exist_ok=True)
    for filename in ('AH-64D_BLK_II.yaml', 'AV8BNA.yaml', 'F-14A-135-GR.yaml', 'F-14B.yaml', 'F-15ESE.yaml',
                     'F-16C_50.yaml', 'FA-18C_hornet.yaml', 'Ka-50.yaml', 'Ka-50_3.yaml'):
        _copy_file(filename=filename, to_path=user_appdata)


def _api_ver_3_0_0(cfg: DcspyConfigYaml) -> None:
    """
    Migrate to version 3.0.0.

    :param cfg: Configuration dictionary
    """
    _add_key(cfg, 'completer_items', 20)
    _add_key(cfg, 'current_plane', 'A-10C')
    _add_key(cfg, 'gkeys_area', 2)
    _add_key(cfg, 'gkeys_float', False)
    _add_key(cfg, 'toolbar_area', 4)
    _add_key(cfg, 'toolbar_style', 0)

    _remove_key(cfg, 'theme_color')
    _remove_key(cfg, 'theme_mode')

    _rename_key_keep_value(cfg, 'font_color_s', 'font_color_m', 22)
    _rename_key_keep_value(cfg, 'font_color_xs', 'font_color_s', 18)
    _rename_key_keep_value(cfg, 'font_mono_s', 'font_mono_m', 11)
    _rename_key_keep_value(cfg, 'font_mono_xs', 'font_mono_s', 9)


def _add_key(cfg: DcspyConfigYaml, key: str, default_value: Union[str, int, bool]) -> None:
    """
    Add key to a dictionary if not exists.

    :param cfg: Configuration dictionary
    :param key: key name
    :param default_value: value to set
    """
    if key not in cfg:
        cfg[key] = default_value
        LOG.debug(f'Added key: {key} with: {default_value}')


def _remove_key(cfg: DcspyConfigYaml, key: str) -> None:
    """
    Remove key from dictionary.

    :param cfg: Configuration dictionary
    :param key: key name
    """
    try:
        del cfg[key]
        LOG.debug(f'Remove key: {key}')
    except KeyError:
        pass


def _rename_key_keep_value(cfg: DcspyConfigYaml, old_name: str, new_name: str, default_value: Union[str, int, bool]) -> None:
    """
    Rename key in dictionary and keep value.

    :param cfg: Configuration dictionary
    :param old_name: Old key name
    :param new_name: New key name
    :param default_value: default value if an old key, do not exist
    """
    value = cfg.get(old_name, default_value)
    try:
        del cfg[old_name]
    except KeyError:
        pass
    cfg[new_name] = value
    LOG.debug(f'Rename key {old_name} -> {new_name} with: {value}')


def _copy_file(filename: str, to_path: Path, force=False) -> None:
    """
    Copy a file from one location to another, only when the file doesn't exist.

    :param filename: The name of the file to be copied.
    :param to_path: The full path where the file should be copied to.
    :param force: Force to overwrite existing file
    """
    if not Path(to_path / filename).is_file() or force:
        try:
            copy(src=DEFAULT_YAML_FILE.parent / filename, dst=to_path)
            LOG.debug(f'Copy file: {filename} to {to_path}')
        except SameFileError:
            pass


def _replace_line_in_file(filename: str, dir_path: Path, pattern: re.Pattern, new_text: str) -> None:
    """
    Replace a line in a file based on a given pattern.

    :param filename: The name of the file to replace the line in.
    :param dir_path: The directory path where the file is located.
    :param pattern: The regular expression pattern to search for in the file.
    :param new_text: The text to replace the line matching the pattern with.
    """
    yaml_filename = dir_path / filename
    try:
        with open(yaml_filename) as yaml_file:
            file_content = yaml_file.read()
        LOG.debug(yaml_filename)
        updated_content = re.sub(pattern, new_text, file_content)
        with open(yaml_filename, 'w') as yaml_file:
            yaml_file.write(updated_content)
    except FileNotFoundError:
        pass
