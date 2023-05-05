from unittest.mock import call, patch

from pytest import mark

from dcspy import LcdType, LcdButton
from dcspy.logitech import KeyboardColor, KeyboardMono
from tests.helpers import all_plane_list


def test_keyboard_base_basic_check(keyboard_base):
    from dcspy.sdk import lcd_sdk

    assert str(keyboard_base) == 'LogitechKeyboard: 160x43'
    logitech_repr = repr(keyboard_base)
    data = ('parser', 'ProtocolParser', 'plane_name', 'plane_detected', 'already_pressed', 'buttons',
            '_display', 'plane', 'Aircraft', 'vert_space', 'lcd')
    for test_string in data:
        assert test_string in logitech_repr

    with patch.object(lcd_sdk, 'clear_display', return_value=True):
        keyboard_base.clear()


@mark.parametrize('pressed1, effect, chk_btn, calls, pressed2', [
    (False, [False, False, False, True], LcdButton.FOUR, [call(1), call(2), call(4), call(8)], True),
    (True, [True, False, False, False], LcdButton.NONE, [call(1)], True),
    (False, [False, False, False, False], LcdButton.NONE, [call(1), call(2), call(4), call(8)], False),
])
def test_keyboard_mono_check_buttons(pressed1, effect, chk_btn, calls, pressed2, keyboard_mono):
    from dcspy.sdk import lcd_sdk
    keyboard_mono.already_pressed = pressed1
    with patch.object(lcd_sdk, 'logi_lcd_is_button_pressed', side_effect=effect) as lcd_btn_pressed:
        assert keyboard_mono.check_buttons() == chk_btn
    lcd_btn_pressed.assert_has_calls(calls)
    assert keyboard_mono.already_pressed is pressed2


def test_keyboard_color_button_handle(keyboard_color, sock):
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_button_pressed', side_effect=[True]):
        keyboard_color.button_handle(sock)
    sock.sendto.assert_called_once_with(b'\n', ('127.0.0.1', 7778))


@mark.parametrize('plane_str, plane, display, detect', [
    ('FA-18C_hornet', 'FA18Chornet', ['Detected aircraft:', 'F/A-18C Hornet'], True),
    ('F-16C_50', 'F16C50', ['Detected aircraft:', 'F-16C Viper'], True),
    ('Ka-50', 'Ka50', ['Detected aircraft:', 'Ka-50 Black Shark II'], True),
    ('Ka-503', 'Ka503', ['Detected aircraft:', 'Ka-50 Black Shark III'], True),
    ('Mi-8MT', 'Mi8MT', ['Detected aircraft:', 'Mi-8MTV2 Magnificent Eight'], True),
    ('Mi-24P', 'Mi24P', ['Detected aircraft:', 'Mi-24P Hind'], True),
    ('AH-64D_BLKII', 'AH64DBLKII', ['Detected aircraft:', 'AH-64D Apache'], True),
    ('A-10C', 'A10C', ['Detected aircraft:', 'A-10C Warthog'], True),
    ('A-10C_2', 'A10C2', ['Detected aircraft:', 'A-10C II Tank Killer'], True),
    ('F-14B', 'F14B', ['Detected aircraft:', 'F-14B Tomcat'], True),
    ('F14A135GR', 'F14A135GR', ['Detected aircraft:', 'F-14A Tomcat'], True),
    ('AV8BNA', 'AV8BNA', ['Detected aircraft:', 'AV-8B N/A Harrier'], True),
    ('F-117_Nighthawk', 'F117Nighthawk', ['Detected aircraft:', 'F117Nighthawk', 'Not supported yet!'], False),
    ('', '', [], False),
])
def test_keyboard_mono_detecting_plane(plane_str, plane, display, detect, keyboard_mono):
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
        keyboard_mono.detecting_plane(plane_str)
    assert keyboard_mono.plane_name == plane
    assert keyboard_mono._display == display
    assert keyboard_mono.plane_detected is detect


@mark.parametrize('mode, size,  lcd_type, keyboard', [('1', (160, 43), LcdType.MONO, KeyboardMono),
                                                      ('RGBA', (320, 240), LcdType.COLOR, KeyboardColor)])
def test_check_keyboard_display_and_prepare_image(mode, size, lcd_type, keyboard, protocol_parser):
    from dcspy.aircraft import Aircraft
    from dcspy.sdk import lcd_sdk
    from dcspy import LcdInfo

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        keyboard = keyboard(protocol_parser)
    assert isinstance(keyboard.plane, Aircraft)
    assert isinstance(keyboard.lcd, LcdInfo)
    assert keyboard.lcd.type == lcd_type
    assert isinstance(keyboard.display, list)
    with patch.object(lcd_sdk, 'update_display', return_value=True):
        keyboard.display = ['1', '2']
        assert len(keyboard.display) == 2

    img = keyboard._prepare_image()
    assert img.mode == mode
    assert img.size == size


@mark.parametrize('keyboard', [KeyboardMono, KeyboardColor])
def test_check_keyboard_text(keyboard, protocol_parser):
    from dcspy.sdk import lcd_sdk

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        keyboard = keyboard(protocol_parser)

    with patch.object(lcd_sdk, 'update_text', return_value=True) as upd_txt:
        keyboard.text(['1', '2'])
        upd_txt.assert_called()


@mark.parametrize('model', all_plane_list)
def test_keyboard_mono_load_plane(model, keyboard_mono):
    from dcspy.sdk import lcd_sdk
    from dcspy.aircraft import Aircraft
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
        keyboard_mono.plane_name = model
        keyboard_mono.load_new_plane()
    assert isinstance(keyboard_mono.plane, Aircraft)
    assert model in keyboard_mono.plane.__class__.__name__
