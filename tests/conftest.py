from unittest.mock import MagicMock, patch

from pytest import fixture

from dcspy import LcdInfo


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


# <=><=><=><=><=> dcsbios <=><=><=><=><=>
@fixture
def protocol_parser():
    """Instance of ProtocolParser."""
    from dcspy.dcsbios import ProtocolParser
    return ProtocolParser()


# <=><=><=><=><=> lcd <=><=><=><=><=>
@fixture()
def lcd_mono() -> LcdInfo:
    """
    Return of mono LCD.

    :return: mono lcd type
    """
    from dcspy import LcdMono
    return LcdMono


@fixture()
def lcd_color() -> LcdInfo:
    """
    Return of color LCD.

    :return: color lcd type
    """
    from dcspy import LcdColor
    return LcdColor


# <=><=><=><=><=> aircraft mono <=><=><=><=><=>
@fixture()
def aircraft(lcd_mono: LcdInfo):
    """
    Return instance of Aircraft base class for Logitech mono LCD.

    :param lcd_mono:
    :return: Aircraft instance
    """
    from dcspy.aircraft import Aircraft
    return Aircraft(lcd_mono)


@fixture()
def hornet_mono(lcd_mono: LcdInfo):
    """
    Return instance of F/A-18C Hornet for Logitech mono LCD.

    :param lcd_mono:
    :return: F/A-18C Hornet instance
    """
    from dcspy.aircraft import FA18Chornet
    return FA18Chornet(lcd_mono)


@fixture()
def viper_mono(lcd_mono: LcdInfo):
    """
    Return instance of F16C Viper for Logitech mono LCD.

    :param lcd_mono:
    :return: F-16C Viper instance
    """
    from dcspy.aircraft import F16C50
    return F16C50(lcd_mono)


@fixture()
def shark_mono(lcd_mono: LcdInfo):
    """
    Return instance of Ka-50 Black Shark II for Logitech mono LCD.

    :param lcd_mono:
    :return: Ka-50 Black Shark II instance
    """
    from dcspy.aircraft import Ka50
    return Ka50(lcd_mono)


@fixture()
def shark3_mono(lcd_mono: LcdInfo):
    """
    Return instance of Ka-50 Black Shark III for Logitech mono LCD.

    :param lcd_mono:
    :return: Ka-50 Black Shark III instance
    """
    from dcspy.aircraft import Ka503
    return Ka503(lcd_mono)


@fixture()
def hip_mono(lcd_mono: LcdInfo):
    """
    Return instance of Mi-8MTV2 Magnificent Eight for Logitech mono LCD.

    :param lcd_mono:
    :return: Mi-8MTV2 Magnificent Eight instance
    """
    from dcspy.aircraft import Mi8MT
    return Mi8MT(lcd_mono)


@fixture()
def hind_mono(lcd_mono: LcdInfo):
    """
    Return instance of Mi-24P Hind for Logitech mono LCD.

    :param lcd_mono:
    :return: Mi-24P Hind instance
    """
    from dcspy.aircraft import Mi24P
    return Mi24P(lcd_mono)


@fixture()
def warthog_mono(lcd_mono: LcdInfo):
    """
    Return instance of A-10C Warthog for Logitech mono LCD.

    :param lcd_mono:
    :return: A-10C Warthog instance
    """
    from dcspy.aircraft import A10C
    return A10C(lcd_mono)


@fixture()
def warthog2_mono(lcd_mono: LcdInfo):
    """
    Return instance of A-10C II Tank Killer for Logitech mono LCD.

    :param lcd_mono:
    :return: A-10C II Tank Killer instance
    """
    from dcspy.aircraft import A10C2
    return A10C2(lcd_mono)


@fixture()
def tomcata_mono(lcd_mono: LcdInfo):
    """
    Return instance of F-14A-135-GR Tomcat for Logitech mono LCD.

    :param lcd_mono:
    :return: F-14A-135-GR Tomcat instance
    """
    from dcspy.aircraft import F14A135GR
    return F14A135GR(lcd_mono)


@fixture()
def tomcatb_mono(lcd_mono: LcdInfo):
    """
    Return instance of F-14B Tomcat for Logitech mono LCD.

    :param lcd_mono:
    :return: F-14B Tomcat instance
    """
    from dcspy.aircraft import F14B
    return F14B(lcd_mono)


@fixture()
def harrier_mono(lcd_mono: LcdInfo):
    """
    Return instance of AV-8B N/A Harrier for Logitech mono LCD.

    :param lcd_mono:
    :return: AV-8B N/A Harrier instance
    """
    from dcspy.aircraft import AV8BNA
    return AV8BNA(lcd_mono)


@fixture()
def apache_mono(lcd_mono: LcdInfo):
    """
    Return instance of AH-64D Apache for Logitech mono LCD.

    :param lcd_mono:
    :return: AH-64D Apache instance
    """
    from dcspy.aircraft import AH64DBLKII
    return AH64DBLKII(lcd_mono)


@fixture()
def eagle_mono(lcd_mono: LcdInfo):
    """
    Return instance of F-15ESE Eagle for Logitech mono LCD.

    :param lcd_mono:
    :return: F/A-18C Hornet instance
    """
    from dcspy.aircraft import F15ESE
    return F15ESE(lcd_mono)


# <=><=><=><=><=> aircraft color <=><=><=><=><=>
@fixture()
def hornet_color(lcd_color: LcdInfo):
    """
    Return instance of F/A-18C Hornet for Logitech color LCD.

    :param lcd_color:
    :return: F/A-18C Hornet instance
    """
    from dcspy.aircraft import FA18Chornet
    return FA18Chornet(lcd_color)


@fixture()
def viper_color(lcd_color: LcdInfo):
    """
    Return instance of F16C Viper for Logitech color LCD.

    :param lcd_color:
    :return: F-16C Viper instance
    """
    from dcspy.aircraft import F16C50
    return F16C50(lcd_color)


@fixture()
def shark_color(lcd_color: LcdInfo):
    """
    Return instance of Ka-50 Black Shark II for Logitech color LCD.

    :param lcd_color:
    :return: Ka-50 Black Shark II instance
    """
    from dcspy.aircraft import Ka50
    return Ka50(lcd_color)


@fixture()
def shark3_color(lcd_color: LcdInfo):
    """
    Return instance of Ka-50 Black Shark III for Logitech color LCD.

    :param lcd_color:
    :return: Ka-50 Black Shark III instance
    """
    from dcspy.aircraft import Ka503
    return Ka503(lcd_color)


@fixture()
def hip_color(lcd_color: LcdInfo):
    """
    Return instance of Mi-8MTV2 Magnificent Eight for Logitech color LCD.

    :param lcd_color:
    :return: Mi-8MTV2 Magnificent Eight instance
    """
    from dcspy.aircraft import Mi8MT
    return Mi8MT(lcd_color)


@fixture()
def hind_color(lcd_color: LcdInfo):
    """
    Return instance of Mi-24P Hind for Logitech color LCD.

    :param lcd_color:
    :return: Mi-24P Hind instance
    """
    from dcspy.aircraft import Mi24P
    return Mi24P(lcd_color)


@fixture()
def warthog_color(lcd_color: LcdInfo):
    """
    Return instance of A-10C II Tank Killer for Logitech color LCD.

    :param lcd_color:
    :return: A-10C II Tank Killer instance
    """
    from dcspy.aircraft import A10C
    return A10C(lcd_color)


@fixture()
def warthog2_color(lcd_color: LcdInfo):
    """
    Return instance of A-10C Warthog for Logitech color LCD.

    :param lcd_color:
    :return: A-10C II Tank Killer instance
    """
    from dcspy.aircraft import A10C2
    return A10C2(lcd_color)


@fixture()
def tomcata_color(lcd_color: LcdInfo):
    """
    Return instance of F-14A-135-GR Tomcat for Logitech color LCD.

    :param lcd_color:
    :return: F-14A-135-GR Tomcat instance
    """
    from dcspy.aircraft import F14A135GR
    return F14A135GR(lcd_color)


@fixture()
def tomcatb_color(lcd_color: LcdInfo):
    """
    Return instance of F-14B Tomcat for Logitech color LCD.

    :param lcd_color:
    :return: F-14B Tomcat instance
    """
    from dcspy.aircraft import F14B
    return F14B(lcd_color)


@fixture()
def harrier_color(lcd_color: LcdInfo):
    """
    Return instance of AV-8B N/A Harrier for Logitech color LCD.

    :param lcd_color:
    :return: AV-8B N/A Harrier instance
    """
    from dcspy.aircraft import AV8BNA
    return AV8BNA(lcd_color)


@fixture()
def apache_color(lcd_color: LcdInfo):
    """
    Return instance of AH-64D Apache for Logitech color LCD.

    :param lcd_color:
    :return: AH-64D Apache instance
    """
    from dcspy.aircraft import AH64DBLKII
    return AH64DBLKII(lcd_color)


@fixture()
def eagle_color(lcd_color: LcdInfo):
    """
    Return instance of F-15ESE Eagle for Logitech color LCD.

    :param lcd_color:
    :return: F/A-18C Hornet instance
    """
    from dcspy.aircraft import F15ESE
    return F15ESE(lcd_color)


# <=><=><=><=><=> logitech <=><=><=><=><=>
@fixture()
def keyboard_base(protocol_parser):
    """
    Return instance of LogitechKeyboard.

    :param protocol_parser: instance of ProtocolParser
    :return: LogitechKeyboard
    """
    from dcspy.logitech import LogitechKeyboard
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        return LogitechKeyboard(protocol_parser)


@fixture()
def keyboard_mono(protocol_parser):
    """
    Return instance of KeyboardMono.

    :param protocol_parser: instance of ProtocolParser
    :return: KeyboardMono
    """
    from dcspy.logitech import KeyboardMono
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        return KeyboardMono(protocol_parser)


@fixture()
def keyboard_color(protocol_parser):
    """
    Return instance of KeyboardColor.

    :param protocol_parser: instance of ProtocolParser
    :return: KeyboardColor
    """
    from dcspy.logitech import KeyboardColor
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        return KeyboardColor(protocol_parser)


# <=><=><=><=><=> others <=><=><=><=><=>
@fixture()
def sock():
    """Socket mock instance."""
    return MagicMock()


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


@fixture()
def apache_pre_mode_bios_data():
    """Bios values for AH-64D Apache PRE mode."""
    return [
        ('PLT_EUFD_LINE1', 'LOW ROTOR RPM     |RECTIFIER 2 FAIL  |PRESET TUNE VHF   '),
        ('PLT_EUFD_LINE2', 'ENGINE 2 OUT      |GENERATOR 2 FAIL  |!CO CMD   127.000 '),
        ('PLT_EUFD_LINE3', 'ENGINE 1 OUT      |AFT FUEL LOW      | D/1/227  135.000 '),
        ('PLT_EUFD_LINE4', '                  |FORWARD FUEL LOW  | JAAT     136.000 '),
        ('PLT_EUFD_LINE5', '                  |                  | BDE/HIG  127.000 '),
        ('PLT_EUFD_LINE6', '                                     | FAAD     125.000 '),
        ('PLT_EUFD_LINE7', '                                     | JTAC     121.000 '),
        ('PLT_EUFD_LINE8', '~<>VHF*  127.000   -----             | AWACS    141.000 '),
        ('PLT_EUFD_LINE9', ' ==UHF*  305.000   -----             | FLIGHT   128.000 '),
        ('PLT_EUFD_LINE10', ' ==FM1*   30.000   -----    NORM     | BATUMI   126.000 '),
        ('PLT_EUFD_LINE11', ' ==FM2*   30.000   -----             | COMMAND  137.000 ')
    ]


@fixture()
def hornet_mono_bios():
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
        ('IFEI_FUEL_UP', '234567')
    ]


@fixture()
def hornet_color_bios(hornet_mono_bios):
    """Bios values for F/A-18C Hornet for Logitech color LCD."""
    return hornet_mono_bios


@fixture()
def viper_mono_bios():
    """Bios values for F16C Viper for Logitech mono LCD."""
    return [
        ('DED_LINE_1', "  INS  08.0/ 6        1a "),
        ('DED_LINE_2', "  LAT *N 43o06.2'*       @"),
        ('DED_LINE_3', "  LNG  E040o34.2'        "),
        ('DED_LINE_4', " SALT      74FT          "),
        ('DED_LINE_5', " THDG   25.0o   G/S    0 "),
    ]


@fixture()
def viper_color_bios(viper_mono_bios):
    """Bios values for F16C Viper for Logitech color LCD."""
    return viper_mono_bios


@fixture()
def shark_mono_bios():
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
        ('AP_PITCH_HOLD_LED', 1)
    ]


@fixture()
def shark_color_bios(shark_mono_bios):
    """Bios values for Ka-50 Black Shark II for Logitech color LCD."""
    return shark_mono_bios


@fixture()
def shark3_mono_bios(shark_mono_bios):
    """Bios values for Ka-50 Black Shark III for Logitech mono LCD."""
    return shark_mono_bios


@fixture()
def shark3_color_bios(shark_mono_bios):
    """Bios values for Ka-50 Black Shark III for Logitech color LCD."""
    return shark_mono_bios


@fixture()
def hip_mono_bios():
    """Bios values for Mi-8MTV2 Magnificent Eight for Logitech mono LCD."""
    return [
        ('LMP_AP_HDG_ON', 1),
        ('LMP_AP_PITCH_ROLL_ON', 0),
        ('LMP_AP_HEIGHT_ON', 1),
        ('R863_CNL_SEL', 9),
        ('R863_MOD', 1),
        ('R863_FREQ', "123.525"),
        ('R828_PRST_CHAN_SEL', 9),
        ('YADRO1A_FREQ', "09091.9"),
    ]


@fixture()
def hip_color_bios(hip_mono_bios):
    """Bios values for Mi-8MTV2 Magnificent Eight for Logitech color LCD."""
    return hip_mono_bios


@fixture()
def hind_mono_bios():
    """Bios values for Mi-24P Hind for Logitech mono LCD."""
    return [
        ('PLT_R863_CHAN', 9),
        ('PLT_R863_MODUL', 1),
        ('PLT_R828_CHAN', 9),
        ('JADRO_FREQ', "08082.8"),
        ('PLT_SAU_HOVER_MODE_ON_L', 1),
        ('PLT_SAU_ROUTE_MODE_ON_L', 0),
        ('PLT_SAU_ALT_MODE_ON_L', 1),
        ('PLT_SAU_H_ON_L', 0),
        ('PLT_SAU_K_ON_L', 0),
        ('PLT_SAU_T_ON_L', 0),
        ('PLT_SAU_B_ON_L', 1),
    ]


@fixture()
def hind_color_bios(hind_mono_bios):
    """Bios values for Mi-24P Hind for Logitech color LCD."""
    return hind_mono_bios


@fixture()
def apache_mono_bios():
    """Bios values for AH-64D Apache for Logitech mono LCD."""
    return [
        ('PLT_EUFD_LINE8', '~<>VHF*  121.000   -----              121.500   -----   '),
        ('PLT_EUFD_LINE9', ' ==UHF*  305.000   -----              305.000   -----   '),
        ('PLT_EUFD_LINE10', ' ==FM1*   30.000   -----    NORM       30.000   -----   '),
        ('PLT_EUFD_LINE11', ' ==FM2*   30.000   -----               30.000   -----   '),
        ('PLT_EUFD_LINE12', ' ==HF *    2.0000A -----    LOW         2.0000A -----   ')
    ]


@fixture()
def apache_color_bios(apache_mono_bios):
    """Bios values for AH-64D Apache for Logitech color LCD."""
    return apache_mono_bios


@fixture()
def warthog_mono_bios():
    """Bios values for A-10C Warthog for Logitech mono LCD."""
    return [
        ('VHFAM_FREQ1', '20'),
        ('VHFAM_FREQ2', 1),
        ('VHFAM_FREQ3', 1),
        ('VHFAM_FREQ4', '30'),
        ('VHFFM_FREQ1', '40'),
        ('VHFFM_FREQ2', 2),
        ('VHFFM_FREQ3', 2),
        ('VHFFM_FREQ4', '50'),
        ('UHF_100MHZ_SEL', '5'),
        ('UHF_10MHZ_SEL', 3),
        ('UHF_1MHZ_SEL', 2),
        ('UHF_POINT1MHZ_SEL', 1),
        ('UHF_POINT25_SEL', '25')
    ]


@fixture()
def warthog_color_bios(warthog_mono_bios):
    """Bios values for A-10C Warthog for Logitech color LCD."""
    return warthog_mono_bios


@fixture()
def warthog2_mono_bios(warthog_mono_bios):
    """Bios values for A-10C II Tank Killer for Logitech mono LCD."""
    return warthog_mono_bios


@fixture()
def warthog2_color_bios(warthog_mono_bios):
    """Bios values for A-10C II Tank Killer for Logitech color LCD."""
    return warthog_mono_bios


@fixture()
def harrier_mono_bios():
    """Bios values for AV-8B N/A Harrier for Logitech mono LCD."""
    return [
        ('UFC_SCRATCHPAD', '123456789012'),
        ('UFC_COMM1_DISPLAY', '11'),
        ('UFC_COMM2_DISPLAY', '22'),
        ('AV8BNA_ODU_1_SELECT', '1'),
        ('AV8BNA_ODU_1_Text', '1234'),
        ('AV8BNA_ODU_2_SELECT', '2'),
        ('AV8BNA_ODU_2_Text', '2345'),
        ('AV8BNA_ODU_3_SELECT', '3'),
        ('AV8BNA_ODU_3_Text', '3456'),
        ('AV8BNA_ODU_4_SELECT', '4'),
        ('AV8BNA_ODU_4_Text', '4567'),
        ('AV8BNA_ODU_5_SELECT', '5'),
        ('AV8BNA_ODU_5_Text', '5678')
    ]


@fixture()
def harrier_color_bios(harrier_mono_bios):
    """Bios values for AV-8B N/A Harrier for Logitech color LCD."""
    return harrier_mono_bios


@fixture()
def tomcata_mono_bios():
    """Bios values for F-14A-135-GR Tomcat for Logitech mono LCD."""
    return []


@fixture()
def tomcata_color_bios(tomcata_mono_bios):
    """Bios values for F-14A-135-GR Tomcat for Logitech color LCD."""
    return tomcata_mono_bios


@fixture()
def tomcatb_mono_bios(tomcata_mono_bios):
    """Bios values for F-14B Tomcat for Logitech mono LCD."""
    return tomcata_mono_bios


@fixture()
def tomcatb_color_bios(tomcata_mono_bios):
    """Bios values for F-14B Tomcat for Logitech color LCD."""
    return tomcata_mono_bios
