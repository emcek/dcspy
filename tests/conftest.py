from dcspy import LcdColor, LcdMono, LcdSize

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
    :rtype: LcdSize
    """
    return LcdMono


@fixture()
def lcd_color() -> LcdSize:
    """
    Return of color LCD.

    :return: color lcd type
    :rtype: LcdSize
    """
    return LcdColor


@fixture()
def hornet_mono(lcd_mono: LcdSize):
    """
    Return instance of F/A-18C Hornet for Logitech mono LCD.
    :param lcd_mono:
    :return: F/A-18C Hornet instance
    :rtype: FA18Chornet
    """
    from dcspy.aircrafts import FA18Chornet
    return FA18Chornet(lcd_mono)


@fixture()
def black_shark_mono(lcd_mono: LcdSize):
    """
    Return instance of Ka-50 Black Shark for Logitech mono LCD.
    :param lcd_mono:
    :return: Ka-50 Black Shark instance
    :rtype: Ka50
    """
    from dcspy.aircrafts import Ka50
    return Ka50(lcd_mono)


@fixture()
def tomcat_mono(lcd_mono: LcdSize):
    """
    Return instance of F-14B Tomcat for Logitech mono LCD.
    :param lcd_mono:
    :return: F-14B Tomcat instance
    :rtype: F14B
    """
    from dcspy.aircrafts import F14B
    return F14B(lcd_mono)
