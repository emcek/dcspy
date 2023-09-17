import json
import sys
import zipfile
from datetime import datetime
from glob import glob
from itertools import chain
from logging import getLogger
from os import environ, makedirs, walk
from pathlib import Path
from platform import python_implementation, python_version, uname
from pprint import pformat, pprint
from re import search
from shutil import rmtree
from subprocess import CalledProcessError, run
from tempfile import gettempdir
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union

import yaml
from packaging import version
from psutil import process_iter
from requests import get

from dcspy.models import CTRL_LIST_SEPARATOR, Control, ControlKeyData, DcsBios

try:
    import git
except ImportError:
    pass

LOG = getLogger(__name__)
__version__ = '2.4.0'
ConfigDict = Dict[str, Union[str, int, bool]]
CONFIG_YAML = 'config.yaml'
DEFAULT_YAML_FILE = Path(__file__).resolve().with_name(CONFIG_YAML)

with open(DEFAULT_YAML_FILE) as c_file:
    defaults_cfg: ConfigDict = yaml.load(c_file, Loader=yaml.FullLoader)
    defaults_cfg['dcsbios'] = f'D:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS'


def get_default_yaml(local_appdata=False) -> Path:
    """
    Return full path to default configuration file.

    :param local_appdata: if True C:/Users/<user_name>/AppData/Local is used
    :return: Path like object
    """
    cfg_ful_path = DEFAULT_YAML_FILE
    if local_appdata:
        localappdata = environ.get('LOCALAPPDATA', None)
        user_appdata = Path(localappdata) / 'dcspy' if localappdata else DEFAULT_YAML_FILE.parent
        makedirs(name=user_appdata, exist_ok=True)
        cfg_ful_path = Path(user_appdata / CONFIG_YAML).resolve()
        if not cfg_ful_path.exists():
            save_yaml(data=defaults_cfg, full_path=cfg_ful_path)
    return cfg_ful_path


class ReleaseInfo(NamedTuple):
    """Tuple to store release related information."""
    latest: bool
    ver: version.Version
    dl_url: str
    published: str
    release_type: str
    asset_file: str


def load_yaml(full_path: Path) -> Dict[str, Any]:
    """
    Load yaml from file into dictionary.

    :param full_path: full path to yaml file
    :return: dictionary
    """
    try:
        with open(file=full_path, encoding='utf-8') as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.FullLoader)
            if not isinstance(data, dict):
                data = {}
    except (FileNotFoundError, yaml.parser.ParserError) as err:
        makedirs(name=full_path.parent, exist_ok=True)
        LOG.warning(f'{type(err).__name__}: {full_path}.')
        LOG.debug(f'{err}')
        data = {}
    return data


def save_yaml(data: Dict[str, Any], full_path: Path) -> None:
    """
    Save disc as yaml file.

    :param data: dict
    :param full_path: full path to yaml file
    """
    with open(file=full_path, mode='w', encoding='utf-8') as yaml_file:
        yaml.dump(data, yaml_file)


def set_defaults(cfg: ConfigDict, filename: Path) -> ConfigDict:
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
    save_yaml(data=migrated_cfg, full_path=filename)
    LOG.debug(f'Save: {migrated_cfg}')
    return migrated_cfg


def check_ver_at_github(repo: str, current_ver: str, extension: str) -> ReleaseInfo:
    """
    Check version of <organization>/<package> at GitHub.

    Return tuple with:
    - result (bool) - if local version is latest
    - online version (version.Version) - the latest version
    - download url (str) - ready to download
    - published date (str) - format DD MMMM YYYY
    - release type (str) - Regular or Pre-release
    - asset file (str) - file name of asset

    :param repo: format '<organization or user>/<package>'
    :param current_ver: current local version
    :param extension: file extension to be returned
    :return: ReleaseInfo NamedTuple with information
    """
    latest, online_version, asset_url, published, pre_release = False, '0.0.0', '', '', False
    package = repo.split('/')[1]
    try:
        response = get(url=f'https://api.github.com/repos/{repo}/releases/latest', timeout=5)
        if response.ok:
            dict_json = response.json()
            online_version = dict_json['tag_name']
            pre_release = dict_json['prerelease']
            published = datetime.strptime(dict_json['published_at'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d %B %Y')
            asset_url = next(url for url in [asset['browser_download_url'] for asset in dict_json['assets']] if url.endswith(extension))
            LOG.debug(f'Latest GitHub version:{online_version} pre:{pre_release} date:{published} url:{asset_url}')
            latest = _compare_versions(package, current_ver, online_version)
        else:
            LOG.warning(f'Unable to check {package} version online. Try again later. Status={response.status_code}')
    except Exception as exc:
        LOG.warning(f'Unable to check {package} version online: {exc}')
    return ReleaseInfo(latest=latest,
                       ver=version.parse(online_version),
                       dl_url=asset_url,
                       published=published,
                       release_type='Pre-release' if pre_release else 'Regular',
                       asset_file=asset_url.split('/')[-1])


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

    :param repo: format '<organization or user>/<package>'.
    :param current_ver: current local version.
    :param check: version online.
    :return: formatted version as string.
    """
    ver_string = f'v{current_ver}'
    if check:
        result = check_ver_at_github(repo=repo, current_ver=current_ver, extension='')
        details = ''
        if result.latest:
            details = ' (latest)'
        elif str(result.ver) != '0.0.0':
            details = ' (update!)'
        elif str(result.ver) == '0.0.0':
            details = ' (failed)'
        ver_string = f'v{current_ver}{details}'
    return ver_string


def download_file(url: str, save_path: Path) -> bool:
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
        if name in proc.info['name']:  # type: ignore
            return proc.info['pid']  # type: ignore
    return 0


def check_dcs_ver(dcs_path: Path) -> Tuple[str, str]:
    """
    Check DCS version and release type.

    :param dcs_path: path to DCS installation directory
    :return: dcs type and version as strings
    """
    result_type, result_ver = 'Unknown', 'Unknown'
    try:
        with open(file=dcs_path / 'autoupdate.cfg', encoding='utf-8') as autoupdate_cfg:
            autoupdate_data = autoupdate_cfg.read()
    except (FileNotFoundError, PermissionError) as err:
        LOG.debug(f'{type(err).__name__}: {err.filename}')
    else:
        result_type = 'stable'
        dcs_type = search(r'"branch":\s"([\w.]*)"', autoupdate_data)
        if dcs_type:
            result_type = str(dcs_type.group(1))
        dcs_ver = search(r'"version":\s"([\d.]*)"', autoupdate_data)
        if dcs_ver:
            result_ver = str(dcs_ver.group(1))
    return result_type, result_ver


def check_bios_ver(bios_path: Union[Path, str]) -> ReleaseInfo:
    """
    Check DSC-BIOS release version.

    :param bios_path: path to DCS-BIOS directory in Saved Games folder
    :return: ReleaseInfo named tuple
    """
    result = ReleaseInfo(latest=False, ver=version.parse('0.0.0'), dl_url='', published='', release_type='', asset_file='')
    try:
        with open(file=Path(bios_path) / 'lib' / 'CommonData.lua', encoding='utf-8') as cd_lua:
            cd_lua_data = cd_lua.read()
    except FileNotFoundError as err:
        LOG.debug(f'While checking DCS-BIOS version {type(err).__name__}: {err.filename}')
    else:
        bios_re = search(r'function getVersion\(\)\s*return\s*\"([\d.]*)\"', cd_lua_data)
        if bios_re:
            bios = version.parse(bios_re.group(1))
            result = ReleaseInfo(latest=False, ver=bios, dl_url='', published='', release_type='', asset_file='')
    return result


def is_git_repo(dir_path: str) -> bool:
    """
    Check if dir_path ios Git repository.

    :param dir_path: path as string
    :return: true if dir is git repo
    """
    import git
    try:
        _ = git.Repo(dir_path).git_dir
        return True
    except (git.InvalidGitRepositoryError, git.exc.NoSuchPathError):
        return False


def check_github_repo(git_ref: str, update=True, repo='DCSFlightpanels/dcs-bios', repo_dir=Path(gettempdir()) / 'dcsbios_git') -> str:
    """
    Update DCS-BIOS git repository.

    Return SHA of latest commit.

    :param git_ref: any Git reference as string
    :param update: perform update process
    :param repo: GitHub repository
    :param repo_dir: local directory for repository
    """
    try:
        import git
    except ImportError:
        raise OSError('Git executable is not available!')

    bios_repo = _checkout_master(repo, repo_dir)
    if update:
        f_info = bios_repo.remotes[0].pull()
        LOG.debug(f'Pulled: {f_info[0].name} as: {f_info[0].commit}')
        try:
            bios_repo.git.checkout(git_ref)
            branch = bios_repo.active_branch.name
            head_commit = bios_repo.head.commit
            sha = f'{branch}: {head_commit.committed_datetime} by: {head_commit.author}'
        except (git.exc.GitCommandError, TypeError):  # type: ignore
            head_commit = bios_repo.head.commit
            sha = f'{head_commit.hexsha[0:8]} from: {head_commit.committed_datetime} by: {head_commit.author}'
        LOG.debug(f"Checkout: {head_commit.hexsha} from: {head_commit.committed_datetime} | by: {head_commit.author}\n{head_commit.message}")  # type: ignore
    else:
        bios_repo.git.checkout(git_ref)
        head_commit = bios_repo.head.commit
        sha = f'{head_commit.hexsha[0:8]} from: {head_commit.committed_datetime}'
    return sha


def _checkout_master(repo: str, repo_dir: Path) -> 'git.Repo':
    """
    Checkout repository at master branch or clone it when not exists in system.

    :param repo: repository name
    :param repo_dir: local repository directory
    :return: Repo object to repository
    """
    import git

    makedirs(name=repo_dir, exist_ok=True)
    if is_git_repo(str(repo_dir)):
        bios_repo = git.Repo(repo_dir)
        bios_repo.git.checkout('master')
    else:
        rmtree(path=repo_dir, ignore_errors=True)
        bios_repo = git.Repo.clone_from(url=f'https://github.com/{repo}.git', to_path=repo_dir)
    return bios_repo


def check_dcs_bios_entry(lua_dst_data: str, lua_dst_path: Path, temp_dir: Path) -> str:
    """
    Check DCS-BIOS entry in Export.lua file.

    :param lua_dst_data: content of Export.lua
    :param lua_dst_path: Export.lua path
    :param temp_dir: directory with DCS-BIOS archive
    :return: result of checks
    """
    result = '\n\nExport.lua exists.'
    lua = 'Export.lua'
    with open(file=temp_dir / lua, encoding='utf-8') as lua_src:
        lua_src_data = lua_src.read()
    export_re = search(r'dofile\(lfs.writedir\(\)\.\.\[\[Scripts\\DCS-BIOS\\BIOS\.lua\]\]\)', lua_dst_data)
    if not export_re:
        with open(file=lua_dst_path / lua, mode='a+', encoding='utf-8') as exportlua_dst:
            exportlua_dst.write(f'\n{lua_src_data}')
        LOG.debug(f'Add DCS-BIOS to Export.lua: {lua_src_data}')
        result += '\n\nDCS-BIOS entry added.\n\nYou verify installation at:\ngithub.com/DCSFlightpanels/DCSFlightpanels/wiki/Installation'
    else:
        result += '\n\nDCS-BIOS entry detected.'
    return result


def is_git_exec_present() -> bool:
    """
    Check if git executable is present in system.

    :return: True if git.exe is available
    """
    try:
        import git
        return bool(git.GIT_OK)
    except ImportError as err:
        LOG.debug(type(err).__name__, exc_info=True)
        return False


def is_git_object(repo_dir: Path, git_obj: str) -> bool:
    """
    Check if git_obj is valid Git reference.

    :param repo_dir: directory with repository
    :param git_obj: git reference to check
    :return: True if git_obj is git reference, False otherwise
    """
    import gitdb
    result = False
    if is_git_repo(str(repo_dir)):
        bios_repo = git.Repo(repo_dir)
        bios_repo.git.checkout('master')
        try:
            bios_repo.commit(git_obj)
            result = True
        except gitdb.exc.BadName:
            pass
    return result


def get_all_git_refs(repo_dir: Path) -> List[str]:
    """
    Get list of branches and tags for repo.

    :param repo_dir: directory with repository
    :return: list of git references as  strings
    """
    refs = []
    if is_git_repo(str(repo_dir)):
        for ref in chain(git.Repo(repo_dir).heads, git.Repo(repo_dir).tags):
            refs.append(str(ref))
    return refs


def collect_debug_data() -> Path:
    """
    Collect add zipp all data for troubleshooting.

    :return: Path object to zip file
    """
    aircrafts = ['FA18Chornet', 'Ka50', 'Ka503', 'Mi8MT', 'Mi24P', 'F16C50', 'F15ESE', 'AH64DBLKII', 'A10C', 'A10C2', 'F14A135GR', 'F14B', 'AV8BNA']
    localappdata = environ.get('LOCALAPPDATA', None)
    user_appdata = Path(localappdata) / 'dcspy' if localappdata else DEFAULT_YAML_FILE.parent
    config_file = Path(user_appdata / CONFIG_YAML).resolve()

    conf_dict = load_yaml(config_file)
    name = uname()
    pyver = (python_version(), python_implementation())
    pyexec = sys.executable
    dcs = check_dcs_ver(dcs_path=Path(str(conf_dict['dcs'])))
    bios_ver = check_bios_ver(bios_path=str(conf_dict['dcsbios'])).ver
    git_ver = (0, 0, 0, 0)
    head_commit = 'N/A'
    try:
        import git
        git_ver = git.cmd.Git().version_info
        head_commit = git.Repo(Path(gettempdir()) / 'dcsbios_git').head.commit
    except (git.exc.NoSuchPathError, ImportError):
        pass

    lgs_dir = '\n'.join([
        str(Path(dirpath) / filename)
        for dirpath, _, filenames in walk("C:\\Program Files\\Logitech Gaming Software\\SDK")
        for filename in filenames
    ])

    png_files = [
        Path(dirpath) / filename
        for dirpath, _, filenames in walk(gettempdir())
        for filename in filenames
        if any([True for aircraft in aircrafts if aircraft in filename and filename.endswith("png")])
    ]

    log_files = []
    for logfile in glob(str(Path(gettempdir()) / 'dcspy.log*')):
        log_files.append(Path(Path(gettempdir()) / logfile))
    sys_data = Path(gettempdir()) / 'system_data.txt'
    zip_file = Path(gettempdir()) / f'dcspy_debug_{str(datetime.now()).replace(" ", "_").replace(":", "")}.zip'

    with open(sys_data, 'w+') as debug_file:
        debug_file.write(f'{__version__=}\n{name=}\n{pyver=}\n{pyexec=}\n{dcs=}\n{bios_ver=}\n{git_ver=}\n{head_commit=}\n{lgs_dir}\ncfg={pformat(conf_dict)}')

    with zipfile.ZipFile(file=zip_file, mode='w', compresslevel=9, compression=zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(sys_data, arcname=sys_data.name)
        for log_file in log_files:
            zipf.write(log_file, arcname=log_file.name)
        zipf.write(config_file, arcname=config_file.name)
        for png in png_files:
            zipf.write(png, arcname=png.name)

    return zip_file


def run_pip_command(cmd: str) -> Tuple[int, str, str]:
    """
    Execute pip command.

    :param cmd: as string
    :return: tuple with return code, stderr and stdout
    """
    try:
        result = run([sys.executable, "-m", "pip", *cmd.split(' ')], capture_output=True, check=True)
        return result.returncode, result.stderr.decode('utf-8'), result.stdout.decode('utf-8')
    except CalledProcessError as e:
        LOG.debug(f'Result: {e}')
        return e.returncode, e.stderr.decode('utf-8'), e.stdout.decode('utf-8')


def load_json(path: Path) -> Dict[str, Any]:
    """
    Load json from file into dictionary.

    :param path: full path
    :return: dict
    """
    with open(path, encoding='utf-8') as json_file:
        data = json_file.read()
    return json.loads(data)


def get_full_bios_for_plane(name: str, bios_dir: Path) -> Dict[str, Any]:
    """
    Collect full BIOS for plane with name.

    :param name: BIOS plane name
    :param bios_dir: path to DCS-BIOS directory
    :return: dict
    """
    alias_path = bios_dir / 'doc' / 'json' / 'AircraftAliases.json'
    local_json: Dict[str, Any] = {}
    aircraft_aliases = load_json(path=alias_path)
    for json_file in aircraft_aliases[name]:
        local_json = {**local_json, **load_json(path=bios_dir / 'doc' / 'json' / f'{json_file}.json')}

    return local_json


def get_inputs_for_plane(name: str, bios_dir: Path) -> Dict[str, Dict[str, ControlKeyData]]:
    """
    Get dict with all not empty inputs for plane.

    :param name: BIOS plane name
    :param bios_dir: path to DCS-BIOS
    :return: dict.
    """
    ctrl_key: Dict[str, Dict[str, ControlKeyData]] = {}
    json_data = get_full_bios_for_plane(name=name, bios_dir=bios_dir)

    for section, controllers in json_data.items():
        ctrl_key[section] = {}
        for ctrl_name, ctrl_data in controllers.items():
            ctrl_input = Control.model_validate(ctrl_data).input
            if ctrl_input:
                ctrl_key[section][ctrl_name] = ctrl_input
        if not len(ctrl_key[section]):
            del ctrl_key[section]
    return ctrl_key


def get_list_of_ctrls(inputs: Dict[str, Dict[str, ControlKeyData]]) -> List[str]:
    """
    Get list of all controllers from dict with sections and inputs.

    :param inputs: dict with ControlKeyData
    :return: list of string
    """
    result_list = []
    for section, controllers in inputs.items():
        result_list.append(f'{CTRL_LIST_SEPARATOR} {section} {CTRL_LIST_SEPARATOR}')
        for ctrl_name in controllers:
            result_list.append(ctrl_name)
    return result_list


def get_planes_list(bios_dir: Path) -> List[str]:
    """
    Get list of all DCS-BIOS supported planes with clickable cockpit.

    :param bios_dir: path to DCS-BIOS
    :return: list of all supported planes
    """
    aircraft_aliases = get_plane_aliases(bios_dir=bios_dir, name=None)
    return [name for name, yaml_data in aircraft_aliases.items() if yaml_data not in (['CommonData', 'FC3'], ['CommonData'])]


def get_plane_aliases(bios_dir: Path, name: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Get list of all yaml files for plane with name.

    :param name: BIOS plane name
    :param bios_dir: path to DCS-BIOS
    :return: list of all yaml files for plane definition
    """
    alias_path = bios_dir / 'doc' / 'json' / 'AircraftAliases.json'
    aircraft_aliases = load_json(path=alias_path)
    if name:
        aircraft_aliases = {name: aircraft_aliases[name]}
    return aircraft_aliases


if __name__ == '__main__':
    bios_local_dir = Path('D:\\Users\\mplic\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS')
    plane_json = get_full_bios_for_plane('F-16C_50', bios_local_dir)
    DcsBios.model_validate(plane_json)
    print('*' * 100)
    pprint(plane_json, width=500)
    ctrl_inputs = get_inputs_for_plane('F-16C_50', bios_local_dir)
    print('*' * 100)
    pprint(ctrl_inputs, width=150)
    in_list = get_list_of_ctrls(ctrl_inputs)
    print('*' * 100)
    print(in_list)
