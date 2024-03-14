from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest import fixture

from dcspy import aircraft, logitech, models, utils


@fixture()
def sock():
    """Socket mock instance."""
    return MagicMock()


def generate_plane_fixtures(plane, lcd_type_with_fonts):
    """
    Generate fixtures for any plane with any lcd type.

    :param plane: any plane object
    :param lcd_type_with_fonts: lcd_type with fonts
    """
    @fixture()
    def _fixture():
        """Fixture."""
        with patch('dcspy.aircraft.default_yaml', Path(__file__).resolve().parents[1] / 'dcspy' / 'config.yaml'):
            plane_instance = plane(lcd_type_with_fonts)
        return plane_instance
    return _fixture


def generate_keyboard_fixtures(keyboard, lcd_type, lcd_font_setting):
    """
    Generate fixtures for any keyboard and with lcd_font_setting.

    :param keyboard: any keyboard object
    :param lcd_font_setting: FontSetting object
    """
    @fixture()
    def _fixture(sock):
        """Fixture."""
        from dcspy.dcsbios import ProtocolParser
        from dcspy.sdk.key_sdk import GkeySdkManager
        from dcspy.sdk.lcd_sdk import LcdSdkManager

        lcd_sdk = LcdSdkManager('test', lcd_type)

        with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True), \
                patch.object(GkeySdkManager, 'logi_gkey_init', return_value=True):
            return keyboard(parser=ProtocolParser(), sock=sock, fonts=lcd_font_setting)
    return _fixture


for plane_model in ['AdvancedAircraft', 'FA18Chornet', 'F16C50', 'F15ESE', 'Ka50', 'Ka503', 'Mi8MT',
                    'Mi24P', 'AH64DBLKII', 'A10C', 'A10C2', 'F14B', 'F14A135GR', 'AV8BNA']:
    for lcd in ['LcdMono', 'LcdColor']:
        airplane = getattr(aircraft, plane_model)
        lcd_type = getattr(models, lcd)
        if lcd == 'LcdMono':
            lcd_type.set_fonts(models.FontsConfig(name=models.DEFAULT_FONT_NAME, small=9, medium=11, large=16))
        else:
            lcd_type.set_fonts(models.FontsConfig(name=models.DEFAULT_FONT_NAME, small=18, medium=22, large=32))
        name = f'{airplane.__name__.lower()}_{lcd_type.type.name.lower()}'
        globals()[name] = generate_plane_fixtures(airplane, lcd_type)

for keyboard_model in ['G13', 'G510', 'G15v1', 'G15v2', 'G19']:
    key = getattr(logitech, keyboard_model)
    if keyboard_model == 'G19':
        lcd_font = models.FontsConfig(name=models.DEFAULT_FONT_NAME, small=18, medium=22, large=32)
        lcd_type = 2
    else:
        lcd_font = models.FontsConfig(name=models.DEFAULT_FONT_NAME, small=9, medium=11, large=16)
        lcd_type = 1
    globals()[keyboard_model] = generate_keyboard_fixtures(key, lcd_type, lcd_font)


def pytest_addoption(parser) -> None:
    """
    Register img_precision CLI argument.

    :param parser:
    """
    parser.addoption('--img_precision', action='store',  type=int, default=0)


@fixture(scope='session')
def img_precision(pytestconfig):
    """
    Get value of img_precision parameter form command line.

    :param pytestconfig:
    :return: value from command line
    """
    return pytestconfig.getoption('img_precision')


@fixture()
def resources():
    """
    Path to tests/resources directory.

    :return: path to tests/resources directory
    """
    return Path(__file__).resolve().with_name('resources')


@fixture()
def test_config_yaml(resources):
    """
    Path to YAML tests config file.

    :return: path to yaml config file
    """
    return resources / 'config.yaml'


@fixture()
def test_dcs_bios(resources):
    """
    Path to DCS-BIOS for test purposes.

    :return: path to DCS-BIOS
    """
    return resources / 'DCS.openbeta' / 'Scripts' / 'DCS-BIOS'


# <=><=><=><=><=> dcsbios <=><=><=><=><=>
@fixture
def protocol_parser():
    """Instance of ProtocolParser."""
    from dcspy.dcsbios import ProtocolParser
    return ProtocolParser()


@fixture
def get_ctrl_for_plane(test_dcs_bios, request):
    """
    Get Control object from DCS-BIOS for plane.

    :param test_dcs_bios: The directory containing the DCS-BIOS configuration files.
    :param request: The request object containing parameters for the test.
    """
    from dcspy.utils import get_full_bios_for_plane

    bios_plane = request.param[0]
    ctrl_name = request.param[1]
    plane_bios = get_full_bios_for_plane(plane=bios_plane, bios_dir=test_dcs_bios)
    ctrl = plane_bios.get_ctrl(ctrl_name=ctrl_name)
    return ctrl


# <=><=><=><=><=> logitech <=><=><=><=><=>
@fixture()
def lcd_font_mono():
    """Returns font configuration for mono LCD."""
    return models.FontsConfig(name=models.DEFAULT_FONT_NAME, small=9, medium=11, large=16)


@fixture()
def lcd_font_color(protocol_parser):
    """Returns font configuration for color LCD."""
    return models.FontsConfig(name=models.DEFAULT_FONT_NAME, small=18, medium=22, large=32)


@fixture()
def keyboard_base(protocol_parser, sock):
    """
    Return instance of KeyboardManager.

    :param protocol_parser: instance of ProtocolParser
    :param sock: net socket object
    :return: KeyboardManager
    """
    from dcspy.sdk.key_sdk import GkeySdkManager
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    lcd_sdk = LcdSdkManager('test', 1)

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True), \
            patch.object(GkeySdkManager, 'logi_gkey_init', return_value=True):
        return logitech.KeyboardManager(protocol_parser, sock=sock)


@fixture()
def keyboard_mono(protocol_parser, sock, lcd_font_mono, resources):
    """
    Return instance of Keyboard with LcdMono.

    :param protocol_parser: instance of ProtocolParser
    :param sock: net socket object
    :param lcd_font_mono: font configuration for LCD
    :param resources: Path to tests/resources directory.
    :return: KeyboardManager
    """
    from dcspy.aircraft import BasicAircraft
    from dcspy.models import Gkey, LcdButton, LcdMono
    from dcspy.sdk.key_sdk import GkeySdkManager
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    class Mono(logitech.KeyboardManager):
        def __init__(self, parser, socket, **kwargs) -> None:
            LcdMono.set_fonts(kwargs['fonts'])
            super().__init__(parser, socket, lcd_type=LcdMono)
            self.buttons = (LcdButton.ONE, LcdButton.TWO, LcdButton.THREE, LcdButton.FOUR)
            self.gkey = Gkey.generate(key=3, mode=1)
            self.vert_space = 10
            plane = BasicAircraft(lcd_type=self.lcd)
            plane.key_req = utils.KeyRequest(yaml_path=resources / 'test_plane.yaml', get_bios_fn=lambda x: 1)
            self.plane = plane

        def _setup_plane_callback(self) -> None:
            print('empty callback setup')

    lcd_sdk = LcdSdkManager('test', 1)

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True), \
            patch.object(GkeySdkManager, 'logi_gkey_init', return_value=True):
        return Mono(parser=protocol_parser, socket=sock, fonts=lcd_font_mono)


@fixture()
def keyboard_color(protocol_parser, sock, lcd_font_color, resources):
    """
    Return instance of Keyboard with LcdColor.

    :param protocol_parser: instance of ProtocolParser
    :param sock: net socket object
    :param lcd_font_color: font configuration for LCD
    :param resources: Path to tests/resources directory.
    :return: KeyboardManager
    """
    from dcspy.aircraft import BasicAircraft
    from dcspy.models import Gkey, LcdButton, LcdColor
    from dcspy.sdk.key_sdk import GkeySdkManager
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    class Color(logitech.KeyboardManager):
        def __init__(self, parser, socket, **kwargs) -> None:
            LcdColor.set_fonts(kwargs['fonts'])
            super().__init__(parser, socket, lcd_type=LcdColor)
            self.buttons = (LcdButton.LEFT, LcdButton.RIGHT, LcdButton.UP, LcdButton.DOWN, LcdButton.OK, LcdButton.CANCEL, LcdButton.MENU)
            self.gkey = Gkey.generate(key=3, mode=1)
            self.vert_space = 40
            plane = BasicAircraft(lcd_type=self.lcd)
            plane.key_req = utils.KeyRequest(yaml_path=resources / 'test_plane.yaml', get_bios_fn=lambda x: 1)
            self.plane = plane

        def _setup_plane_callback(self) -> None:
            print('empty callback setup')

    lcd_sdk = LcdSdkManager('test', 2)

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True), \
            patch.object(GkeySdkManager, 'logi_gkey_init', return_value=True):
        return Color(parser=protocol_parser, socket=sock, fonts=lcd_font_color)


# <=><=><=><=><=> others <=><=><=><=><=>
@fixture()
def default_config():
    """Get default configuration dict."""
    from os import environ
    return {
        'dcsbios': f'C:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
        'dcs': 'C:\\Program Files\\Eagle Dynamics\\DCS World OpenBeta', 'keyboard': 'G13', 'save_lcd': False, 'show_gui': True, 'autostart': False,
        'verbose': False, 'check_bios': True, 'check_ver': True, 'font_name': models.DEFAULT_FONT_NAME, 'font_mono_m': 11, 'font_mono_s': 9, 'font_mono_l': 16,
        'font_color_m': 22, 'font_color_s': 18, 'font_color_l': 32, 'f16_ded_font': True, 'git_bios': True, 'git_bios_ref': 'master', 'toolbar_style': 0,
        'toolbar_area': 4, 'gkeys_area': 2, 'gkeys_float': False, 'theme_mode': 'system', 'theme_color': 'dark-blue', 'completer_items': 20,
        'current_plane': 'A-10A',
    }


@fixture()
def switch_dcs_bios_path_in_config(test_dcs_bios, test_config_yaml):
    """
    Switch path to config yaml file during testing.

    :param test_dcs_bios: path to DCS-BIOS in tests
    :param test_config_yaml: test confi.yaml file
    """
    from dcspy import utils

    org = utils.load_yaml(test_config_yaml)
    dcs_bios = org['dcsbios']
    org['dcsbios'] = str(test_dcs_bios)
    utils.save_yaml(data=org, full_path=test_config_yaml)
    yield
    org['dcsbios'] = dcs_bios
    utils.save_yaml(data=org, full_path=test_config_yaml)


# <=><=><=><=><=> DCS World autoupdate_cfg <=><=><=><=><=>
@fixture()
def autoupdate1_cfg():
    """Mock for correct autoupdate_cfg."""
    return """{
 "WARNING": "DO NOT EDIT this file. You may break your install!",
 "branch": "openbeta",
 "version": "2.7.16.28157",
 "timestamp": "20220729-154039",
 "arch": "x86_64",
 "lang": "EN",
 "modules": [
  "WORLD",
  "FA-18C",
  "NS430_MI-8MTV2",
  "NS430",
  "MI-8MTV2",
  "UH-1H",
  "A-10C",
"""


@fixture()
def autoupdate2_cfg():
    """Mock for wrong autoupdate_cfg."""
    return """{
 "WARNING": "DO NOT EDIT this file. You may break your install!",
 "branch": "openbeta",
 "timestamp": "20220729-154039",
 "arch": "x86_64",
 "lang": "EN",
 "modules": [
  "WORLD",
  "FA-18C",
  "NS430_MI-8MTV2",
  "NS430",
  "MI-8MTV2",
  "UH-1H",
  "A-10C",
"""


@fixture()
def autoupdate3_cfg():
    """Mock for wrong autoupdate_cfg."""
    return """{
 "WARNING": "DO NOT EDIT this file. You may break your install!",
 "version": "2.7.18.28157",
 "timestamp": "20220729-154039",
 "arch": "x86_64",
 "lang": "EN",
 "modules": [
  "WORLD",
  "FA-18C",
  "NS430_MI-8MTV2",
  "NS430",
  "MI-8MTV2",
  "UH-1H",
  "A-10C",
"""


# <=><=><=><=><=> airplane bios data <=><=><=><=><=>
@fixture()
def apache_pre_mode_bios_data():
    """Bios values for AH-64D Apache PRE mode."""
    return [
        ('PLT_EUFD_LINE1', 'LOW ROTOR RPM     |RECTIFIER 2 FAIL  |PRESET TUNE VHF  |'),
        ('PLT_EUFD_LINE2', 'ENGINE 2 OUT      |GENERATOR 2 FAIL  |!PRESET 1 134.000|'),
        ('PLT_EUFD_LINE3', 'ENGINE 1 OUT      |AFT FUEL LOW      | PRESET 2 134.000|'),
        ('PLT_EUFD_LINE4', '                  |FORWARD FUEL LOW  | PRESET 3 136.000|'),
        ('PLT_EUFD_LINE5', '                  |                  | PRESET 4 127.000|'),
        ('PLT_EUFD_LINE6', '                  |                  | PRESET 5 125.000|'),
        ('PLT_EUFD_LINE7', '                  |                  | PRESET 6 121.000|'),
        ('PLT_EUFD_LINE8', '~<>VHF*  134.000   MAN               | PRESET 7 141.000|'),
        ('PLT_EUFD_LINE9', ' ==UHF*  240.000   PRE 2         L2  | PRESET 8 128.000|'),
        ('PLT_EUFD_LINE10', ' ==FM1*   30.015   PRE 3    NORM L3  | PRESET 9 126.000|'),
        ('PLT_EUFD_LINE11', ' ==FM2*   30.020   PRE 4         L4  | PRESET10 137.000|'),
    ]


@fixture()
def fa18chornet_mono_bios():
    """Bios values for F/A-18C Hornet for Logitech mono LCD."""
    return [
        ('UFC_SCRATCHPAD_STRING_1_DISPLAY', '11'),
        ('UFC_SCRATCHPAD_STRING_2_DISPLAY', '22'),
        ('UFC_SCRATCHPAD_NUMBER_DISPLAY', '1234567890'),
        ('UFC_OPTION_DISPLAY_1', '1234'),
        ('UFC_OPTION_DISPLAY_2', '2345'),
        ('UFC_OPTION_DISPLAY_3', '3456'),
        ('UFC_OPTION_DISPLAY_4', '4567'),
        ('UFC_OPTION_DISPLAY_5', '5678'),
        ('UFC_COMM1_DISPLAY', '11'),
        ('UFC_COMM2_DISPLAY', '22'),
        ('UFC_OPTION_CUEING_1', '1'),
        ('UFC_OPTION_CUEING_2', '2'),
        ('UFC_OPTION_CUEING_3', '3'),
        ('UFC_OPTION_CUEING_4', '4'),
        ('UFC_OPTION_CUEING_5', '5'),
        ('IFEI_FUEL_DOWN', '123456'),
        ('IFEI_FUEL_UP', '234567'),
    ]


@fixture()
def fa18chornet_color_bios(fa18chornet_mono_bios):
    """Bios values for F/A-18C Hornet for Logitech color LCD."""
    return fa18chornet_mono_bios


@fixture()
def f16c50_mono_bios():
    """Bios values for F16C Viper for Logitech mono LCD."""
    return [
        ('DED_LINE_1', '  INS  08.0/ 6        1a '),
        ('DED_LINE_2', "  LAT *N 43o06.2'*       @"),
        ('DED_LINE_3', "  LNG  E040o34.2'        "),
        ('DED_LINE_4', ' SALT      74FT          '),
        ('DED_LINE_5', ' THDG   25.0o   G/S    0 '),
    ]


@fixture()
def f16c50_color_bios(f16c50_mono_bios):
    """Bios values for F16C Viper for Logitech color LCD."""
    return f16c50_mono_bios


@fixture()
def f15ese_mono_bios():
    """Bios values for F-15ESE Eagle for Logitech mono LCD."""
    return [
        ('F_UFC_LINE1_DISPLAY', '*R2-35     141000-AM'),
        ('F_UFC_LINE2_DISPLAY', 'MARITIME      MAN-'),
        ('F_UFC_LINE3_DISPLAY', ' HQ       AJ PROGRAM'),
        ('F_UFC_LINE4_DISPLAY', 'KY-58       SQUELCH*'),
        ('F_UFC_LINE5_DISPLAY', '*U262000    U133000*'),
        ('F_UFC_LINE6_DISPLAY', ' 10               G '),
    ]


@fixture()
def f15ese_color_bios(f15ese_mono_bios):
    """Bios values for F-15ESE Eagle for Logitech color LCD."""
    return f15ese_mono_bios


@fixture()
def ka50_mono_bios():
    """Bios values for Ka-50 Black Shark II for Logitech mono LCD."""
    return [
        ('PVI_LINE1_APOSTROPHE1', '`'),
        ('PVI_LINE1_APOSTROPHE2', '`'),
        ('PVI_LINE1_POINT', '1'),
        ('PVI_LINE1_SIGN', '-'),
        ('PVI_LINE1_TEXT', '123456'),
        ('PVI_LINE2_APOSTROPHE1', '`'),
        ('PVI_LINE2_APOSTROPHE2', '`'),
        ('PVI_LINE2_POINT', '2'),
        ('PVI_LINE2_SIGN', ' '),
        ('PVI_LINE2_TEXT', '654321'),
        ('AP_ALT_HOLD_LED', 1),
        ('AP_BANK_HOLD_LED', 0),
        ('AP_FD_LED', 1),
        ('AP_HDG_HOLD_LED', 0),
        ('AP_PITCH_HOLD_LED', 1),
    ]


@fixture()
def ka50_color_bios(ka50_mono_bios):
    """Bios values for Ka-50 Black Shark II for Logitech color LCD."""
    return ka50_mono_bios


@fixture()
def ka503_mono_bios(ka50_mono_bios):
    """Bios values for Ka-50 Black Shark III for Logitech mono LCD."""
    return ka50_mono_bios


@fixture()
def ka503_color_bios(ka50_mono_bios):
    """Bios values for Ka-50 Black Shark III for Logitech color LCD."""
    return ka50_mono_bios


@fixture()
def mi8mt_mono_bios():
    """Bios values for Mi-8MTV2 Magnificent Eight for Logitech mono LCD."""
    return [
        ('LMP_AP_HDG_ON', 1),
        ('LMP_AP_PITCH_ROLL_ON', 0),
        ('LMP_AP_HEIGHT_ON', 1),
        ('R863_CNL_SEL', 9),
        ('R863_MOD', 1),
        ('R863_FREQ', '123.525'),
        ('R828_PRST_CHAN_SEL', 9),
        ('YADRO1A_FREQ', '09091.9'),
    ]


@fixture()
def mi8mt_color_bios(mi8mt_mono_bios):
    """Bios values for Mi-8MTV2 Magnificent Eight for Logitech color LCD."""
    return mi8mt_mono_bios


@fixture()
def mi24p_mono_bios():
    """Bios values for Mi-24P Hind for Logitech mono LCD."""
    return [
        ('PLT_R863_CHAN', 9),
        ('PLT_R863_MODUL', 1),
        ('PLT_R828_CHAN', 9),
        ('JADRO_FREQ', '08082.8'),
        ('PLT_SAU_HOVER_MODE_ON_L', 1),
        ('PLT_SAU_ROUTE_MODE_ON_L', 0),
        ('PLT_SAU_ALT_MODE_ON_L', 1),
        ('PLT_SAU_H_ON_L', 0),
        ('PLT_SAU_K_ON_L', 0),
        ('PLT_SAU_T_ON_L', 0),
        ('PLT_SAU_B_ON_L', 1),
    ]


@fixture()
def mi24p_color_bios(mi24p_mono_bios):
    """Bios values for Mi-24P Hind for Logitech color LCD."""
    return mi24p_mono_bios


@fixture()
def ah64dblkii_mono_bios():
    """Bios values for AH-64D Apache for Logitech mono LCD."""
    return [
        ('PLT_EUFD_LINE8', '~<>VHF*  134.000   MAN                121.500   MAN     '),
        ('PLT_EUFD_LINE9', ' ==UHF*  240.000   PRE 2         L2   305.000   MAN     '),
        ('PLT_EUFD_LINE10', ' ==FM1*   30.015   PRE 3    NORM L3    30.000   MAN     '),
        ('PLT_EUFD_LINE11', ' ==FM2*   30.020   PRE 4         L4    30.000   MAN     '),
        ('PLT_EUFD_LINE12', ' ==HF *    2.0000A          LOW         2.0000A         '),
    ]


@fixture()
def ah64dblkii_color_bios(ah64dblkii_mono_bios):
    """Bios values for AH-64D Apache for Logitech color LCD."""
    return ah64dblkii_mono_bios


@fixture()
def a10c_mono_bios():
    """Bios values for A-10C Warthog for Logitech mono LCD."""
    return [
        ('VHFAM_FREQ1', 9),
        ('VHFAM_FREQ2', 1),
        ('VHFAM_FREQ3', 1),
        ('VHFAM_FREQ4', 3),
        ('VHFAM_PRESET', 1),
        ('VHFFM_FREQ1', 3),
        ('VHFFM_FREQ2', 2),
        ('VHFFM_FREQ3', 2),
        ('VHFFM_FREQ4', 0),
        ('VHFFM_PRESET', 3),
        ('UHF_100MHZ_SEL', 2),
        ('UHF_10MHZ_SEL', 3),
        ('UHF_1MHZ_SEL', 2),
        ('UHF_POINT1MHZ_SEL', 1),
        ('UHF_POINT25_SEL', 1),
        ('UHF_PRESET', '01'),
        ('ARC210_FREQUENCY', '123.125'),
        ('ARC210_PREV_MANUAL_FREQ', '234.075'),
    ]


@fixture()
def a10c_color_bios(a10c_mono_bios):
    """Bios values for A-10C Warthog for Logitech color LCD."""
    return a10c_mono_bios


@fixture()
def a10c2_mono_bios(a10c_mono_bios):
    """Bios values for A-10C II Tank Killer for Logitech mono LCD."""
    return a10c_mono_bios


@fixture()
def a10c2_color_bios(a10c_mono_bios):
    """Bios values for A-10C II Tank Killer for Logitech color LCD."""
    return a10c_mono_bios


@fixture()
def av8bna_mono_bios():
    """Bios values for AV-8B N/A Harrier for Logitech mono LCD."""
    return [
        ('UFC_SCRATCHPAD', '123456789012'),
        ('UFC_COMM1_DISPLAY', '11'),
        ('UFC_COMM2_DISPLAY', '22'),
        ('AV8BNA_ODU_1_SELECT', '1'),
        ('AV8BNA_ODU_1_TEXT', '1234'),
        ('AV8BNA_ODU_2_SELECT', '2'),
        ('AV8BNA_ODU_2_TEXT', '2345'),
        ('AV8BNA_ODU_3_SELECT', '3'),
        ('AV8BNA_ODU_3_TEXT', '3456'),
        ('AV8BNA_ODU_4_SELECT', '4'),
        ('AV8BNA_ODU_4_TEXT', '4567'),
        ('AV8BNA_ODU_5_SELECT', '5'),
        ('AV8BNA_ODU_5_TEXT', '5678'),
    ]


@fixture()
def av8bna_color_bios(av8bna_mono_bios):
    """Bios values for AV-8B N/A Harrier for Logitech color LCD."""
    return av8bna_mono_bios


@fixture()
def f14a135gr_mono_bios():
    """Bios values for F-14A-135-GR Tomcat for Logitech mono LCD."""
    return []


@fixture()
def f14a135gr_color_bios(f14a135gr_mono_bios):
    """Bios values for F-14A-135-GR Tomcat for Logitech color LCD."""
    return f14a135gr_mono_bios


@fixture()
def f14b_mono_bios(f14a135gr_mono_bios):
    """Bios values for F-14B Tomcat for Logitech mono LCD."""
    return f14a135gr_mono_bios


@fixture()
def f14b_color_bios(f14a135gr_mono_bios):
    """Bios values for F-14B Tomcat for Logitech color LCD."""
    return f14a135gr_mono_bios
