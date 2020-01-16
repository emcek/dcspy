from pytest import fixture


@fixture
def protocol_parser():
    """Empty instance of ProtocolParser"""
    from dcspy.dcsbios import ProtocolParser
    return ProtocolParser()
