from unittest.mock import patch


def test_check_g13_has_aircraft_member():
    from dcspy.logitech import G13
    from dcspy.dcsbios import ProtocolParser
    from dcspy.aircrafts import Aircraft
    from dcspy.sdk import lcd_sdk

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        g = G13(ProtocolParser())
        assert isinstance(g.plane, Aircraft)
