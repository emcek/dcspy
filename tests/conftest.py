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
