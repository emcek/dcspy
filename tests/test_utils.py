from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, mock_open, patch

from packaging import version
from pytest import mark

from dcspy import utils


@mark.parametrize('online_tag, result', [
    ('1.1.1', utils.ReleaseInfo(latest=True,
                                ver=version.parse('1.1.1'),
                                dl_url='github.com/fake.tgz',
                                published='09 August 2021',
                                release_type='Pre-release',
                                archive_file='fake.tgz')),
    ('3.2.1', utils.ReleaseInfo(latest=False,
                                ver=version.parse('3.2.1'),
                                dl_url='github.com/fake.tgz',
                                published='09 August 2021',
                                release_type='Pre-release',
                                archive_file='fake.tgz'))
], ids=['No update', 'New version'])
def test_check_ver_is_possible(online_tag, result):
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=True)
        type(response_get.return_value).json = MagicMock(return_value={'tag_name': online_tag, 'prerelease': True,
                                                                       'assets': [{'browser_download_url': 'github.com/fake.tgz'}],
                                                                       'published_at': '2021-08-09T16:41:51Z'})
        assert utils.check_ver_at_github(repo='fake1/package1', current_ver='1.1.1') == result


def test_check_ver_can_not_check():
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=False)
        assert utils.check_ver_at_github(repo='fake2/package2', current_ver='2.2.2') == utils.ReleaseInfo(False, version.parse('0.0.0'), '', '', 'Regular', '')


def test_check_ver_exception():
    with patch.object(utils, 'get', side_effect=Exception('Connection error')):
        assert utils.check_ver_at_github(repo='fake3/package3', current_ver='3.3.3') == utils.ReleaseInfo(False, version.parse('0.0.0'), '', '', 'Regular', '')


@mark.parametrize('online_tag, result', [
    ('1.1.1', 'v1.1.1 (latest)'),
    ('3.2.1', 'v1.1.1 (please update!)')
], ids=['No update', 'New version'])
def test_get_version_string_is_possible(online_tag, result):
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=True)
        type(response_get.return_value).json = MagicMock(return_value={'tag_name': online_tag, 'prerelease': True,
                                                                       'assets': [{'browser_download_url': 'github.com/fake.tgz'}],
                                                                       'published_at': '2021-08-09T16:41:51Z'})
        assert utils.get_version_string(repo='fake1/package1', current_ver='1.1.1', check=True) == result


def test_get_version_string_without_checking():
    assert utils.get_version_string(repo='fake4/package4', current_ver='4.4.4', check=False) == 'v4.4.4'


def test_get_version_string_exception():
    with patch.object(utils, 'get', side_effect=Exception('Connection error')):
        assert utils.get_version_string(repo='fake4/package4', current_ver='4.4.4', check=True) == 'v4.4.4 (failed)'


@mark.parametrize('response, result', [(False, False), (True, True)], ids=['Download failed', 'Download success'])
def test_download_file(response, result, tmp_path):
    dl_file = str(tmp_path / 'tmp.txt')
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=response)
        type(response_get.return_value).iter_content = MagicMock(return_value=[b'1', b'0', b'0', b'1'])
        assert utils.download_file('https://test.com', dl_file) is result


def test_proc_is_running():
    assert utils.proc_is_running('python')
    assert not utils.proc_is_running('wrong_python')


def test_dummy_save_load_set_defaults(tmpdir):
    from os import environ
    test_tmp_yaml = Path(tmpdir) / 'c.yml'

    utils.save_cfg(cfg_dict={'font_mono_xs': 9}, filename=test_tmp_yaml)
    d_cfg = utils.load_cfg(filename=test_tmp_yaml)
    assert d_cfg == {'font_mono_xs': 9}
    d_cfg = utils.set_defaults(cfg=d_cfg, filename=test_tmp_yaml)
    assert d_cfg == {'keyboard': 'G13',
                     'save_lcd': False,
                     'show_gui': True,
                     'autostart': False,
                     'dcsbios': f'D:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
                     'dcs': 'C:\\Program Files\\Eagle Dynamics\\DCS World OpenBeta',
                     'verbose': False,
                     'check_bios': True,
                     'check_ver': True,
                     'font_name': 'consola.ttf',
                     'font_mono_s': 11,
                     'font_mono_xs': 9,
                     'font_mono_l': 16,
                     'font_color_s': 22,
                     'font_color_xs': 18,
                     'font_color_l': 32,
                     'f16_ded_font': True,
                     'git_bios': False,
                     'git_bios_ref': 'master',
                     'theme_mode': 'system',
                     'theme_color': 'blue'}
    with open(test_tmp_yaml, 'w+') as f:
        f.write('')
    d_cfg = utils.load_cfg(filename=test_tmp_yaml)
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


def test_is_git_repo(tmpdir):
    from git import Repo
    assert utils.is_git_repo(tmpdir) is False
    Repo.init(tmpdir)
    assert utils.is_git_repo(tmpdir) is True


def test_check_github_repo(tmpdir):
    from re import search
    sha = utils.check_github_repo(git_ref='master', update=True, repo='emcek/dcspy', repo_dir=tmpdir)
    match = search(r'(master):\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}\sby:\s.*', sha)
    assert match.group(1) == 'master'
    sha = utils.check_github_repo(git_ref='branch', update=True, repo='emcek/dcspy', repo_dir=tmpdir)
    match = search(r'([0-9a-f]{8})\sfrom:\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}\sby:\s.*', sha)
    assert match.group(1)
    sha = utils.check_github_repo(git_ref='master', update=False, repo='emcek/dcspy', repo_dir=tmpdir)
    match = search(r'([0-9a-f]{8})\sfrom:\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', sha)
    assert match.group(1)


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
    assert result == '\n\nExport.lua exists.\n\nDCS-BIOS entry added.\n\nYou verify installation at:\ngithub.com/DCSFlightpanels/DCSFlightpanels/wiki/Installation'


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
