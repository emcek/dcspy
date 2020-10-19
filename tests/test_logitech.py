from unittest.mock import patch


def test_check_keyboard_mono_has_aircraft_member():
    from dcspy.logitech import KeyboardMono
    from dcspy.dcsbios import ProtocolParser
    from dcspy.aircrafts import Aircraft
    from dcspy import lcd_sdk
    from dcspy import LcdSize

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        mono = KeyboardMono(ProtocolParser())
        assert isinstance(mono.plane, Aircraft)
        assert isinstance(mono.lcd, LcdSize)
        assert mono.lcd.type == lcd_sdk.TYPE_MONO


def test_check_keyboard_color_has_aircraft_member():
    from dcspy.logitech import KeyboardColor
    from dcspy.dcsbios import ProtocolParser
    from dcspy.aircrafts import Aircraft
    from dcspy import lcd_sdk
    from dcspy import LcdSize

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        color = KeyboardColor(ProtocolParser())
        assert isinstance(color.plane, Aircraft)
        assert isinstance(color.lcd, LcdSize)
        assert color.lcd.type == lcd_sdk.TYPE_COLOR
