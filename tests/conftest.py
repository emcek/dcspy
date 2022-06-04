from unittest.mock import patch, MagicMock

from pytest import fixture

from dcspy import LcdInfo


# <=><=><=><=><=> dcsbios <=><=><=><=><=>
@fixture
def protocol_parser():
    """Basic instance of ProtocolParser"""
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
def black_shark_mono(lcd_mono: LcdInfo):
    """
    Return instance of Ka-50 Black Shark for Logitech mono LCD.
    :param lcd_mono:
    :return: Ka-50 Black Shark instance
    """
    from dcspy.aircraft import Ka50
    return Ka50(lcd_mono)


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
def tomcat_mono(lcd_mono: LcdInfo):
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
def black_shark_color(lcd_color: LcdInfo):
    """
    Return instance of Ka-50 Black Shark for Logitech color LCD.
    :param lcd_color:
    :return: Ka-50 Black Shark instance
    """
    from dcspy.aircraft import Ka50
    return Ka50(lcd_color)


@fixture()
def warthog_color(lcd_color: LcdInfo):
    """
    Return instance of A-10C II Tank Killer for Logitech mono LCD.
    :param lcd_color:
    :return: A-10C II Tank Killer instance
    """
    from dcspy.aircraft import A10C2
    return A10C2(lcd_color)


@fixture()
def tomcat_color(lcd_color: LcdInfo):
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


# <=><=><=><=><=> logitech <=><=><=><=><=>
@fixture()
def keyboard_base(protocol_parser):
    from dcspy.logitech import LogitechKeyboard
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        return LogitechKeyboard(protocol_parser)


@fixture()
def keyboard_mono(protocol_parser):
    from dcspy.logitech import KeyboardMono
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        return KeyboardMono(protocol_parser)


@fixture()
def keyboard_color(protocol_parser):
    from dcspy.logitech import KeyboardColor
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        return KeyboardColor(protocol_parser)


# <=><=><=><=><=> others <=><=><=><=><=>
@fixture()
def sock():
    return MagicMock()
