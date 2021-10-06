from datetime import datetime
from logging import getLogger
from os import environ, makedirs
from sys import prefix, version_info
from typing import Dict, Union, List, Tuple

from packaging import version
from psutil import process_iter
from requests import get
from yaml import load, FullLoader, parser, dump

LOG = getLogger(__name__)
ConfigDict = Dict[str, Union[str, int, List[int]]]
default_yaml = f'{prefix}/dcspy_data/config.yaml'


def load_cfg(filename=default_yaml) -> ConfigDict:
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


def save_cfg(cfg_dict: ConfigDict, filename=default_yaml) -> None:
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
                            'keyboard': 'G13',
                            'auto_gui': True}
    migrated_cfg = {key: cfg.get(key, defaults[key]) for key in defaults}
    save_cfg(migrated_cfg)
    return migrated_cfg


def check_ver_at_github(repo: str, current_ver: str) -> Tuple[bool, str, str, str, bool]:
    """
    Check version of <organization>/<package> at GitHub.

    Return tuple with:
    - result (bool) - if local version is latest
    - online version (str) - latest version
    - download url (str) - ready to download
    - published date (str) - format DD MMMM YYYY
    - pre-release (bool) - normal or pre release

    :param repo: format '<organization or user>/<package>'
    :param current_ver: current local version
    :return: tuple with information
    """
    latest, online_version, asset_url, published, pre_release = False, '', '', '', False
    package = repo.split('/')[1]
    try:
        response = get(f'https://api.github.com/repos/{repo}/releases/latest')
        if response.ok:
            dict_json = response.json()
            online_version = dict_json['tag_name']
            pre_release = dict_json['prerelease']
            # code need cleanup after remove py36
            frmt = '%Y-%m-%dT%H:%M:%S%z' if version_info.minor > 6 else '%Y-%m-%dT%H:%M:%SZ'
            published = datetime.strptime(dict_json['published_at'], frmt).strftime('%d %B %Y')
            asset_url = dict_json['assets'][0]['browser_download_url']
            LOG.debug(f'Latest GitHub version:{online_version} pre:{pre_release} date:{published} url:{asset_url}')
            if version.parse(online_version) > version.parse(current_ver):
                LOG.info(f'There is new version of {package}: {online_version}')
            elif version.parse(online_version) <= version.parse(current_ver):
                LOG.info(f'{package} is up-to-date version: {current_ver}')
                latest = True
        else:
            LOG.warning(f'Unable to check {package} version online. Try again later. Status={response.status_code}')
    except Exception as exc:
        LOG.warning(f'Unable to check {package} version online: {exc}')
    return latest, online_version, asset_url, published, pre_release


def download_file(url: str, save_path: str) -> bool:
    """
    Download file from URL and save to save_path.

    :param url: URL address
    :param save_path: full path to save
    """
    response = get(url=url, stream=True)
    if response.ok:
        LOG.debug(f'Download file from: {url}')
        with open(save_path, 'wb+') as dl_file:
            for chunk in response.iter_content(chunk_size=128):
                dl_file.write(chunk)
            LOG.debug(f'Saved as: {save_path}')
            return True
    else:
        LOG.warning(f'Can not download from: {url}')
        return False


def proc_is_running(name: str) -> int:
    """
    Check if process is running and return its PID.

    If process name is not found, 0 (zero) is returned.
    :param name: process name
    :return: PID as int
    """
    for proc in process_iter(['pid', 'name']):
        if name in proc.info['name']:
            return proc.info['pid']
    return 0
