from logging import getLogger
from os import environ, makedirs
from sys import prefix
from typing import Dict, Union, List

from yaml import load, FullLoader, parser, dump

LOG = getLogger(__name__)
ConfigDict = Dict[str, Union[str, int, List[int]]]


def load_cfg(filename=f'{prefix}/dcspy_data/config.yaml') -> ConfigDict:
    """
    Load configuration form yaml filename.

    :param filename: path to yam file - default dcspy_data/config.yaml
    :return: configuration dict
    """
    cfg_dict: ConfigDict = {}
    try:
        with open(filename) as yaml_file:
            cfg_dict = load(yaml_file, Loader=FullLoader)
            if not isinstance(cfg_dict, dict):
                cfg_dict, old_dict = {}, cfg_dict
                raise AttributeError(f'Config is not a dict {type(old_dict)} value: **{old_dict}**')
            LOG.debug(f'Load: {cfg_dict}')
    except (FileNotFoundError, parser.ParserError, AttributeError) as err:
        makedirs(name=filename.rpartition('/')[0], exist_ok=True)
        LOG.warning(f'{err.__class__.__name__}: {filename}. Default configuration will be used.')
        LOG.debug(f'{err}')
    return cfg_dict


def save_cfg(cfg_dict: ConfigDict, filename=f'{prefix}/dcspy_data/config.yaml') -> None:
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


def set_defaults(cfg: ConfigDict) -> ConfigDict:
    """
    Set defaults to not existing config options.

    :param cfg: dict before migration
    :return: dict after migration
    """
    LOG.debug(f'Before migration: {cfg}')
    defaults: ConfigDict = {'dcsbios': f'D:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
                            'keyboard': 'G13', 'fontname': 'consola.ttf', 'fontsize': [11, 16, 22, 32]}
    migrated_cfg = {key: cfg.get(key, defaults[key]) for key in defaults}
    save_cfg(migrated_cfg)
    return migrated_cfg
