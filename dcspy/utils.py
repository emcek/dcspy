from datetime import datetime
from logging import getLogger
from os import environ, makedirs, path
from pathlib import Path
from re import search
from tempfile import gettempdir
from typing import Dict, Union, Tuple, NamedTuple

import git
from git import Repo
from git.exc import InvalidGitRepositoryError
from packaging import version
from psutil import process_iter
from requests import get
from yaml import load, FullLoader, parser, dump

LOG = getLogger(__name__)
ConfigDict = Dict[str, Union[str, int, bool]]
default_yaml = path.join(path.abspath(path.dirname(__file__)), 'config.yaml')
defaults_cfg: ConfigDict = {
    'dcsbios': f'D:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
    'dcs': 'C:\\Program Files\\Eagle Dynamics\\DCS World OpenBeta',
    'check_bios': True,
    'check_ver': True,
    'autostart': False,
    'verbose': False,
    'keyboard': 'G13',
    'save_lcd': False,
    'show_gui': True,
    'font_name': 'consola.ttf',
    'font_mono_s': 11,
    'font_mono_xs': 9,
    'font_mono_l': 16,
    'font_color_s': 22,
    'font_color_xs': 18,
    'font_color_l': 32,
    'git_bios': False,
    'git_bios_ref': 'master',
    'theme_mode': 'system',
    'theme_color': 'blue',
    'f16_ded_font': True
}


class ReleaseInfo(NamedTuple):
    """Tuple to store release related information."""
    latest: bool
    ver: Union[version.Version, version.LegacyVersion]
    dl_url: str
    published: str
    release_type: str
    archive_file: str


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
    migrated_cfg = {key: cfg.get(key, value) for key, value in defaults_cfg.items()}
    if 'UNKNOWN' in str(migrated_cfg['dcsbios']):
        migrated_cfg['dcsbios'] = defaults_cfg['dcsbios']
    save_cfg(cfg_dict=migrated_cfg, filename=filename)
    return migrated_cfg


def check_ver_at_github(repo: str, current_ver: str) -> ReleaseInfo:
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
    :return: ReleaseInfo NamedTuple with information
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
    return ReleaseInfo(latest, version.parse(online_version), asset_url, published, 'Pre-release' if pre_release else 'Regular', asset_url.split('/')[-1])


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


def get_version_string(repo: str, current_ver: str, check=True) -> str:
    """
    Generate formatted string with version number.

    :param repo: format '<organization or user>/<package>'
    :param current_ver: current local version
    :param check: version online
    :return: formatted version as string
    """
    ver_string = f'v{current_ver}'
    if check:
        result = check_ver_at_github(repo=repo, current_ver=current_ver)
        details = ''
        if result.latest:
            details = ' (latest)'
        elif str(result.ver) != 'unknown':
            details = ' (please update!)'
        elif str(result.ver) == 'unknown':
            details = ' (failed)'
        ver_string = f'v{current_ver}{details}'
    return ver_string


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
    except (FileNotFoundError, PermissionError) as err:
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


def is_git_repo(dir_path: str) -> bool:
    """
    Check if dir_path ios Git repository.

    :param dir_path: path as string
    :return: true if dir is git repo
    """
    try:
        _ = Repo(dir_path).git_dir
        return True
    except InvalidGitRepositoryError:
        return False


def check_github_repo(git_ref: str, update=True, repo='DCSFlightpanels/dcs-bios', repo_dir=path.join(gettempdir(), 'dcsbios_git')) -> str:
    """
    Update DCS-BIOS git repository.

    Return SHA of latest commit.

    :param git_ref: any Git reference as string
    :param update: perform update process
    :param repo: GitHub repository
    :param repo_dir: local directory for repository
    """
    makedirs(name=repo_dir, exist_ok=True)
    if is_git_repo(repo_dir):
        bios_repo = git.Repo(repo_dir)
        bios_repo.git.checkout('master')
    else:
        bios_repo = git.Repo.clone_from(url=f'https://github.com/{repo}.git', to_path=repo_dir)
    if update:
        f_info = bios_repo.remotes[0].pull()
        LOG.debug(f'Pulled: {f_info[0].name} as: {f_info[0].commit}')
        try:
            bios_repo.git.checkout(git_ref)
            branch = bios_repo.active_branch.name
            head_commit = bios_repo.head.commit
            sha = f'{branch}: {head_commit.committed_datetime} by: {head_commit.author}'
        except (git.exc.GitCommandError, TypeError):   # type: ignore
            head_commit = bios_repo.head.commit
            sha = f'{head_commit.hexsha[0:8]} from: {head_commit.committed_datetime} by: {head_commit.author}'
        LOG.debug(f"Checkout: {head_commit.hexsha} from: {head_commit.committed_datetime} | {head_commit.message} | by: {head_commit.author}")  # type: ignore
    else:
        head_commit = bios_repo.head.commit
        sha = f'{head_commit.hexsha[0:8]} from: {head_commit.committed_datetime}'
    return sha


def check_dcs_bios_entry(lua_dst_data: str, lua_dst_path: str, temp_dir: str) -> str:
    """
    Check DCS-BIOS entry in Export.lua file.

    :param lua_dst_data: content of Export.lua
    :param lua_dst_path: Export.lua path
    :param temp_dir: directory with DCS-BIOS archive
    :return: result of checks
    """
    result = '\n\nExport.lua exists.'
    lua = 'Export.lua'
    with open(file=path.join(temp_dir, lua), encoding='utf-8') as lua_src:
        lua_src_data = lua_src.read()
    export_re = search(r'dofile\(lfs.writedir\(\)\.\.\[\[Scripts\\DCS-BIOS\\BIOS\.lua\]\]\)', lua_dst_data)
    if not export_re:
        with open(file=path.join(lua_dst_path, lua), mode='a+',
                  encoding='utf-8') as exportlua_dst:
            exportlua_dst.write(f'\n{lua_src_data}')
        LOG.debug(f'Add DCS-BIOS to Export.lua: {lua_src_data}')
        result += '\n\nDCS-BIOS entry added.\n\nYou verify installation at:\ngithub.com/DCSFlightpanels/DCSFlightpanels/wiki/Installation'
    else:
        result += '\n\nDCS-BIOS entry detected.'
    return result
