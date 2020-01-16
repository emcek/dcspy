from typing import Tuple

from pytest import fixture


# <=><=><=><=><=> dcsbios <=><=><=><=><=>
@fixture
def protocol_parser():
    """Basic instance of ProtocolParser"""
    from dcspy.dcsbios import ProtocolParser
    return ProtocolParser()


# <=><=><=><=><=> aircrafts <=><=><=><=><=>
@fixture()
def lcd_size() -> Tuple[int, int]:
    """
    Return width and height of G13 LCD as tuple of integers.

    :return: width and height
    :rtype: Tuple[int, int]
    """
    from dcspy.sdk.lcd_sdk import MONO_WIDTH, MONO_HEIGHT
    return MONO_WIDTH, MONO_HEIGHT


@fixture()
def hornet(lcd_size: Tuple[int, int]):
    """
    Return instance of F/A-18C Hornet for Logitech G13.
    :param lcd_size:
    :return: F/A-18C Hornet instance
    :rtype: FA18Chornet
    """
    from dcspy.aircrafts import FA18Chornet
    return FA18Chornet(*lcd_size)


@fixture()
def black_shark(lcd_size: Tuple[int, int]):
    """
    Return instance of Ka-50 Black Shark for Logitech G13.
    :param lcd_size:
    :return: Ka-50 Black Shark instance
    :rtype: Ka50
    """
    from dcspy.aircrafts import Ka50
    return Ka50(*lcd_size)
