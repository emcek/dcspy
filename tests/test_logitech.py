from unittest.mock import patch


def test_check_keyboard_mono_has_aircraft_member():
    from dcspy.logitech import KeyboardMono
    from dcspy.dcsbios import ProtocolParser
    from dcspy.aircrafts import Aircraft
    from dcspy import lcd_sdk

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        lcd = KeyboardMono(ProtocolParser())
        assert isinstance(lcd.plane, Aircraft)


def test_check_keyboard_color_has_aircraft_member():
    from dcspy.logitech import KeyboardColor
    from dcspy.dcsbios import ProtocolParser
    from dcspy.aircrafts import Aircraft
    from dcspy import lcd_sdk

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        lcd = KeyboardColor(ProtocolParser())
        assert isinstance(lcd.plane, Aircraft)
