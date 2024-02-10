import json
import sys
import zipfile
from datetime import datetime
from functools import lru_cache
from glob import glob
from itertools import chain
from logging import getLogger
from os import environ, makedirs, walk
from pathlib import Path
from platform import python_implementation, python_version, uname
from pprint import pformat
from re import search, sub
from shutil import rmtree
from subprocess import CalledProcessError, run
from tempfile import gettempdir
from typing import Any, ClassVar, Dict, Generator, List, Optional, Sequence, Tuple, Union

import yaml
from packaging import version
from psutil import process_iter
from requests import get

from dcspy.models import CTRL_LIST_SEPARATOR, DCS_BIOS_REPO_DIR, ControlKeyData, DcsBiosPlaneData, DcspyConfigYaml, ReleaseInfo

try:
    import git
except ImportError:
    pass

LOG = getLogger(__name__)
__version__ = '3.1.4'
CONFIG_YAML = 'config.yaml'
DEFAULT_YAML_FILE = Path(__file__).resolve().with_name(CONFIG_YAML)

with open(DEFAULT_YAML_FILE) as c_file:
    defaults_cfg: DcspyConfigYaml = yaml.load(c_file, Loader=yaml.FullLoader)
    defaults_cfg['dcsbios'] = f'C:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS'


def get_default_yaml(local_appdata=False) -> Path:
    """
    Return full path to default configuration file.

    :param local_appdata: if True C:/Users/<user_name>/AppData/Local is used
    :return: Path like object
    """
    cfg_ful_path = DEFAULT_YAML_FILE
    if local_appdata:
        user_appdata = get_config_yaml_location()
        makedirs(name=user_appdata, exist_ok=True)
        cfg_ful_path = Path(user_appdata / CONFIG_YAML).resolve()
        if not cfg_ful_path.exists():
            save_yaml(data=defaults_cfg, full_path=cfg_ful_path)
    return cfg_ful_path


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
        LOG.warning(f'{type(err).__name__}: {full_path}.', exc_info=True)
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
    :param extension: file extension
    :return: ReleaseInfo with data
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
    return ReleaseInfo(
        latest=latest,
        ver=version.parse(online_version),
        dl_url=asset_url,
        published=published,
        release_type='Pre-release' if pre_release else 'Regular',
        asset_file=asset_url.split('/')[-1],
    )


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
        if name in proc.info['name']:  # type: ignore[attr-defined]
            return proc.info['pid']  # type: ignore[attr-defined]
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
        if dcs_type := search(r'"branch":\s"([\w.]*)"', autoupdate_data):
            result_type = str(dcs_type.group(1))
        if dcs_ver := search(r'"version":\s"([\d.]*)"', autoupdate_data):
            result_ver = str(dcs_ver.group(1))
    return result_type, result_ver


def check_bios_ver(bios_path: Union[Path, str]) -> ReleaseInfo:
    """
    Check DSC-BIOS release version.

    :param bios_path: path to DCS-BIOS directory in Saved Games folder
    :return: ReleaseInfo named tuple
    """
    result = ReleaseInfo(latest=False, ver=version.parse('0.0.0'), dl_url='', published='', release_type='', asset_file='')
    new_location = Path(bios_path) / 'lib' / 'modules' / 'common_modules' / 'CommonData.lua'
    old_location = Path(bios_path) / 'lib' / 'CommonData.lua'

    if new_location.is_file():
        with open(file=new_location, encoding='utf-8') as cd_lua:
            cd_lua_data = cd_lua.read()
    elif old_location.is_file():
        with open(file=old_location, encoding='utf-8') as cd_lua:
            cd_lua_data = cd_lua.read()
    else:
        cd_lua_data = ''
        LOG.debug(f'No `CommonData.lua` while checking DCS-BIOS version at {new_location.parent} or {old_location.parent}')

    if bios_re := search(r'function getVersion\(\)\s*return\s*\"([\d.]*)\"', cd_lua_data):
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


def check_github_repo(git_ref: str, update=True, repo='DCS-Skunkworks/dcs-bios', repo_dir=Path(gettempdir()) / 'dcsbios_git',
                      progress: Optional[git.RemoteProgress] = None) -> str:
    """
    Update DCS-BIOS git repository.

    Return SHA of latest commit.

    :param git_ref: any Git reference as string
    :param update: perform update process
    :param repo: GitHub repository
    :param repo_dir: local directory for repository
    :param progress: progress callback
    """
    try:
        import git
    except ImportError:
        raise OSError('Git executable is not available!')

    bios_repo = _checkout_repo(repo=repo, repo_dir=repo_dir, progress=progress)
    if update:
        f_info = bios_repo.remotes[0].pull(progress=progress)
        LOG.debug(f'Pulled: {f_info[0].name} as: {f_info[0].commit}')
        try:
            bios_repo.git.checkout(git_ref)
            branch = bios_repo.active_branch.name
            head_commit = bios_repo.head.commit
            sha = f'{branch}: {head_commit.committed_datetime} by: {head_commit.author}'
        except (git.exc.GitCommandError, TypeError):
            head_commit = bios_repo.head.commit
            sha = f'{head_commit.hexsha[0:8]} from: {head_commit.committed_datetime} by: {head_commit.author}'
        LOG.debug(f'Checkout: {head_commit.hexsha} from: {head_commit.committed_datetime} | by: {head_commit.author}\n{head_commit.message}')  # type: ignore
    else:
        bios_repo.git.checkout(git_ref)
        head_commit = bios_repo.head.commit
        sha = f'{head_commit.hexsha[0:8]} from: {head_commit.committed_datetime.strftime("%d-%b-%Y %H:%M:%S")}'
    return sha


def _checkout_repo(repo: str, repo_dir: Path, checkout_ref: str = 'master', progress: Optional[git.RemoteProgress] = None) -> 'git.Repo':
    """
    Checkout repository at master branch or clone it when not exists in system.

    :param repo: repository name
    :param repo_dir: local repository directory
    :param checkout_ref: git reference to checkout
    :param progress: progress callback
    :return: Repo object to repository
    """
    import git

    makedirs(name=repo_dir, exist_ok=True)
    if is_git_repo(str(repo_dir)):
        bios_repo = git.Repo(repo_dir)
        bios_repo.git.checkout(checkout_ref)
    else:
        rmtree(path=repo_dir, ignore_errors=True)
        bios_repo = git.Repo.clone_from(url=f'https://github.com/{repo}.git', to_path=repo_dir, progress=progress)  # type: ignore
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
    export_re = search(r'dofile\(lfs.writedir\(\)\s*\.\.\s*\[\[Scripts\\DCS-BIOS\\BIOS\.lua]]\)', lua_dst_data)
    if not export_re:
        with open(file=lua_dst_path / lua, mode='a+', encoding='utf-8') as exportlua_dst:
            exportlua_dst.write(f'\n{lua_src_data}')
        LOG.debug(f'Add DCS-BIOS to Export.lua: {lua_src_data}')
        result += '\n\nDCS-BIOS entry added.\n\nYou verify installation at:\ngithub.com/DCS-Skunkworks/DCSFlightpanels/wiki/Installation'
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
    import gitdb  # type: ignore[import-untyped]
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


def get_sha_for_current_git_ref(git_ref: str, repo='DCS-Skunkworks/dcs-bios', repo_dir=Path(gettempdir()) / 'dcsbios_git') -> str:
    """
    Get SHA for current git reference.

    :param git_ref: any Git reference as string
    :param repo: GitHub repository
    :param repo_dir: local directory for repository
    :return: Hex of SHA
    """
    bios_repo = _checkout_repo(repo=repo, repo_dir=repo_dir, checkout_ref=git_ref)
    head_commit = bios_repo.head.commit
    return head_commit.hexsha


class CloneProgress(git.RemoteProgress):
    """Handler providing an interface to parse progress information emitted by git."""
    OP_CODES: ClassVar[List[str]] = ['BEGIN', 'CHECKING_OUT', 'COMPRESSING', 'COUNTING', 'END', 'FINDING_SOURCES', 'RECEIVING', 'RESOLVING', 'WRITING']
    OP_CODE_MAP: ClassVar[Dict[int, str]] = {getattr(git.RemoteProgress, _op_code): _op_code for _op_code in OP_CODES}

    def __init__(self, progress, stage) -> None:
        """
        Initialize the progress handler.

        :param progress: progress Qt6 signal
        :param stage: report stage Qt6 signal
        """
        super().__init__()
        self.progress_signal = progress
        self.stage_signal = stage

    def get_curr_op(self, op_code: int) -> str:
        """
        Get stage name from OP code.

        :param op_code: OP code
        :return: stage name
        """
        op_code_masked = op_code & self.OP_MASK
        return self.OP_CODE_MAP.get(op_code_masked, '?').title()

    def update(self, op_code, cur_count, max_count=None, message=''):
        """
        Call whenever the progress changes.

        :param op_code: Integer allowing to be compared against Operation IDs and stage IDs.
        :param cur_count: Current absolute count of items
        :param max_count: The maximum count of items we expect. It may be None in case there is no maximum number of items or if it is (yet) unknown.
        :param message: It contains the amount of bytes transferred. It may possibly be used for other purposes as well.
        """
        if op_code & git.RemoteProgress.BEGIN:
            self.stage_signal.emit(f'Git clone: {self.get_curr_op(op_code)}')

        percentage = int(cur_count / max_count * 100) if max_count else 0
        self.progress_signal.emit(percentage)


def collect_debug_data() -> Path:
    """
    Collect and zip all data for troubleshooting.

    :return: Path object to zip file
    """
    config_file = Path(get_config_yaml_location() / CONFIG_YAML).resolve()
    conf_dict = load_yaml(config_file)
    sys_data = _get_sys_file(conf_dict)
    dcs_log = _get_dcs_log(conf_dict)

    zip_file = Path(gettempdir()) / f'dcspy_debug_{str(datetime.now()).replace(" ", "_").replace(":", "")}.zip'
    with zipfile.ZipFile(file=zip_file, mode='w', compresslevel=9, compression=zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(sys_data, arcname=sys_data.name)
        zipf.write(dcs_log, arcname=dcs_log.name)
        for log_file in _get_log_files():
            zipf.write(log_file, arcname=log_file.name)
        for yaml_file in _get_yaml_files(config_file):
            zipf.write(yaml_file, arcname=yaml_file.name)
        for png in _get_png_files():
            zipf.write(png, arcname=png.name)

    return zip_file


def _get_sys_file(conf_dict: Dict[str, Any]) -> Path:
    """
    Save system information to file and return its path.

    :param conf_dict: A dictionary containing configuration information.
    :return: A Path object representing the path to the system data file.
    """
    system_info = _fetch_system_info(conf_dict)
    sys_data = Path(gettempdir()) / 'system_data.txt'
    with open(sys_data, 'w+') as debug_file:
        debug_file.write(system_info)
    return sys_data


def _fetch_system_info(conf_dict: Dict[str, Any]) -> str:
    """
    Fetch system information.

    :param conf_dict: A dictionary containing configuration information.
    :return: system data as string
    """
    name = uname()
    pyver = (python_version(), python_implementation())
    pyexec = sys.executable
    dcs = check_dcs_ver(dcs_path=Path(str(conf_dict['dcs'])))
    bios_ver = check_bios_ver(bios_path=str(conf_dict['dcsbios'])).ver
    git_ver, head_commit = _fetch_git_data()
    lgs_dir = '\n'.join([
        str(Path(dirpath) / filename)
        for dirpath, _, filenames in walk('C:\\Program Files\\Logitech Gaming Software\\SDK')
        for filename in filenames
    ])
    return f'{__version__=}\n{name=}\n{pyver=}\n{pyexec=}\n{dcs=}\n{bios_ver=}\n{git_ver=}\n{head_commit=}\n{lgs_dir}\ncfg={pformat(conf_dict)}'


def _fetch_git_data() -> Tuple[Sequence[int], str]:
    """
    Fetch Git version and SHA of HEAD commit.

    :return: Tuple of (a version) and SHA of HEAD commit
    """
    try:
        import git
        git_ver = git.cmd.Git().version_info
        head_commit = str(git.Repo(DCS_BIOS_REPO_DIR).head.commit)
    except (git.exc.NoSuchPathError, ImportError):
        git_ver = (0, 0, 0, 0)
        head_commit = 'N/A'
    return git_ver, head_commit


def _get_dcs_log(conf_dict: Dict[str, Any]) -> Path:
    """
    Get path to dcs.log path.

    :param conf_dict: A dictionary containing configuration information.
    :return: A Path object representing the path to the dcs.log file.
    """
    dcs_log_file = Path(conf_dict['dcsbios']).parents[1] / 'Logs' / 'dcs.log'
    return dcs_log_file if dcs_log_file.is_file() else Path()


def _get_log_files() -> Generator[Path, None, None]:
    """
    Get path to all logg files.

    :return: generator of path to log files
    """
    return (
        Path(gettempdir()) / logfile
        for logfile in glob(str(Path(gettempdir()) / 'dcspy.log*'))
    )


def _get_yaml_files(config_file) -> Generator[Path, None, None]:
    """
    Get path to all configuration yaml files.

    :param config_file:
    :return: generator of path to yaml files
    """
    return (
        Path(dirpath) / filename
        for dirpath, _, filenames in walk(config_file.parent)
        for filename in filenames
        if filename.endswith('yaml')
    )


def _get_png_files() -> Generator[Path, None, None]:
    """
    Get path to png screenshots for all airplanes.

    :return: generator of path to png files
    """
    aircrafts = ['FA18Chornet', 'Ka50', 'Ka503', 'Mi8MT', 'Mi24P', 'F16C50', 'F15ESE',
                 'AH64DBLKII', 'A10C', 'A10C2', 'F14A135GR', 'F14B', 'AV8BNA']
    return (
        Path(dirpath) / filename
        for dirpath, _, filenames in walk(gettempdir())
        for filename in filenames
        if any(True for aircraft in aircrafts if aircraft in filename and filename.endswith('png'))
    )


def get_config_yaml_location() -> Path:
    """
    Get location of YAML configuration files.

    :rtype: Path object to directory
    """
    localappdata = environ.get('LOCALAPPDATA', None)
    user_appdata = Path(localappdata) / 'dcspy' if localappdata else DEFAULT_YAML_FILE.parent
    return user_appdata


def run_pip_command(cmd: str) -> Tuple[int, str, str]:
    """
    Execute pip command.

    :param cmd: as string
    :return: tuple with return code, stderr and stdout
    """
    try:
        result = run([sys.executable, '-m', 'pip', *cmd.split(' ')], capture_output=True, check=True)
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


@lru_cache
def get_full_bios_for_plane(plane: str, bios_dir: Path) -> DcsBiosPlaneData:
    """
    Collect full BIOS for plane with name.

    :param plane: BIOS plane name
    :param bios_dir: path to DCS-BIOS directory
    :return: dict
    """
    alias_path = bios_dir / 'doc' / 'json' / 'AircraftAliases.json'
    local_json: Dict[str, Any] = {}
    aircraft_aliases = load_json(path=alias_path)
    for json_file in aircraft_aliases[plane]:
        local_json = {**local_json, **load_json(path=bios_dir / 'doc' / 'json' / f'{json_file}.json')}

    return DcsBiosPlaneData.model_validate(local_json)


@lru_cache
def get_inputs_for_plane(plane: str, bios_dir: Path) -> Dict[str, Dict[str, ControlKeyData]]:
    """
    Get dict with all not empty inputs for plane.

    :param plane: BIOS plane name
    :param bios_dir: path to DCS-BIOS
    :return: dict.
    """
    plane_bios = get_full_bios_for_plane(plane=plane, bios_dir=bios_dir)
    inputs = plane_bios.get_inputs()
    return inputs


def get_list_of_ctrls(inputs: Dict[str, Dict[str, ControlKeyData]]) -> Dict[str, str]:
    """
    Get list of all controllers from dict with sections and inputs.

    :param inputs: dict with ControlKeyData
    :return: list of string
    """
    result_list = {}
    for section, controllers in inputs.items():
        # result_list.append(f'{CTRL_LIST_SEPARATOR} {section} {CTRL_LIST_SEPARATOR}')
        result_list[f'{CTRL_LIST_SEPARATOR} {section} {CTRL_LIST_SEPARATOR}'] = ''
        for ctrl_name, ctrl in controllers.items():
            # result_list.append(ctrl_name)
            result_list[ctrl_name] = ctrl.description
    return result_list


@lru_cache
def get_planes_list(bios_dir: Path) -> List[str]:
    """
    Get list of all DCS-BIOS supported planes with clickable cockpit.

    :param bios_dir: path to DCS-BIOS
    :return: list of all supported planes
    """
    aircraft_aliases = get_plane_aliases(bios_dir=bios_dir, plane=None)
    return [name for name, yaml_data in aircraft_aliases.items() if yaml_data not in (['CommonData', 'FC3'], ['CommonData'])]


@lru_cache
def get_plane_aliases(bios_dir: Path, plane: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Get list of all yaml files for plane with name.

    :param plane: BIOS plane name
    :param bios_dir: path to DCS-BIOS
    :return: list of all yaml files for plane definition
    """
    alias_path = bios_dir / 'doc' / 'json' / 'AircraftAliases.json'
    aircraft_aliases = load_json(path=alias_path)
    if plane:
        aircraft_aliases = {plane: aircraft_aliases[plane]}
    return aircraft_aliases


def substitute_symbols(value: str, symbol_replacement: Sequence[Sequence[str]]) -> str:
    """
    Substitute symbols in a string with specified replacements.

    :param value: The input string to be processed
    :param symbol_replacement: A list of symbol patterns and their corresponding replacements.
    :return: The processed string with symbols replaced according to the provided symbol_replacement list.
    """
    for pattern, replacement in symbol_replacement:
        value = sub(pattern, replacement, value)
    return value


def replace_symbols(value: str, symbol_replacement: Sequence[Sequence[str]]) -> str:
    """
    Replace symbols in a string with specified replacements.

    :param value: The string in which symbols will be replaced.
    :param symbol_replacement: A sequence of sequences containing the original symbols and their replacement strings.
    :return: The string with symbols replaced.
    """
    for original, replacement in symbol_replacement:
        value = value.replace(original, replacement)
    return value
