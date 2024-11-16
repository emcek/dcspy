from os import environ, makedirs
from pathlib import Path
from sys import platform
from unittest.mock import MagicMock, PropertyMock, mock_open, patch

from packaging import version
from pytest import mark, raises

from dcspy import utils
from dcspy.models import DEFAULT_FONT_NAME, get_key_instance


def test_check_ver_can_not_check():
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=False)
        with raises(ValueError):
            utils.check_ver_at_github(repo='fake2/package2')


def test_check_ver_exception():
    with patch.object(utils, 'get', side_effect=Exception('Connection error')):
        with raises(ValueError):
            utils.check_ver_at_github(repo='fake3/package3')

@mark.parametrize('current_ver, extension, file_name, result', [
    ('3.6.1', 'tar.gz', 'dcspy', {'latest': True, 'dl_url': 'https://github.com/emcek/dcspy/releases/download/v3.6.1/dcspy-3.6.1.tar.gz'}),
    ('3.5.0', 'exe', 'dcspy_cli', {'latest': False, 'dl_url': 'https://github.com/emcek/dcspy/releases/download/v3.6.1/dcspy_cli.exe'}),
    ('3.6.1', 'exe', 'fake', {'latest': True, 'dl_url': ''}),
    ('3.5.0', 'jpg', 'dcspy', {'latest': False, 'dl_url': ''}),
], ids=['latest', 'not latest', 'fake file', 'fake ext'])
def test_new_check_ver_at_github(current_ver, extension, file_name, result, resources):
    import json
    with open(resources / 'dcspy_3.6.1.json', encoding='utf-8') as json_file:
        content = json_file.read()
    json_data = json.loads(content)

    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=True)
        type(response_get.return_value).json = MagicMock(return_value=json_data)
        rel = utils.check_ver_at_github(repo='emcek/dcspy')
        assert rel.is_latest(current_ver=current_ver) == result['latest']
        assert rel.version == version.parse('3.6.1')
        assert rel.download_url(extension=extension, file_name=file_name) == result['dl_url']
        assert rel.published == '05 November 2024'


@mark.parametrize('current_ver, result', [
    ('3.6.1', 'v3.6.1 (latest)'),
    ('1.1.1', 'v3.6.1 (update!)')
], ids=['No update', 'New version'])
def test_get_version_string_is_possible(current_ver, result, resources):
    import json
    with open(resources / 'dcspy_3.6.1.json', encoding='utf-8') as json_file:
        content = json_file.read()
    json_data = json.loads(content)

    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=True)
        type(response_get.return_value).json = MagicMock(return_value=json_data)
        assert utils.get_version_string(repo='emcek/dcspy', current_ver=current_ver, check=True) == result


def test_get_version_string_without_checking():
    assert utils.get_version_string(repo='fake4/package4', current_ver=version.parse('4.4.4'), check=False) == 'v4.4.4'


def test_get_version_string_exception():
    with patch.object(utils, 'get', side_effect=Exception('Connection error')):
        assert utils.get_version_string(repo='fake4/package4', current_ver=version.parse('4.4.4'), check=True) == 'v4.4.4 (failed)'


@mark.parametrize('response, result', [(False, False), (True, True)], ids=['Download failed', 'Download success'])
def test_download_file(response, result, tmp_path):
    dl_file = tmp_path / 'tmp.txt'
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=response)
        type(response_get.return_value).iter_content = MagicMock(return_value=[b'1', b'0', b'0', b'1'])
        assert utils.download_file('https://test.com', dl_file) is result


@mark.slow
def test_proc_is_running():
    assert utils.proc_is_running('python')
    assert not utils.proc_is_running('wrong_python')


def test_dummy_save_load_migrate(tmpdir):
    from dcspy.migration import migrate
    test_tmp_yaml = Path(tmpdir) / 'test_cfg.yaml'

    utils.save_yaml(data={'font_mono_s': 9}, full_path=test_tmp_yaml)
    d_cfg = utils.load_yaml(full_path=test_tmp_yaml)
    assert d_cfg == {'font_mono_s': 9}
    d_cfg = migrate(cfg=d_cfg)
    assert d_cfg == {
        'api_ver': '3.6.1',
        'device': 'G13',
        'save_lcd': False,
        'show_gui': True,
        'autostart': False,
        'completer_items': 20,
        'current_plane': 'A-10C',
        'dcsbios': f'C:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
        'dcs': 'C:/Program Files/Eagle Dynamics/DCS World OpenBeta',
        'verbose': False,
        'check_bios': True,
        'check_ver': True,
        'font_name': DEFAULT_FONT_NAME,
        'font_mono_m': 9,
        'font_mono_s': 9,
        'font_mono_l': 16,
        'font_color_m': 22,
        'font_color_s': 18,
        'font_color_l': 32,
        'f16_ded_font': True,
        'git_bios': True,
        'toolbar_area': 4,
        'toolbar_style': 0,
        'git_bios_ref': 'master',
        'gkeys_area': 2,
        'gkeys_float': False,
    }
    with open(test_tmp_yaml, 'w+') as f:
        f.write('')
    d_cfg = utils.load_yaml(full_path=test_tmp_yaml)
    assert len(d_cfg) == 0


def test_check_dcs_ver_file_exists_with_ver(autoupdate1_cfg):
    with patch('dcspy.utils.open', mock_open(read_data=autoupdate1_cfg)):
        dcs_ver = utils.check_dcs_ver(Path(''))
        assert dcs_ver == ('openbeta', '2.7.16.28157')


def test_check_dcs_ver_file_exists_without_ver(autoupdate2_cfg):
    with patch('dcspy.utils.open', mock_open(read_data=autoupdate2_cfg)):
        dcs_ver = utils.check_dcs_ver(Path(''))
        assert dcs_ver == ('openbeta', 'Unknown')


def test_check_dcs_ver_file_exists_without_branch(autoupdate3_cfg):
    with patch('dcspy.utils.open', mock_open(read_data=autoupdate3_cfg)):
        dcs_ver = utils.check_dcs_ver(Path(''))
        assert dcs_ver == ('stable', '2.7.18.28157')


@mark.parametrize('side_effect', [FileNotFoundError, PermissionError])
def test_check_dcs_ver_file_not_exists(side_effect):
    with patch('dcspy.utils.open', side_effect=side_effect):
        dcs_ver = utils.check_dcs_ver(Path(''))
        assert dcs_ver == ('Unknown', 'Unknown')


def test_check_bios_ver_new_location(tmpdir):
    makedirs(Path(tmpdir) / 'lib' / 'modules' / 'common_modules')
    common_data_lua = Path(tmpdir) / 'lib' / 'modules' / 'common_modules' / 'CommonData.lua'
    with open(file=common_data_lua, encoding='utf-8', mode='w+') as cd_lua:
        cd_lua.write('local function getVersion()\n\treturn "1.2.3"\nend')
    result = utils.check_bios_ver(bios_path=tmpdir)
    assert result == version.parse('1.2.3')


def test_check_bios_ver_old_location(tmpdir):
    makedirs(Path(tmpdir) / 'lib')
    common_data_lua = Path(tmpdir) / 'lib' / 'CommonData.lua'
    with open(file=common_data_lua, encoding='utf-8', mode='w+') as cd_lua:
        cd_lua.write('local function getVersion()\n\treturn "3.2.1"\nend')
    result = utils.check_bios_ver(bios_path=tmpdir)
    assert result == version.parse('3.2.1')


def test_check_bios_ver_empty_lua(tmpdir):
    makedirs(Path(tmpdir) / 'lib' / 'modules' / 'common_modules')
    common_data_lua = Path(tmpdir) / 'lib' / 'modules' / 'common_modules' / 'CommonData.lua'
    with open(file=common_data_lua, encoding='utf-8', mode='w+') as cd_lua:
        cd_lua.write('')
    result = utils.check_bios_ver(bios_path=tmpdir)
    assert result == version.parse('0.0.0')


def test_check_bios_ver_lue_not_exists(tmpdir):
    result = utils.check_bios_ver(bios_path=tmpdir)
    assert result == version.parse('0.0.0')


def test_is_git_repo(tmpdir):
    from git import Repo
    assert utils.is_git_repo(tmpdir) is False
    assert utils.is_git_repo(tmpdir / 'new') is False
    Repo.init(tmpdir)
    assert utils.is_git_repo(tmpdir) is True


def test_is_git_exec_present():
    assert utils.is_git_exec_present() is True


@mark.slow
def test_check_github_repo(tmpdir):
    from re import search
    sha = utils.check_github_repo(git_ref='master', update=True, repo='emcek/common_sense', repo_dir=tmpdir)
    match = search(r'(master)\sfrom:\s\d{2}-\w{3}-\d{4}\s\d{2}:\d{2}:\d{2}\sby:\s.*', sha)
    assert match.group(1) == 'master'
    sha = utils.check_github_repo(git_ref='branch', update=True, repo='emcek/common_sense', repo_dir=tmpdir)
    match = search(r'([0-9a-f]{8})\sfrom:\s\d{2}-\w{3}-\d{4}\s\d{2}:\d{2}:\d{2}\sby:\s.*', sha)
    assert match.group(1)


@mark.slow
def test_is_git_object(tmpdir):
    utils.check_github_repo(git_ref='master', update=True, repo='emcek/common_sense', repo_dir=tmpdir)
    assert utils.is_git_object(repo_dir=tmpdir, git_obj='master') is True
    assert utils.is_git_object(repo_dir=tmpdir, git_obj='wrong') is False
    assert utils.is_git_object(repo_dir=Path('/'), git_obj='master') is False


@mark.slow
def test_get_all_git_refs(tmpdir):
    utils.check_github_repo(git_ref='master', update=True, repo='emcek/common_sense', repo_dir=tmpdir)
    assert utils.get_all_git_refs(repo_dir=tmpdir) == ['master']


def test_check_dcs_bios_entry_no_entry(tmpdir):
    install_dir = tmpdir / 'install'
    makedirs(install_dir)
    lua = 'Export.lua'
    lua_dst_data = ''

    with open(file=tmpdir / lua, mode='a+', encoding='utf-8') as lua_from_zip:
        lua_from_zip.write('anything')
    with open(file=install_dir / lua, mode='a+', encoding='utf-8') as lua_dst:
        lua_dst.write(lua_dst_data)

    result = utils.check_dcs_bios_entry(lua_dst_data=lua_dst_data, lua_dst_path=install_dir, temp_dir=tmpdir)
    assert result == ('\n\nExport.lua exists.\n\nDCS-BIOS entry added.\n\nYou verify installation '
                      'at:\ngithub.com/DCS-Skunkworks/DCSFlightpanels/wiki/Installation')


@mark.parametrize('lua_dst_data', [
    r'dofile(lfs.writedir()..[[Scripts\DCS-BIOS\BIOS.lua]])',
    r'dofile(lfs.writedir() .. [[Scripts\DCS-BIOS\BIOS.lua]])',
], ids=['dofile without space', 'dofile with space'])
def test_check_dcs_bios_entry_ok(lua_dst_data, tmpdir):
    install_dir = tmpdir / 'install'
    makedirs(install_dir)
    lua = 'Export.lua'

    with open(file=tmpdir / lua, mode='a+', encoding='utf-8') as lua_from_zip:
        lua_from_zip.write('anything')
    with open(file=install_dir / lua, mode='a+', encoding='utf-8') as lua_dst:
        lua_dst.write(lua_dst_data)

    result = utils.check_dcs_bios_entry(lua_dst_data=lua_dst_data, lua_dst_path=install_dir, temp_dir=tmpdir)
    assert result == '\n\nExport.lua exists.\n\nDCS-BIOS entry detected.'


@mark.parametrize('ext, result', [('json', 14), ('exe', 0)])
def test_count_files_exists(ext, result, test_dcs_bios):
    assert utils.count_files(directory=test_dcs_bios / 'doc' / 'json', extension=ext) == result


def test_count_files_wrong_dir(test_dcs_bios):
    assert utils.count_files(directory=test_dcs_bios / 'wrong', extension='json') == -1


@mark.slow
def test_collect_debug_data(switch_dcs_bios_path_in_config, resources):
    from tempfile import gettempdir
    from zipfile import ZipFile
    with open(Path(gettempdir()) / 'Ka50_999.png', 'w+') as png:
        png.write('')
    with patch('dcspy.utils.get_config_yaml_location', lambda: resources):
        zip_file = utils.collect_debug_data()
    assert 'dcspy_debug_' in str(zip_file)
    assert zip_file.suffix == '.zip'
    assert zip_file.is_file()
    assert zip_file.exists()
    with ZipFile(file=zip_file, mode='r') as zipf:
        zip_list = zipf.namelist()
    assert 'system_data.txt' in zip_list
    assert sum('.yaml' in s for s in zip_list) == 4
    assert 'dcspy.log' in zip_list
    assert 'Ka50_999.png' in zip_list
    assert 'dcs.log' in zip_list


@mark.slow
def test_run_pip_command_success():
    rc, err, out = utils.run_pip_command('list')
    assert rc == 0
    assert 'pip' in out, out
    assert err == '' or len(err) > 1, err


@mark.slow
def test_run_pip_command_failed():
    rc, err, out = utils.run_pip_command('bullshit')
    assert rc == 1
    assert out == '', out
    assert err != '', err


@mark.slow
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
@mark.parametrize('cmd, result', [('Clear-Host', 0), ('bullshit', -1)])
def test_run_command(cmd, result):
    rc = utils.run_command(cmd=['powershell', cmd])
    assert rc == result


@mark.parametrize('plane_str, roots , values', [
    ('FA-18C_hornet', 80, 531),
    ('F-16C_50', 49, 533),
    ('F-4E-45MC', 116, 1123),
    ('Ka-50', 77, 599),
    ('Ka-50_3', 77, 599),
    ('Mi-8MT', 77, 800),
    ('Mi-24P', 114, 1001),
    ('AH-64D_BLK_II', 53, 730),
    ('A-10C', 64, 777),
    ('A-10C_2', 64, 777),
    ('F-14A-135-GR', 76, 1124),
    ('F-14B', 76, 1124),
    ('AV8BNA', 48, 515),
    ('F-15ESE', 98, 890),
])
def test_get_full_bios_for_plane(plane_str, roots, values, test_dcs_bios):
    model = utils.get_full_bios_for_plane(plane=plane_str, bios_dir=test_dcs_bios)
    assert len(model.root) == roots
    assert sum(len(values) for values in model.root.values()) == values


def test_get_inputs_for_plane(test_dcs_bios):
    from dcspy.models import CTRL_LIST_SEPARATOR, ControlKeyData
    bios = utils.get_inputs_for_plane(plane='A-10C', bios_dir=test_dcs_bios)
    for section, ctrls in bios.items():
        for name, ctrl in ctrls.items():
            assert isinstance(ctrl, ControlKeyData), f'Wrong type fpr {section} / {name}'

    list_of_ctrls = utils.get_list_of_ctrls(inputs=bios)
    assert CTRL_LIST_SEPARATOR
    assert CTRL_LIST_SEPARATOR in list_of_ctrls[0], list_of_ctrls[0]


def test_get_depiction_of_ctrls(test_dcs_bios):
    from dcspy.models import ControlDepiction
    bios = utils.get_inputs_for_plane(plane='A-10C', bios_dir=test_dcs_bios)
    ctrls_depiction = utils.get_depiction_of_ctrls(inputs=bios)
    assert isinstance(ctrls_depiction['IFF_CODE'], ControlDepiction)


def test_get_inputs_for_wrong_plane(test_dcs_bios):
    with raises(KeyError):
        _ = utils.get_inputs_for_plane(plane='Wrong', bios_dir=test_dcs_bios)


def test_get_plane_aliases_all(test_dcs_bios):
    s = utils.get_plane_aliases(bios_dir=test_dcs_bios)
    assert s == {
        'A-10C': ['CommonData', 'A-10C'],
        'A-10C_2': ['CommonData', 'A-10C'],
        'AH-64D_BLK_II': ['CommonData', 'AH-64D'],
        'AV8BNA': ['CommonData', 'AV8BNA', 'NS430'],
        'F-14A-135-GR': ['CommonData', 'F-14', 'NS430'],
        'F-14B': ['CommonData', 'F-14', 'NS430'],
        'F-15ESE': ['CommonData', 'F-15E'],
        'F-16C_50': ['CommonData', 'F-16C_50'],
        'F-4E-45MC': ['CommonData', 'F-4E'],
        'FA-18C_hornet': ['CommonData', 'FA-18C_hornet'],
        'Ka-50': ['CommonData', 'Ka-50'],
        'Ka-50_3': ['CommonData', 'Ka-50'],
        'Mi-24P': ['CommonData', 'Mi-24P', 'NS430'],
        'Mi-8MT': ['CommonData', 'Mi-8MT', 'NS430'],
        'Mi-8MTV2': ['CommonData', 'Mi-8MT'],
        'NS430': ['CommonData'],
    }


def test_get_plane_aliases_one_plane(test_dcs_bios):
    s = utils.get_plane_aliases(bios_dir=test_dcs_bios, plane='A-10C')
    assert s == {'A-10C': ['CommonData', 'A-10C']}


def test_get_plane_aliases_wrong_plane(test_dcs_bios):
    with raises(KeyError):
        _ = utils.get_plane_aliases(bios_dir=test_dcs_bios, plane='A-Wrong')


def test_get_planes_list(test_dcs_bios):
    plane_list = utils.get_planes_list(bios_dir=test_dcs_bios)
    assert plane_list == [
        'A-10C',
        'A-10C_2',
        'AH-64D_BLK_II',
        'AV8BNA',
        'F-14A-135-GR',
        'F-14B',
        'F-15ESE',
        'F-16C_50',
        'F-4E-45MC',
        'FA-18C_hornet',
        'Ka-50',
        'Ka-50_3',
        'Mi-24P',
        'Mi-8MT',
        'Mi-8MTV2',
    ]


def test_clone_progress():
    from PySide6.QtCore import QObject, Signal

    class Signals(QObject):
        progress = Signal(int)
        stage = Signal(str)

    def update_progress(progress):
        assert progress == 100

    def update_label(stage):
        assert stage == 'Git clone: Counting'

    signals = Signals()
    signals.progress.connect(update_progress)
    signals.stage.connect(update_label)
    clone = utils.CloneProgress(signals.progress, signals.stage)
    clone.update(5, 1, 1, 'test')


@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_get_config_yaml_location():
    assert utils.get_config_yaml_location() == Path(environ.get('LOCALAPPDATA', None)) / 'dcspy'


def test_replace_symbols():
    assert utils.replace_symbols('1q2w3e', (('1', '4'), ('w', 'W'))) == '4q2W3e'


def test_substitute_symbols():
    assert utils.substitute_symbols('123qwe123qwe', ((r'\d+', r'QWE'),)) == 'QWEqweQWEqwe'


def test_key_request_create(test_config_yaml):
    def get_bios_fn(val: str) -> int:
        return 1

    key_req = utils.KeyRequest(yaml_path=test_config_yaml.parent / 'F-16C_50.yaml', get_bios_fn=get_bios_fn)
    assert key_req.buttons[get_key_instance('ONE')].is_cycle is True
    assert key_req.buttons[get_key_instance('G1_M1')].is_push_button is True
    assert key_req.buttons[get_key_instance('G2_M1')].is_custom is True
    assert key_req.buttons[get_key_instance('M_4')].is_push_button is True

    req_model = key_req.get_request(get_key_instance('G3_M1'))
    assert req_model.is_cycle is False
    assert req_model.is_push_button is False
    assert req_model.is_custom is False


def test_key_request_update_bios_data_and_set_req(test_config_yaml):
    def get_bios_fn(val: str) -> int:
        return 1

    key_req = utils.KeyRequest(yaml_path=test_config_yaml.parent / 'F-16C_50.yaml', get_bios_fn=get_bios_fn)
    key = get_key_instance('G3_M1')
    req = 'MASTER_ARM_SW 1'
    assert key_req.cycle_button_ctrl_name == {'IFF_MASTER_KNB': 0}
    key_req.set_request(key, req)
    assert key_req.get_request(key).raw_request == req


@mark.slow
def test_generate_bios_jsons_with_lupa(test_saved_games):
    utils.generate_bios_jsons_with_lupa(dcs_save_games=test_saved_games)
    mosquito = utils.get_full_bios_for_plane(plane='MosquitoFBMkVI', bios_dir=test_saved_games / 'Scripts' / 'DCS-BIOS')
    assert len(mosquito.root) == 27
    assert sum(len(values) for values in mosquito.root.values()) == 299
