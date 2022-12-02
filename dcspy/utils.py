from datetime import datetime
from logging import getLogger
from os import environ, makedirs, path
from pathlib import Path
from re import search
from typing import Dict, Union, Tuple

from packaging import version
from psutil import process_iter
from requests import get
from yaml import load, FullLoader, parser, dump

LOG = getLogger(__name__)
ConfigDict = Dict[str, Union[str, int, bool]]
default_yaml = path.join(path.abspath(path.dirname(__file__)), 'config.yaml')


def load_cfg(filename=default_yaml) -> ConfigDict:
    """
    Load configuration form yaml filename.

    :param filename: path to yam file - default <package_dir>/config.yaml
    :return: configuration dict
    """
    cfg_dict: ConfigDict = {}
    try:
        with open(file=filename, encoding='utf-8') as yaml_file:
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
    :param filename: path to yam file - default <package_dir>/config.yaml
    """
    curr_dict = load_cfg(filename)
    curr_dict.update(cfg_dict)
    LOG.debug(f'Save: {curr_dict}')
    with open(file=filename, mode='w', encoding='utf-8') as yaml_file:
        dump(curr_dict, yaml_file)


def set_defaults(cfg: ConfigDict, filename=default_yaml) -> ConfigDict:
    """
    Set defaults to not existing config options.

    :param cfg: dict before migration
    :param filename: path to yam file - default <package_dir>/config.yaml
    :return: dict after migration
    """
    LOG.debug(f'Before migration: {cfg}')
    defaults: ConfigDict = {'dcsbios': f'D:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
                            'dcs': 'C:\\Program Files\\Eagle Dynamics\\DCS World OpenBeta',
                            'autostart': False,
                            'verbose': False,
                            'keyboard': 'G13',
                            'show_gui': True,
                            'font_name': 'consola.ttf',
                            'font_mono_s': 11,
                            'font_mono_xs': 9,
                            'font_mono_l': 16,
                            'font_color_s': 22,
                            'font_color_xs': 18,
                            'font_color_l': 32}
    migrated_cfg = {key: cfg.get(key, value) for key, value in defaults.items()}
    if 'UNKNOWN' in str(migrated_cfg['dcsbios']):
        migrated_cfg['dcsbios'] = defaults['dcsbios']
    save_cfg(cfg_dict=migrated_cfg, filename=filename)
    return migrated_cfg


def check_ver_at_github(repo: str, current_ver: str) -> Tuple[bool, Union[version.Version, version.LegacyVersion], str, str, str, str]:
    """
    Check version of <organization>/<package> at GitHub.

    Return tuple with:
    - result (bool) - if local version is latest
    - online version (version.Version, version.LegacyVersion) - the latest version
    - download url (str) - ready to download
    - published date (str) - format DD MMMM YYYY
    - release type (str) - Regular or Pre-release
    - archive file (str) - file name of archive

    :param repo: format '<organization or user>/<package>'
    :param current_ver: current local version
    :return: tuple with information
    """
    latest, online_version, asset_url, published, pre_release = False, 'unknown', '', '', False
    package = repo.split('/')[1]
    try:
        response = get(url=f'https://api.github.com/repos/{repo}/releases/latest', timeout=5)
        if response.ok:
            dict_json = response.json()
            online_version = dict_json['tag_name']
            pre_release = dict_json['prerelease']
            published = datetime.strptime(dict_json['published_at'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d %B %Y')
            asset_url = dict_json['assets'][0]['browser_download_url']
            LOG.debug(f'Latest GitHub version:{online_version} pre:{pre_release} date:{published} url:{asset_url}')
            latest = _compare_versions(package, current_ver, online_version)
        else:
            LOG.warning(f'Unable to check {package} version online. Try again later. Status={response.status_code}')
    except Exception as exc:
        LOG.warning(f'Unable to check {package} version online: {exc}')
    return latest, version.parse(online_version), asset_url, published, 'Pre-release' if pre_release else 'Regular', asset_url.split('/')[-1]


def _compare_versions(package: str, current_ver: str, remote_ver: str) -> bool:
    """
    Compare two version of package and return result.

    :param package: package name
    :param current_ver: current/local version
    :param remote_ver: remote/online version
    :return:
    """
    latest = False
    if version.parse(remote_ver) > version.parse(current_ver):
        LOG.info(f'There is new version of {package}: {remote_ver}')
    elif version.parse(remote_ver) <= version.parse(current_ver):
        LOG.info(f'{package} is up-to-date version: {current_ver}')
        latest = True
    return latest


def download_file(url: str, save_path: str) -> bool:
    """
    Download file from URL and save to save_path.

    :param url: URL address
    :param save_path: full path to save
    """
    response = get(url=url, stream=True, timeout=5)
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


def check_dcs_ver(dcs_path: str) -> Tuple[str, str]:
    """
    Check DCS version and release type.

    :param dcs_path: path to DCS installation directory
    :return: dcs type and version as strings
    """
    result_type, result_ver = 'Unknown', 'Unknown'
    try:
        with open(file=Path(path.join(dcs_path, 'autoupdate.cfg')), encoding='utf-8') as autoupdate_cfg:
            autoupdate_data = autoupdate_cfg.read()
    except FileNotFoundError as err:
        LOG.debug(f'{err.__class__.__name__}: {err.filename}')
    else:
        result_type = 'stable'
        dcs_type = search(r'"branch":\s"([\w.]*)"', autoupdate_data)
        if dcs_type:
            result_type = str(dcs_type.group(1))
        dcs_ver = search(r'"version":\s"([\d.]*)"', autoupdate_data)
        if dcs_ver:
            result_ver = str(dcs_ver.group(1))
    return result_type, result_ver
