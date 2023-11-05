from os import linesep, makedirs
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, mock_open, patch

import pytest
from packaging import version
from pytest import mark

from dcspy import utils
from dcspy.models import DEFAULT_FONT_NAME


@mark.parametrize('online_tag, result', [
    ('1.1.1', utils.ReleaseInfo(latest=True,
                                ver=version.parse('1.1.1'),
                                dl_url='github.com/fake.tgz',
                                published='09 August 2021',
                                release_type='Pre-release',
                                asset_file='fake.tgz')),
    ('3.2.1', utils.ReleaseInfo(latest=False,
                                ver=version.parse('3.2.1'),
                                dl_url='github.com/fake.tgz',
                                published='09 August 2021',
                                release_type='Pre-release',
                                asset_file='fake.tgz'))
], ids=[
    'No update',
    'New version',
])
def test_check_ver_is_possible(online_tag, result):
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=True)
        type(response_get.return_value).json = MagicMock(return_value={'tag_name': online_tag, 'prerelease': True,
                                                                       'assets': [{
                                                                           'browser_download_url': 'github.com/fake.tgz'}],
                                                                       'published_at': '2021-08-09T16:41:51Z'})
        assert utils.check_ver_at_github(repo='fake1/package1', current_ver='1.1.1', extension='.tgz') == result


def test_check_ver_can_not_check():
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=False)
        assert utils.check_ver_at_github(repo='fake2/package2', current_ver='2.2.2',
                                         extension='.zip') == utils.ReleaseInfo(False, version.parse('0.0.0'), '', '',
                                                                                'Regular', '')


def test_check_ver_exception():
    with patch.object(utils, 'get', side_effect=Exception('Connection error')):
        assert utils.check_ver_at_github(repo='fake3/package3', current_ver='3.3.3',
                                         extension='.exe') == utils.ReleaseInfo(False, version.parse('0.0.0'), '', '',
                                                                                'Regular', '')


@mark.parametrize('online_tag, result', [
    ('1.1.1', 'v1.1.1 (latest)'),
    ('3.2.1', 'v1.1.1 (update!)')
], ids=['No update', 'New version'])
def test_get_version_string_is_possible(online_tag, result):
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=True)
        type(response_get.return_value).json = MagicMock(return_value={'tag_name': online_tag, 'prerelease': True,
                                                                       'assets': [{
                                                                           'browser_download_url': 'github.com/fake.tgz'}],
                                                                       'published_at': '2021-08-09T16:41:51Z'})
        assert utils.get_version_string(repo='fake1/package1', current_ver='1.1.1', check=True) == result


def test_get_version_string_without_checking():
    assert utils.get_version_string(repo='fake4/package4', current_ver='4.4.4', check=False) == 'v4.4.4'


def test_get_version_string_exception():
    with patch.object(utils, 'get', side_effect=Exception('Connection error')):
        assert utils.get_version_string(repo='fake4/package4', current_ver='4.4.4', check=True) == 'v4.4.4 (failed)'


@mark.parametrize('response, result', [(False, False), (True, True)], ids=['Download failed', 'Download success'])
def test_download_file(response, result, tmp_path):
    dl_file = tmp_path / 'tmp.txt'
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=response)
        type(response_get.return_value).iter_content = MagicMock(return_value=[b'1', b'0', b'0', b'1'])
        assert utils.download_file('https://test.com', dl_file) is result


def test_proc_is_running():
    assert utils.proc_is_running('python')
    assert not utils.proc_is_running('wrong_python')


def test_dummy_save_load_migrate(tmpdir):
    from os import environ

    from dcspy.migration import migrate
    test_tmp_yaml = Path(tmpdir) / 'test_cfg.yaml'

    utils.save_yaml(data={'font_mono_s': 9}, full_path=test_tmp_yaml)
    d_cfg = utils.load_yaml(full_path=test_tmp_yaml)
    assert d_cfg == {'font_mono_s': 9}
    d_cfg = migrate(cfg=d_cfg)
    assert d_cfg == {
        'api_ver': '3.0.0-rc2',
        'keyboard': 'G13',
        'save_lcd': False,
        'show_gui': True,
        'autostart': False,
        'completer_items': 20,
        'current_plane': 'A-10C',
        'dcsbios': f'D:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
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
        'git_bios': False,
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


def test_check_bios_ver(tmpdir):
    makedirs(Path(tmpdir) / 'lib' / 'modules' / 'common_modules')
    common_data_lua = Path(tmpdir) / 'lib' / 'modules' / 'common_modules' / 'CommonData.lua'
    with open(file=common_data_lua, encoding='utf-8', mode='w+') as cd_lua:
        cd_lua.write('local function getVersion()\n\treturn "1.2.3"\nend')
    result = utils.check_bios_ver(bios_path=tmpdir)
    assert result == utils.ReleaseInfo(latest=False, ver=version.parse('1.2.3'), dl_url='',
                                       published='', release_type='', asset_file='')


def test_check_bios_ver_empty_lua(tmpdir):
    makedirs(Path(tmpdir) / 'lib')
    common_data_lua = Path(tmpdir) / 'lib' / 'CommonData.lua'
    with open(file=common_data_lua, encoding='utf-8', mode='w+') as cd_lua:
        cd_lua.write('')
    result = utils.check_bios_ver(bios_path=tmpdir)
    assert result == utils.ReleaseInfo(latest=False, ver=version.parse('0.0.0'), dl_url='',
                                       published='', release_type='', asset_file='')


def test_check_bios_ver_raise_exception(tmpdir):
    result = utils.check_bios_ver(bios_path=tmpdir)
    assert result == utils.ReleaseInfo(latest=False, ver=version.parse('0.0.0'), dl_url='',
                                       published='', release_type='', asset_file='')


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
    match = search(r'(master):\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}\sby:\s.*', sha)
    assert match.group(1) == 'master'
    sha = utils.check_github_repo(git_ref='branch', update=True, repo='emcek/common_sense', repo_dir=tmpdir)
    match = search(r'([0-9a-f]{8})\sfrom:\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}\sby:\s.*', sha)
    assert match.group(1)
    sha = utils.check_github_repo(git_ref='master', update=False, repo='emcek/common_sense', repo_dir=tmpdir)
    match = search(r'([0-9a-f]{8})\sfrom:\s\d{2}-\w{3}-\d{4}\s\d{2}:\d{2}:\d{2}', sha)
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
    from os import makedirs
    install_dir = tmpdir / 'install'
    makedirs(install_dir)
    lua = 'Export.lua'
    lua_dst_data = ''

    with open(file=tmpdir / lua, mode='a+', encoding='utf-8') as lua_from_zip:
        lua_from_zip.write('anything')
    with open(file=install_dir / lua, mode='a+', encoding='utf-8') as lua_dst:
        lua_dst.write(lua_dst_data)

    result = utils.check_dcs_bios_entry(lua_dst_data=lua_dst_data, lua_dst_path=install_dir, temp_dir=tmpdir)
    assert result == '\n\nExport.lua exists.\n\nDCS-BIOS entry added.\n\nYou verify installation at:\ngithub.com/DCS-Skunkworks/DCSFlightpanels/wiki/Installation'


def test_check_dcs_bios_entry_ok(tmpdir):
    from os import makedirs
    install_dir = tmpdir / 'install'
    makedirs(install_dir)
    lua = 'Export.lua'
    lua_dst_data = r'dofile(lfs.writedir()..[[Scripts\DCS-BIOS\BIOS.lua]])'

    with open(file=tmpdir / lua, mode='a+', encoding='utf-8') as lua_from_zip:
        lua_from_zip.write('anything')
    with open(file=install_dir / lua, mode='a+', encoding='utf-8') as lua_dst:
        lua_dst.write(lua_dst_data)

    result = utils.check_dcs_bios_entry(lua_dst_data=lua_dst_data, lua_dst_path=install_dir, temp_dir=tmpdir)
    assert result == '\n\nExport.lua exists.\n\nDCS-BIOS entry detected.'


@mark.slow
def test_collect_debug_data():
    from tempfile import gettempdir
    from zipfile import ZipFile
    with open(Path(gettempdir()) / 'Ka50_999.png', 'w+') as png:
        png.write('')
    zip_file = utils.collect_debug_data()
    assert 'dcspy_debug_' in str(zip_file)
    assert zip_file.suffix == '.zip'
    assert zip_file.is_file()
    assert zip_file.exists()
    with ZipFile(file=zip_file, mode='r') as zipf:
        zip_list = zipf.namelist()
    assert 'system_data.txt' in zip_list
    assert 'config.yaml' in zip_list
    assert 'dcspy.log' in zip_list
    assert 'Ka50_999.png' in zip_list


@mark.slow
def test_run_pip_command_success():
    rc, err, out = utils.run_pip_command('list')
    assert rc == 0
    assert 'pip' in out, out
    assert err == '' or err == f'WARNING: There was an error checking the latest version of pip.{linesep}', err


@mark.slow
def test_run_pip_command_failed():
    rc, err, out = utils.run_pip_command('bullshit')
    assert rc == 1
    assert out == '', out
    assert err != '', err


def test_get_full_bios_for_plane(resources):
    a10_model = utils.get_full_bios_for_plane(plane='A-10C', bios_dir=resources / 'dcs_bios')
    assert len(a10_model.root) == 64
    assert sum(len(values) for values in a10_model.root.values()) == 772


def test_get_inputs_for_plane(resources):
    from dcspy.models import CTRL_LIST_SEPARATOR, ControlKeyData
    bios = utils.get_inputs_for_plane(plane='A-10C', bios_dir=resources / 'dcs_bios')
    for section, ctrls in bios.items():
        for name, ctrl in ctrls.items():
            assert isinstance(ctrl, ControlKeyData), f'Wrong type fpr {section} / {name}'

    list_of_ctrls = utils.get_list_of_ctrls(inputs=bios)
    assert CTRL_LIST_SEPARATOR
    assert CTRL_LIST_SEPARATOR in list_of_ctrls[0], list_of_ctrls[0]


def test_get_inputs_for_wrong_plane(resources):
    with pytest.raises(KeyError):
        _ = utils.get_inputs_for_plane(plane='Wrong', bios_dir=resources / 'dcs_bios')


def test_get_plane_aliases_all(resources):
    s = utils.get_plane_aliases(bios_dir=resources / 'dcs_bios')
    assert s == {
        'A-10C': ['CommonData', 'A-10C'],
        'A-10C_2': ['CommonData', 'A-10C'],
        'AH-64D_BLK_II': ['CommonData', 'AH-64D'],
        'AV8BNA': ['CommonData', 'AV8BNA', 'NS430'],
        'F-14A-135-GR': ['CommonData', 'F-14', 'NS430'],
        'F-14B': ['CommonData', 'F-14', 'NS430'],
        'F-15ESE': ['CommonData', 'F-15E'],
        'F-16C_50': ['CommonData', 'F-16C_50'],
        'FA-18C_hornet': ['CommonData', 'FA-18C_hornet'],
        'Ka-50': ['CommonData', 'Ka-50'],
        'Ka-50_3': ['CommonData', 'Ka-50'],
        'Mi-24P': ['CommonData', 'Mi-24P', 'NS430'],
        'Mi-8MT': ['CommonData', 'Mi-8MT', 'NS430'],
        'NS430': ['CommonData'],
    }


def test_get_plane_aliases_one_plane(resources):
    s = utils.get_plane_aliases(bios_dir=resources / 'dcs_bios', plane='A-10C')
    assert s == {'A-10C': ['CommonData', 'A-10C']}


def test_get_plane_aliases_wrong_plane(resources):
    with pytest.raises(KeyError):
        _ = utils.get_plane_aliases(bios_dir=resources / 'dcs_bios', plane='A-Wrong')


def test_get_planes_list(resources):
    plane_list = utils.get_planes_list(bios_dir=resources / 'dcs_bios')
    assert plane_list == [
        'A-10C',
        'A-10C_2',
        'AH-64D_BLK_II',
        'AV8BNA',
        'F-14A-135-GR',
        'F-14B',
        'F-15ESE',
        'F-16C_50',
        'FA-18C_hornet',
        'Ka-50',
        'Ka-50_3',
        'Mi-24P',
        'Mi-8MT',
    ]
