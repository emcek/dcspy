from typing import Tuple

from pytest import fixture


# <=><=><=><=><=> dcsbios <=><=><=><=><=>
@fixture
def protocol_parser():
    """Basic instance of ProtocolParser"""
    from dcspy.dcs.bios import ProtocolParser
    return ProtocolParser()


# <=><=><=><=><=> aircrafts <=><=><=><=><=>
@fixture()
def lcd_size() -> Tuple[int, int]:
    """
    Return width and height of mono LCD as tuple of integers.

    :return: width and height
    :rtype: Tuple[int, int]
    """
    from dcspy.lcd_sdk import MONO_WIDTH, MONO_HEIGHT
    return MONO_WIDTH, MONO_HEIGHT


@fixture()
def hornet(lcd_size: Tuple[int, int]):
    """
    Return instance of F/A-18C Hornet for Logitech mono LCD.
    :param lcd_size:
    :return: F/A-18C Hornet instance
    :rtype: FA18Chornet
    """
    from dcspy.dcs.aircrafts import FA18Chornet
    return FA18Chornet(*lcd_size)


@fixture()
def black_shark(lcd_size: Tuple[int, int]):
    """
    Return instance of Ka-50 Black Shark for Logitech mono LCD.
    :param lcd_size:
    :return: Ka-50 Black Shark instance
    :rtype: Ka50
    """
    from dcspy.dcs.aircrafts import Ka50
    return Ka50(*lcd_size)


@fixture()
def tomcat(lcd_size: Tuple[int, int]):
    """
    Return instance of F-14B Tomcat for Logitech mono LCD.
    :param lcd_size:
    :return: F-14B Tomcat instance
    :rtype: F14B
    """
    from dcspy.dcs.aircrafts import F14B
    return F14B(*lcd_size)
