from unittest.mock import call, patch

from pytest import mark, raises

from dcspy.logitech import KeyboardColor, KeyboardMono


def test_keyboard_base_basic_check(keyboard_base):
    from dcspy import lcd_sdk
    with raises(NotImplementedError):
        keyboard_base._prepare_image()

    assert str(keyboard_base) == 'LogitechKeyboard: 160x43'
    logitech_repr = repr(keyboard_base)
    data = ('parser', 'ProtocolParser', 'plane_name', 'plane_detected', 'already_pressed', 'buttons',
            '_display', 'plane', 'Aircraft')
    for test_string in data:
        assert test_string in logitech_repr

    with patch.object(lcd_sdk, 'clear_display', return_value=True):
        keyboard_base.clear()


@mark.parametrize('pressed1, effect, chk_btn, calls, pressed2',
                  [(False, [False, False, False, True], 4, [call(1), call(2), call(4), call(8)], True),
                   (True, [True, False, False, False], 0, [call(1)], True),
                   (False, [False, False, False, False], 0, [call(1), call(2), call(4), call(8)], False)])
def test_keyboard_mono_check_buttons(pressed1, effect, chk_btn, calls, pressed2, keyboard_mono):
    from dcspy import lcd_sdk
    keyboard_mono.already_pressed = pressed1
    with patch.object(lcd_sdk, 'logi_lcd_is_button_pressed', side_effect=effect) as lcd_btn_pressed:
        assert keyboard_mono.check_buttons() == chk_btn
    lcd_btn_pressed.assert_has_calls(calls)
    assert keyboard_mono.already_pressed is pressed2


def test_keyboard_color_button_handle(keyboard_color, sock):
    from dcspy import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_button_pressed', side_effect=[True]):
        keyboard_color.button_handle(sock)
    sock.sendto.assert_called_once_with(b'\n', ('127.0.0.1', 7778))


@mark.parametrize('plane_str, plane, display, detect', [('FA-18C_hornet', 'FA18Chornet', [], True),
                                                        ('F-114_Nighthawk', 'F114Nighthawk', ['Not supported yet!'], False)])
def test_keyboard_mono_detecting_plane(plane_str, plane, display, detect, keyboard_mono):
    from dcspy import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
        with patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                keyboard_mono.detecting_plane(plane_str)
    assert keyboard_mono.plane_name == plane
    assert keyboard_mono._display == ['Detected aircraft:'] + [plane] + display
    assert keyboard_mono.plane_detected is detect


@mark.parametrize('mode, size, lcd_type, keyboard', [('1', (160, 43), 1, KeyboardMono),
                                                     ('RGBA', (320, 240), 2, KeyboardColor)])
def test_check_keyboard_display_and_prepare_image(mode, size, lcd_type, keyboard, protocol_parser):
    from dcspy.aircrafts import Aircraft
    from dcspy import lcd_sdk
    from dcspy import LcdSize

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        keyboard = keyboard(protocol_parser)
    assert isinstance(keyboard.plane, Aircraft)
    assert isinstance(keyboard.lcd, LcdSize)
    assert keyboard.lcd.type == lcd_type
    assert isinstance(keyboard.display, list)
    with patch.object(lcd_sdk, 'update_display', return_value=True):
        keyboard.display = ['1', '2']
        assert len(keyboard.display) == 2
    img = keyboard._prepare_image()
    assert img.mode == mode
    assert img.size == size
