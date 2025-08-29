from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from collections.abc import Callable, Generator, Sequence
from datetime import datetime
from functools import lru_cache
from glob import glob
from itertools import chain
from logging import getLogger
from os import chdir, environ, getcwd, makedirs, walk
from pathlib import Path
from platform import python_implementation, python_version, uname
from pprint import pformat
from re import search, sub
from shutil import rmtree
from subprocess import CalledProcessError, run
from tempfile import gettempdir
from typing import Any, ClassVar

import yaml
from packaging import version
from PIL import ImageColor
from psutil import process_iter
from requests import get

from dcspy.models import (CONFIG_YAML, CTRL_LIST_SEPARATOR, DEFAULT_YAML_FILE, AnyButton, BiosValue, Color, ControlDepiction, ControlKeyData, DcsBiosPlaneData,
                          DcspyConfigYaml, Gkey, LcdButton, LcdMode, MouseButton, Release, RequestModel, __version__)

try:
    import git
except ImportError:
    pass

LOG = getLogger(__name__)

with open(DEFAULT_YAML_FILE) as c_file:
    defaults_cfg: DcspyConfigYaml = yaml.load(c_file, Loader=yaml.SafeLoader)
    defaults_cfg['dcsbios'] = f'C:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS\\Scripts\\DCS-BIOS'


def get_default_yaml(local_appdata: bool = False) -> Path:
    """
    Return a full path to the default configuration file.

    :param local_appdata: If True value C:/Users/<user_name>/AppData/Local is used
    :return: Path like an object
    """
    cfg_ful_path = DEFAULT_YAML_FILE
    if local_appdata:
        user_appdata = get_config_yaml_location()
        makedirs(name=user_appdata, exist_ok=True)
        cfg_ful_path = Path(user_appdata / CONFIG_YAML).resolve()
        if not cfg_ful_path.exists():
            save_yaml(data=defaults_cfg, full_path=cfg_ful_path)
    return cfg_ful_path


def load_yaml(full_path: Path) -> DcspyConfigYaml:
    """
    Load YAML from a file into a dictionary.

    :param full_path: Full path to YAML file
    :return: Dictionary with data
    """
    try:
        with open(file=full_path, encoding='utf-8') as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.SafeLoader)
            if not isinstance(data, dict):
                data = {}
    except (FileNotFoundError, yaml.parser.ParserError) as err:
        makedirs(name=full_path.parent, exist_ok=True)
        LOG.warning(f'{type(err).__name__}: {full_path}.', exc_info=True)
        LOG.debug(f'{err}')
        data = {}
    return data


def save_yaml(data: DcspyConfigYaml, full_path: Path) -> None:
    """
    Save disc as YAML file.

    :param data: Dictionary with data
    :param full_path: Full a path to YAML file
    """
    with open(file=full_path, mode='w', encoding='utf-8') as yaml_file:
        yaml.dump(data, yaml_file, Dumper=yaml.SafeDumper)


def check_ver_at_github(repo: str) -> Release:
    """
    Check a version of <organization>/<package> at GitHub.

    :param repo: Format '<organization or user>/<package>'
    :return: Release object with data
    """
    package = repo.split('/')[1]
    try:
        response = get(url=f'https://api.github.com/repos/{repo}/releases/latest', timeout=5)
        if response.ok:
            rel = Release(**response.json())
            LOG.debug(f'Latest GitHub release: {rel}')
            return rel
        else:
            raise ValueError(f'Try again later. Status={response.status_code}')
    except Exception as exc:
        raise ValueError(f'Unable to check {package} version online: {exc}')


def get_version_string(repo: str, current_ver: str | version.Version, check: bool = True) -> str:
    """
    Generate formatted string with version number.

    :param repo: Format '<organization or user>/<package>'.
    :param current_ver: String or Version object.
    :param check: Version online.
    :return: Formatted version as a string.
    """
    ver_string = f'v{current_ver}'
    if check:
        try:
            details = ''
            result = check_ver_at_github(repo=repo)
        except ValueError:
            return f'v{current_ver} (failed)'

        if result.is_latest(current_ver=current_ver):
            details = ' (latest)'
        elif result.version != version.parse('0.0.0'):
            details = ' (update!)'
            current_ver = result.version
        ver_string = f'v{current_ver}{details}'
    return ver_string


def download_file(url: str, save_path: Path, progress_fn: Callable[[int], None] | None = None) -> bool:
    """
    Download a file from URL and save to save_path.

    :param url: URL address
    :param save_path: full path to save
    :param progress_fn: a callable object to report download progress
    """
    response = get(url=url, stream=True, timeout=5)
    if response.ok:
        file_size = int(response.headers.get('Content-Length', 0))
        LOG.debug(f'File size: {file_size / (1024 * 1024):.2f} MB' if file_size else 'File size: Unknown')
        LOG.debug(f'Download file from: {url}')
        with open(save_path, 'wb+') as dl_file:
            downloaded = 0
            progress = 0
            for chunk in response.iter_content(chunk_size=1024):
                dl_file.write(chunk)
                downloaded += len(chunk)
                new_progress = int((downloaded / file_size) * 100)
                if progress_fn and new_progress == progress + 1:
                    progress = new_progress
                    progress_fn(progress)
            LOG.debug(f'Saved as: {save_path}')
            return True
    else:
        LOG.warning(f'Can not download from: {url}')
        return False


def proc_is_running(name: str) -> int:
    """
    Check if the process is running and return its PID.

    If the process name is not found, 0 (zero) is returned.
    :param name: Process name
    :return: PID as int
    """
    for proc in process_iter(['pid', 'name']):
        if name in proc.info['name']:
            return proc.info['pid']
    return 0


def check_dcs_ver(dcs_path: Path) -> str:
    """
    Check DCS version and release type.

    :param dcs_path: Path to DCS installation directory
    :return: DCS version as strings
    """
    result_ver = 'Unknown'
    try:
        with open(file=dcs_path / 'autoupdate.cfg', encoding='utf-8') as autoupdate_cfg:
            autoupdate_data = autoupdate_cfg.read()
    except (FileNotFoundError, PermissionError) as err:
        LOG.debug(f'{type(err).__name__}: {err.filename}')
    else:
        if dcs_ver := search(r'"version":\s"([\d.]*)"', autoupdate_data):
            result_ver = str(dcs_ver.group(1))
    return result_ver


def check_bios_ver(bios_path: Path | str) -> version.Version:
    """
    Check the DSC-BIOS release version.

    :param bios_path: Path to DCS-BIOS directory in the SavedGames folder
    :return: Version object
    """
    bios_ver = version.parse('0.0.0')
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
        bios_ver = version.parse(bios_re.group(1))
    return bios_ver


def is_git_repo(dir_path: str) -> bool:
    """
    Check if dir_path ios Git repository.

    :param dir_path: Path as string
    :return: True if dir is git repo
    """
    import git
    try:
        _ = git.Repo(dir_path).git_dir
        return True
    except (git.InvalidGitRepositoryError, git.exc.NoSuchPathError):
        return False


def _get_sha_hex_str(bios_repo: git.Repo, git_ref: str) -> str:
    """
    Return a string representing the commit hash, date, and author of the given Git reference in the provided repository.

    :param bios_repo: A Git repository object.
    :param git_ref: A string representing the Git reference (e.g., commit, branch, tag).
    :return: A string representing the commit hash, date, and author.
    """
    try:
        import git
    except ImportError:
        raise OSError('Git executable is not available!')
    try:
        bios_repo.git.checkout(git_ref)
        branch = bios_repo.active_branch.name
        head_commit = bios_repo.head.commit
        sha = f'{branch} from: {head_commit.committed_datetime.strftime("%d-%b-%Y %H:%M:%S")} by: {head_commit.author}'
    except (git.exc.GitCommandError, TypeError):
        head_commit = bios_repo.head.commit
        sha = f'{head_commit.hexsha[0:8]} from: {head_commit.committed_datetime.strftime("%d-%b-%Y %H:%M:%S")} by: {head_commit.author}'
    LOG.debug(f'Checkout: {head_commit.hexsha} from: {head_commit.committed_datetime} | by: {head_commit.author}\n{head_commit.message}')  # type: ignore
    return sha


def check_github_repo(git_ref: str, repo_dir: Path, repo: str, update: bool = True, progress: git.RemoteProgress | None = None) -> str:
    """
    Update git repository.

    Return SHA of the latest commit.

    :param git_ref: Any Git reference as a string
    :param repo_dir: Local directory for a repository
    :param repo: GitHub repository user/name
    :param update: Perform update process
    :param progress: Progress callback
    """
    bios_repo = _checkout_repo(repo=repo, repo_dir=repo_dir, progress=progress)
    if update:
        f_info = bios_repo.remotes[0].pull(progress=progress)
        LOG.debug(f'Pulled: {f_info[0].name} as: {f_info[0].commit}')
    sha = _get_sha_hex_str(bios_repo, git_ref)
    return sha


def _checkout_repo(repo: str, repo_dir: Path, progress: git.RemoteProgress | None = None) -> git.Repo:
    """
    Checkout repository at a main/master branch or clone it when not exists in a system.

    :param repo: Repository name
    :param repo_dir: Local repository directory
    :param progress: Progress callback
    :return: Repo object of the repository
    """
    import git

    makedirs(name=repo_dir, exist_ok=True)
    if is_git_repo(str(repo_dir)):
        bios_repo = git.Repo(repo_dir)
        all_refs = get_all_git_refs(repo_dir=repo_dir)
        checkout_ref = 'main' if 'main' in all_refs else 'master'
        bios_repo.git.checkout(checkout_ref)
    else:
        rmtree(path=repo_dir, ignore_errors=True)
        bios_repo = git.Repo.clone_from(url=f'https://github.com/{repo}.git', to_path=repo_dir, progress=progress)  # type: ignore[arg-type]
    return bios_repo


def check_dcs_bios_entry(lua_dst_data: str, lua_dst_path: Path, temp_dir: Path) -> str:
    """
    Check DCS-BIOS entry in Export.lua file.

    :param lua_dst_data: Content of Export.lua
    :param lua_dst_path: Export.lua path
    :param temp_dir: Directory with DCS-BIOS archive
    :return: Result of checks
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


def count_files(directory: Path, extension: str) -> int:
    """
    Count files with extension in a directory.

    :param directory: As Path object
    :param extension: File extension
    :return: Number of files
    """
    try:
        json_files = [f.name for f in directory.iterdir() if f.is_file() and f.suffix == f'.{extension}']
        LOG.debug(f'In: {directory} found {json_files} ')
        return len(json_files)
    except FileNotFoundError:
        LOG.debug(f'Wrong directory: {directory}')
        return -1


def is_git_exec_present() -> bool:
    """
    Check if the git executable is present in a system.

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
    Check if git_obj is a valid Git reference.

    :param repo_dir: Directory with repository
    :param git_obj: Git reference to check
    :return: True if git_obj is git reference, False otherwise
    """
    import gitdb  # type: ignore[import-untyped]
    result = False
    if is_git_repo(str(repo_dir)):
        bios_repo = git.Repo(repo_dir)
        try:
            bios_repo.commit(git_obj)
            result = True
        except (gitdb.exc.BadName, TypeError):
            pass
    return result


def get_all_git_refs(repo_dir: Path) -> list[str]:
    """
    Get a list of branches and tags for repo.

    :param repo_dir: Directory with a repository
    :return: List of git references as strings
    """
    refs = []
    if is_git_repo(str(repo_dir)):
        for ref in chain(git.Repo(repo_dir).heads, git.Repo(repo_dir).tags):
            refs.append(str(ref))
    return refs


class CloneProgress(git.RemoteProgress):
    """Handler providing an interface to parse progress information emitted by git."""
    OP_CODES: ClassVar[list[str]] = ['BEGIN', 'CHECKING_OUT', 'COMPRESSING', 'COUNTING', 'END', 'FINDING_SOURCES', 'RECEIVING', 'RESOLVING', 'WRITING']
    OP_CODE_MAP: ClassVar[dict[int, str]] = {getattr(git.RemoteProgress, _op_code): _op_code for _op_code in OP_CODES}

    def __init__(self, progress, stage) -> None:
        """
        Initialize the progress handler.

        :param progress: Progress Qt6 signal
        :param stage: Report stage Qt6 signal
        """
        super().__init__()
        self.progress_signal = progress
        self.stage_signal = stage

    def get_curr_op(self, op_code: int) -> str:
        """
        Get a stage name from OP code.

        :param op_code: OP code
        :return: stage name
        """
        op_code_masked = op_code & self.OP_MASK
        return self.OP_CODE_MAP.get(op_code_masked, '?').title()

    def update(self, op_code: int, cur_count, max_count=None, message: str = '') -> None:
        """
        Call whenever the progress changes.

        :param op_code: Integer allowing to be compared against Operation IDs and stage IDs.
        :param cur_count: A count of current absolute items
        :param max_count: The maximum count of items we expect. It may be None in case there is no maximum number of items or if it is (yet) unknown.
        :param message: It contains the number of bytes transferred. It may be used for other purposes as well.
        """
        if op_code & git.RemoteProgress.BEGIN:
            self.stage_signal.emit(f'Git clone: {self.get_curr_op(op_code)}')

        percentage = int(cur_count / max_count * 100) if max_count else 0
        self.progress_signal.emit(percentage)


def collect_debug_data() -> Path:
    """
    Collect and zip all data for troubleshooting.

    :return: Path object to ZIP file
    """
    config_file = Path(get_config_yaml_location() / CONFIG_YAML).resolve()
    conf_dict = load_yaml(config_file)
    sys_data = _get_sys_file(conf_dict)
    dcs_log = _get_dcs_log(conf_dict)

    zip_file = Path(gettempdir()) / f'dcspy_debug_{str(datetime.now()).replace(" ", "_").replace(":", "")}.zip'
    with zipfile.ZipFile(file=zip_file, mode='w', compresslevel=9, compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(sys_data, arcname=sys_data.name)
        archive.write(dcs_log, arcname=dcs_log.name)
        for log_file in _get_log_files():
            archive.write(log_file, arcname=log_file.name)
        for yaml_file in _get_yaml_files(config_file):
            archive.write(yaml_file, arcname=yaml_file.name)
        for png in _get_png_files():
            archive.write(png, arcname=png.name)

    return zip_file


def _get_sys_file(conf_dict: dict[str, Any]) -> Path:
    """
    Save system information to a file and return its path.

    :param conf_dict: A dictionary containing configuration information.
    :return: A Path object representing the path to the system data file.
    """
    system_info = _fetch_system_info(conf_dict)
    sys_data = Path(gettempdir()) / 'system_data.txt'
    with open(sys_data, 'w+') as debug_file:
        debug_file.write(system_info)
    return sys_data


def _fetch_system_info(conf_dict: dict[str, Any]) -> str:
    """
    Fetch system information.

    :param conf_dict: A dictionary containing configuration information.
    :return: System data as a string
    """
    name = uname()
    pyver = (python_version(), python_implementation())
    pyexec = sys.executable
    dcs = check_dcs_ver(dcs_path=Path(str(conf_dict['dcs'])))
    bios_ver = check_bios_ver(bios_path=str(conf_dict['dcsbios']))
    repo_dir = Path(str(conf_dict['dcsbios'])).parents[1] / 'dcs-bios'
    git_ver, head_commit = _fetch_git_data(repo_dir=repo_dir)
    lgs_dir = '\n'.join([
        str(Path(dir_path) / filename)
        for dir_path, _, filenames in walk('C:\\Program Files\\Logitech Gaming Software\\SDK')
        for filename in filenames
    ])
    return f'{__version__=}\n{name=}\n{pyver=}\n{pyexec=}\n{dcs=}\n{bios_ver=}\n{git_ver=}\n{head_commit=}\n{lgs_dir}\ncfg={pformat(conf_dict)}'


def _fetch_git_data(repo_dir: Path) -> tuple[Sequence[int], str]:
    """
    Fetch the Git version and SHA of HEAD commit.

    :param repo_dir: Local directory for repository
    :return: Tuple of (a version) and SHA of HEAD commit
    """
    try:
        import git
        git_ver = git.cmd.Git().version_info
        head_commit = str(git.Repo(repo_dir).head.commit)
    except (git.exc.NoSuchPathError, git.exc.InvalidGitRepositoryError, ImportError):
        git_ver = (0, 0, 0, 0)
        head_commit = 'N/A'
    return git_ver, head_commit


def _get_dcs_log(conf_dict: dict[str, Any]) -> Path:
    """
    Get a path to dcs.log path.

    :param conf_dict: A dictionary containing configuration information.
    :return: A Path object representing the path to the dcs.log file.
    """
    dcs_log_file = Path(conf_dict['dcsbios']).parents[1] / 'Logs' / 'dcs.log'
    return dcs_log_file if dcs_log_file.is_file() else Path()


def _get_log_files() -> Generator[Path]:
    """
    Get a path to all logg files.

    :return: Generator of a path to log files
    """
    return (
        Path(gettempdir()) / logfile
        for logfile in glob(str(Path(gettempdir()) / 'dcspy.log*'))
    )


def _get_yaml_files(config_file: Path) -> Generator[Path]:
    """
    Get a path to all configuration YAML files.

    :param config_file: Path to the config file
    :return: Generator of a path to YAML files
    """
    return (
        Path(dirpath) / filename
        for dirpath, _, filenames in walk(config_file.parent)
        for filename in filenames
        if filename.endswith('yaml')
    )


def _get_png_files() -> Generator[Path]:
    """
    Get a path to png screenshots for all airplanes.

    :return: Generator of a path to png files
    """
    aircrafts = ['FA18Chornet', 'Ka50', 'Ka503', 'Mi8MT', 'Mi24P', 'F16C50', 'F15ESE',
                 'AH64DBLKII', 'A10C', 'A10C2', 'F14A135GR', 'F14B', 'AV8BNA']
    return (
        Path(dir_path) / filename
        for dir_path, _, filenames in walk(gettempdir())
        for filename in filenames
        if any(True for aircraft in aircrafts if aircraft in filename and filename.endswith('png'))
    )


def get_config_yaml_location() -> Path:
    """
    Get a location of YAML configuration files.

    :rtype: Path object to directory
    """
    localappdata = environ.get('LOCALAPPDATA', None)
    user_appdata = Path(localappdata) / 'dcspy' if localappdata else DEFAULT_YAML_FILE.parent
    return user_appdata


def run_command(cmd: Sequence[str], cwd: Path | None = None) -> int:
    """
    Run command in shell as a subprocess.

    :param cmd: The command to be executed as a sequence of strings
    :param cwd: current working directory
    :return: The return code of command
    """
    try:
        proc = run(cmd, check=True, shell=False, cwd=cwd)
        return proc.returncode
    except CalledProcessError as e:
        LOG.debug(f'Result: {e}')
        return -1


def load_json(full_path: Path) -> dict[Any, Any]:
    """
    Load JSON from a file into a dictionary.

    :param full_path: Full path
    :return: Python representation of JSON
    """
    with open(full_path, encoding='utf-8') as json_file:
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
    local_json: dict[str, Any] = {}
    aircraft_aliases = load_json(full_path=alias_path)
    for json_file in aircraft_aliases[plane]:
        local_json = {**local_json, **load_json(full_path=bios_dir / 'doc' / 'json' / f'{json_file}.json')}

    return DcsBiosPlaneData.model_validate(local_json)


@lru_cache
def get_inputs_for_plane(plane: str, bios_dir: Path) -> dict[str, dict[str, ControlKeyData]]:
    """
    Get dict with all not empty inputs for plane.

    :param plane: BIOS plane name
    :param bios_dir: path to DCS-BIOS
    :return: dict.
    """
    plane_bios = get_full_bios_for_plane(plane=plane, bios_dir=bios_dir)
    inputs = plane_bios.get_inputs()
    return inputs


def get_list_of_ctrls(inputs: dict[str, dict[str, ControlKeyData]]) -> list[str]:
    """
    Get a list of all controllers from dict with sections and inputs.

    :param inputs: Dictionary with ControlKeyData
    :return: List of string
    """
    result_list = []
    for section, controllers in inputs.items():
        result_list.append(f'{CTRL_LIST_SEPARATOR} {section} {CTRL_LIST_SEPARATOR}')
        for ctrl_name in controllers:
            result_list.append(ctrl_name)
    return result_list


@lru_cache
def get_planes_list(bios_dir: Path) -> list[str]:
    """
    Get a list of all DCS-BIOS supported planes with clickable cockpit.

    :param bios_dir: Path to DCS-BIOS
    :return: List of all supported planes
    """
    aircraft_aliases = get_plane_aliases(bios_dir=bios_dir, plane=None)
    return [name for name, yaml_data in aircraft_aliases.items() if yaml_data not in (['CommonData', 'FC3'], ['CommonData'])]


@lru_cache
def get_plane_aliases(bios_dir: Path, plane: str | None = None) -> dict[str, list[str]]:
    """
    Get a list of all YAML files for plane with name.

    :param plane: BIOS plane name
    :param bios_dir: path to DCS-BIOS
    :return: list of all YAML files for plane definition
    """
    alias_path = bios_dir / 'doc' / 'json' / 'AircraftAliases.json'
    aircraft_aliases = load_json(full_path=alias_path)
    if plane:
        aircraft_aliases = {plane: aircraft_aliases[plane]}
    return aircraft_aliases


def get_depiction_of_ctrls(inputs: dict[str, dict[str, ControlKeyData]]) -> dict[str, ControlDepiction]:
    """
    Get the depiction of controls.

    :param inputs: Dictionary with ControlKeyData
    :return: A dictionary containing the depiction of controls.
    """
    result = {}
    for section, controllers in inputs.items():
        for ctrl_name, ctrl in controllers.items():
            result[ctrl_name] = ctrl.depiction
    return result


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
    :return: The string with symbols to replace.
    """
    for original, replacement in symbol_replacement:
        value = value.replace(original, replacement)
    return value


def _try_key_instance(klass: type[Gkey] | type[LcdButton] | type[MouseButton], method: str, key_str: str) -> AnyButton | None:
    """
    Attempt to invoke a method on a class with a given key string.

    The method will first attempt to call the provided method with the `key_str` as a parameter.
    If there is a TypeError (indicating the method does not support a parameter), it attempts to call
    the method without arguments.
    If the method is missing or the call fails due to a ValueError or AttributeError, the function returns None.

    :param klass: The class type on which the method is to be invoked.
    :param method: The name of the method to call on the class.
    :param key_str: A string key to be passed as a parameter to the method, if supported.
    :return: An instance of `AnyButton` from the invoked method, if successful, otherwise None.
    """
    try:
        return getattr(klass, method)(key_str)
    except TypeError:
        return getattr(klass, method)
    except (ValueError, AttributeError):
        return None


def get_key_instance(key_str: str) -> AnyButton:
    """
    Resolve the provided key string into an instance of a valid key class based on a predefined set of classes and their respective resolution methods.

    If the key string matches a class method's criteria, it returns the resolved key instance.
    If no match is found, an exception is raised.

    :param key_str: A string representing the name or identifier of the key to be resolved into a key instance (e.g., Gkey, LcdButton, or MouseButton).
    :return: An instance of a class (AnyButton) that corresponds to the provided key string, if successfully resolved.
    :raises AttributeError: If the provided key string cannot be resolved into a valid key instance using the predefined classes and methods.
    """
    for klass, method in [(Gkey, 'from_yaml'), (MouseButton, 'from_yaml'), (LcdButton, key_str)]:
        key_instance = _try_key_instance(klass=klass, method=method, key_str=key_str)
        if key_instance:
            return key_instance
    raise AttributeError(f'Could not resolve "{key_str}" to a Gkey/LcdButton/MouseButton instance')


class KeyRequest:
    """Map LCD button or G-Key with an abstract request model."""

    def __init__(self, yaml_path: Path, get_bios_fn: Callable[[str], BiosValue]) -> None:
        """
        Load YAML with BIOS request for G-Keys and LCD buttons.

        :param yaml_path: Path to the airplane YAML file.
        :param get_bios_fn: Function used to get a current BIOS value.
        """
        plane_yaml = load_yaml(full_path=yaml_path)
        self.buttons: dict[AnyButton, RequestModel] = {}
        for key_str, request in plane_yaml.items():
            if request:
                key = get_key_instance(key_str)
                self.buttons[key] = RequestModel.from_request(key=key, request=request, get_bios_fn=get_bios_fn)

    @property
    def cycle_button_ctrl_name(self) -> dict[str, int]:
        """Return a dictionary with BIOS selectors to track changes of values for a cycle button to get current values."""
        return {req_model.ctrl_name: int() for req_model in self.buttons.values() if req_model.is_cycle}

    def get_request(self, button: AnyButton) -> RequestModel:
        """
        Get abstract representation for request ti be sent for requested button.

        :param button: LcdButton, Gkey or MouseButton
        :return: RequestModel object
        """
        return self.buttons.get(button, RequestModel.make_empty(key=button))

    def set_request(self, button: AnyButton, req: str) -> None:
        """
        Update the internal string request for the specified button.

        :param button: LcdButton, Gkey or MouseButton
        :param req: The raw request to set.
        """
        self.buttons[button].raw_request = req


def generate_bios_jsons_with_lupa(dcs_save_games: Path, local_compile='./Scripts/DCS-BIOS/test/compile/LocalCompile.lua') -> None:
    r"""
    Regenerate DCS-BIOS JSON files.

    Using the Lupa library, first it will try to use LuaJIT 2.1 if not it will fall back to Lua 5.1

    :param dcs_save_games: Full path to the Saved Games\DCS directory.
    :param local_compile: Relative path to the LocalCompile.lua file.
    """
    try:
        import lupa.luajit21 as lupa
    except ImportError:
        try:
            import lupa.lua51 as lupa  # type: ignore[no-redef]
        except ImportError:
            return

    previous_dir = getcwd()
    try:
        chdir(dcs_save_games)
        LOG.debug(f"Changed to: {dcs_save_games}")
        lua = lupa.LuaRuntime()
        LOG.debug(f"Using {lupa.LuaRuntime().lua_implementation} (compiled with {lupa.LUA_VERSION})")
        with open(local_compile) as lua_file:
            lua_script = lua_file.read()
        lua.execute(lua_script)
    finally:
        chdir(previous_dir)
        LOG.debug(f"Change directory back to: {getcwd()}")


def rgba(c: Color, /, mode: LcdMode | int = LcdMode.TRUE_COLOR) -> tuple[int, ...] | int:
    """
    Convert a color to a single integer or tuple of integers.

    This depends on a given mode/alpha channel:
    * If a mode is an integer, then return a tuple of RGBA channels.
    * If a mode is a LcdMode.TRUE_COLOR, then return a tuple of RGBA channels.
    * If a mode is a LcdMode.BLACK_WHITE, then return a single integer.

    :param c: Color name to convert
    :param mode: Mode of the LCD or alpha channel as an integer
    :return: tuple with RGBA channels or single integer
    """
    if isinstance(mode, int):
        return *rgb(c), mode
    else:
        return ImageColor.getcolor(color=c.name, mode=mode.value)


def rgb(c: Color, /) -> tuple[int, int, int]:
    """
    Convert a Color instance to its RGB components as a tuple of integers.

    The function extracts the red, green, and blue components from the
    color's value, which is expected to be a single integer representing
    a 24-bit RGB color.

    :param c: An instance of Color, whose value is a 24-bit RGB integer.
    :return: A tuple containing the red, green, and blue components.
    """
    red = (c.value >> 16) & 0xff
    green = (c.value >> 8) & 0xff
    blue = c.value & 0xff
    return red, green, blue


def detect_system_color_mode() -> str:
    """
    Detect the color mode of the system.

    Registry will return 0 if Windows is in Dark Mode and 1 if Windows is in Light Mode.
    In case of error, it will return 'light' as default.

    :return: Dark or light as string
    """
    from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx  # type: ignore[attr-defined]

    try:
        key = OpenKey(HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize')
        subkey = QueryValueEx(key, 'AppsUseLightTheme')[0]
    except (OSError, IndexError):
        return 'Light'
    return {0: 'Dark', 1: 'Light'}[subkey]

def verify_hashes(file_path: Path, digest_file: Path) -> tuple[bool, dict[str, bool]]:
    """
    Check hashes for a file.

    :param file_path: Path to the file
    :param digest_file: Path to the digests file
    :return: Overall verdict and detailed results
    """
    if not file_path.is_file() or not digest_file.is_file():
        return False, {}

    with open(digest_file) as f_digests:
        all_digests = f_digests.readlines()

    hashes: dict[str, dict[str, str]] = {}
    for line in all_digests:
        if line.startswith('#HASH'):
            hash_type = line.split()[1]
        elif line.strip():
            hash_and_file = line.split()
            filename = hash_and_file[1] if len(hash_and_file) > 1 else ''
            hashes.setdefault(filename, {})[hash_type] = hash_and_file[0]
    LOG.debug(f'Supported algorithms are: {hashlib.algorithms_guaranteed}')
    results = _compute_hash_and_check_file(file_path=file_path, hashes=hashes)

    return all(results.values()), results


def _compute_hash_and_check_file(file_path: Path, hashes: dict[str, dict[str, str]]) -> dict[str, bool]:
    """
    Compute and verify hashes for a file.

    :param file_path: Path for file to chack hashes
    :param hashes: Dictionary of hash types and values
    :return: Dictionary of verification results
    """
    result = {}
    for hash_type, hash_value in hashes.get(file_path.name, {}).items():
        try:
            with open(file_path, 'rb') as f_path:
                if sys.version_info.minor > 10:
                    computed_hash = hashlib.file_digest(f_path, hash_type).hexdigest()
                else:
                    h = hashlib.new(hash_type)
                    h.update(f_path.read())
                    computed_hash = h.hexdigest()
        except ValueError:
            computed_hash = ''
            # todo: why there is diffrent hashes for sha1 and md5 on linux
        result[hash_type] = (computed_hash == hash_value)
    return result
