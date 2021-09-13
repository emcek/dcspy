from unittest.mock import patch, MagicMock

from dcspy import LcdSize

from pytest import fixture


# <=><=><=><=><=> dcsbios <=><=><=><=><=>
@fixture
def protocol_parser():
    """Basic instance of ProtocolParser"""
    from dcspy.dcsbios import ProtocolParser
    return ProtocolParser()


# <=><=><=><=><=> aircrafts <=><=><=><=><=>
@fixture()
def lcd_mono() -> LcdSize:
    """
    Return of mono LCD.

    :return: mono lcd type
    """
    from dcspy import LcdMono
    return LcdMono


@fixture()
def lcd_color() -> LcdSize:
    """
    Return of color LCD.

    :return: color lcd type
    """
    from dcspy import LcdColor
    return LcdColor


@fixture()
def aircraft(lcd_mono: LcdSize):
    """
    Return instance of Aircraft base class for Logitech mono LCD.
    :param lcd_mono:
    :return: Aircraft instance
    """
    from dcspy.aircrafts import Aircraft
    return Aircraft(lcd_mono)


@fixture()
def hornet_mono(lcd_mono: LcdSize):
    """
    Return instance of F/A-18C Hornet for Logitech mono LCD.
    :param lcd_mono:
    :return: F/A-18C Hornet instance
    """
    from dcspy.aircrafts import FA18Chornet
    return FA18Chornet(lcd_mono)


@fixture()
def black_shark_mono(lcd_mono: LcdSize):
    """
    Return instance of Ka-50 Black Shark for Logitech mono LCD.
    :param lcd_mono:
    :return: Ka-50 Black Shark instance
    """
    from dcspy.aircrafts import Ka50
    return Ka50(lcd_mono)


@fixture()
def tomcat_mono(lcd_mono: LcdSize):
    """
    Return instance of F-14B Tomcat for Logitech mono LCD.
    :param lcd_mono:
    :return: F-14B Tomcat instance
    """
    from dcspy.aircrafts import F14B
    return F14B(lcd_mono)


@fixture()
def viper_mono(lcd_mono: LcdSize):
    """
    Return instance of F16C Viper for Logitech mono LCD.
    :param lcd_mono:
    :return: F-16C Viper instance
    """
    from dcspy.aircrafts import F16C50
    return F16C50(lcd_mono)


@fixture()
def hornet_color(lcd_color: LcdSize):
    """
    Return instance of F/A-18C Hornet for Logitech color LCD.
    :param lcd_color:
    :return: F/A-18C Hornet instance
    """
    from dcspy.aircrafts import FA18Chornet
    return FA18Chornet(lcd_color)


@fixture()
def black_shark_color(lcd_color: LcdSize):
    """
    Return instance of Ka-50 Black Shark for Logitech color LCD.
    :param lcd_color:
    :return: Ka-50 Black Shark instance
    """
    from dcspy.aircrafts import Ka50
    return Ka50(lcd_color)


@fixture()
def tomcat_color(lcd_color: LcdSize):
    """
    Return instance of F-14B Tomcat for Logitech color LCD.
    :param lcd_color:
    :return: F-14B Tomcat instance
    """
    from dcspy.aircrafts import F14B
    return F14B(lcd_color)


# <=><=><=><=><=> logitech <=><=><=><=><=>
@fixture()
def keyboard_base(protocol_parser):
    from dcspy.logitech import LogitechKeyboard
    from dcspy import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        return LogitechKeyboard(protocol_parser)


@fixture()
def keyboard_mono(protocol_parser):
    from dcspy.logitech import KeyboardMono
    from dcspy import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        return KeyboardMono(protocol_parser)


@fixture()
def keyboard_color(protocol_parser):
    from dcspy.logitech import KeyboardColor
    from dcspy import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        return KeyboardColor(protocol_parser)


@fixture()
def sock():
    return MagicMock()
