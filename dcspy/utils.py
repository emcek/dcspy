from logging import getLogger
from sys import prefix
from typing import Dict, Union

from yaml import load, FullLoader, parser, dump

LOG = getLogger(__name__)


def load_cfg(filename=f'{prefix}/dcspy_data/config.yaml') -> Dict[str, Union[str, int]]:
    """
    Load configuration form yaml filename.

    :param filename: path to yam file - default dcspy_data/config.yaml
    :return: configuration dict
    """
    cfg_dict: Dict[str, Union[str, int]] = {}
    try:
        with open(filename) as yaml_file:
            cfg_dict = load(yaml_file, Loader=FullLoader)
            if not isinstance(cfg_dict, dict):
                cfg_dict, old_dict = {}, cfg_dict
                raise AttributeError(f'Config is not a dict {type(old_dict)} value: **{old_dict}**')
            LOG.debug(f'Load: {cfg_dict}')
    except (FileNotFoundError, parser.ParserError, AttributeError) as err:
        LOG.warning(f'{err.__class__.__name__}: {filename}. Default configuration will be used.')
        LOG.debug(f'{err}')
    return cfg_dict


def save_cfg(cfg_dict: Dict[str, Union[str, int]], filename=f'{prefix}/dcspy_data/config.yaml') -> None:
    """
    Update yaml file with dict.

    :param cfg_dict: configuration dict
    :param filename: path to yam file - default dcspy_data/config.yaml
    """
    curr_dict = load_cfg(filename)
    curr_dict.update(cfg_dict)
    LOG.debug(f'Save: {curr_dict}')
    with open(filename, 'w') as yaml_file:
        dump(curr_dict, yaml_file)


def set_defaults(cfg: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
    """
    Set defaults to not existing config options.

    :param cfg: dict before migration
    :return: dict after migration
    """
    LOG.debug(f'Before migration: {cfg}')
    defaults = {'keyboard': 'G13', 'dcsbios': '', 'fontname': 'consola.ttf', 'fontsize': [11, 16, 22, 32]}
    migrated_cfg = {key: cfg.get(key, defaults[key]) for key in defaults}
    save_cfg(migrated_cfg)
    return migrated_cfg
