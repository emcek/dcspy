from unittest.mock import patch, PropertyMock, MagicMock, mock_open

from packaging import version
from pytest import mark

from dcspy import utils


@mark.parametrize('online_tag, result', [('1.1.1', (True, version.parse('1.1.1'), 'github.com/fake.tgz', '09 August 2021', 'Pre-release', 'fake.tgz')),
                                         ('3.2.1', (False, version.parse('3.2.1'), 'github.com/fake.tgz', '09 August 2021', 'Pre-release', 'fake.tgz'))])
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
        assert utils.check_ver_at_github(repo='fake2/package2', current_ver='2.2.2') == (False, version.parse('unknown'), '', '', 'Regular', '')


def test_check_ver_exception():
    with patch.object(utils, 'get', side_effect=Exception('Connection error')):
        assert utils.check_ver_at_github(repo='fake3/package3', current_ver='3.3.3') == (False, version.parse('unknown'), '', '', 'Regular', '')


@mark.parametrize('response, result', [(False, False), (True, True)])
def test_download_file(response, result, tmp_path):
    dl_file = str(tmp_path / 'tmp.txt')
    with patch.object(utils, 'get') as response_get:
        type(response_get.return_value).ok = PropertyMock(return_value=response)
        type(response_get.return_value).iter_content = MagicMock(return_value=[b'1', b'0', b'0', b'1'])
        assert utils.download_file('https://test.com', dl_file) is result


def test_proc_is_running():
    assert utils.proc_is_running('python')
    assert not utils.proc_is_running('wrong_python')


def test_dummy_save_load_set_defaults():
    from os import makedirs, remove, rmdir, environ
    makedirs(name='./tmp', exist_ok=True)
    test_tmp_yaml = './tmp/c.yaml'

    utils.save_cfg({'font_mono_xs': 9}, test_tmp_yaml)
    d_cfg = utils.load_cfg(test_tmp_yaml)
    assert d_cfg == {'font_mono_xs': 9}
    d_cfg = utils.set_defaults(d_cfg, test_tmp_yaml)
    assert d_cfg == {'keyboard': 'G13', 'show_gui': True, 'autostart': False,
                     'dcsbios': f'D:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
                     'dcs': 'C:\\Program Files\\Eagle Dynamics\\DCS World OpenBeta',
                     'verbose': False,
                     'font_name': 'consola.ttf',
                     'font_mono_s': 11,
                     'font_mono_xs': 9,
                     'font_mono_l': 16,
                     'font_color_s': 22,
                     'font_color_xs': 18,
                     'font_color_l': 32,
                     'theme_mode': 'system',
                     'theme_color': 'blue'}
    with open(test_tmp_yaml, 'w+') as f:
        f.write('')
    d_cfg = utils.load_cfg(test_tmp_yaml)
    assert len(d_cfg) == 0

    remove(test_tmp_yaml)
    rmdir('./tmp/')


def test_check_dcs_ver_file_exists_with_ver(autoupdate1_cfg):
    with patch('dcspy.utils.open', mock_open(read_data=autoupdate1_cfg)):
        dcs_ver = utils.check_dcs_ver('')
        assert dcs_ver == ('openbeta', '2.7.16.28157')


def test_check_dcs_ver_file_exists_without_ver(autoupdate2_cfg):
    with patch('dcspy.utils.open', mock_open(read_data=autoupdate2_cfg)):
        dcs_ver = utils.check_dcs_ver('')
        assert dcs_ver == ('openbeta', 'Unknown')


def test_check_dcs_ver_file_exists_without_branch(autoupdate3_cfg):
    with patch('dcspy.utils.open', mock_open(read_data=autoupdate3_cfg)):
        dcs_ver = utils.check_dcs_ver('')
        assert dcs_ver == ('stable', '2.7.18.28157')


def test_check_dcs_ver_file_not_exists():
    with patch('dcspy.utils.open', side_effect=FileNotFoundError):
        dcs_ver = utils.check_dcs_ver('')
        assert dcs_ver == ('Unknown', 'Unknown')
