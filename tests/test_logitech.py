from unittest.mock import call, patch

from pytest import mark

from dcspy import LcdButton, LcdMode, LcdType
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


@mark.parametrize('keyboard, pressed1, effect, chk_btn, calls, pressed2', [
    ('keyboard_mono', False, [False] * 3 + [True], LcdButton.FOUR, [call(1), call(2), call(4), call(8)], True),
    ('keyboard_color', False, [False] * 4 + [True] + [False] * 2, LcdButton.OK, [call(256), call(512), call(4096), call(8192), call(1024)], True),
    ('keyboard_mono', True, [True, False, False, False], LcdButton.NONE, [call(1)], True),
    ('keyboard_color', True, [True] + [False] * 6, LcdButton.NONE, [call(256)], True),
    ('keyboard_mono', False, [False] * 4, LcdButton.NONE, [call(1), call(2), call(4), call(8)], False),
    ('keyboard_color', False, [False] * 8, LcdButton.NONE, [call(256), call(512), call(4096), call(8192), call(1024), call(2048), call(16384)], False),
], ids=['Mono 4 Button', 'Color Ok Button', 'Mono None already_pressed', 'Color None already_pressed', 'Mono None Button', 'Color None Button'])
def test_keyboard_mono_check_buttons(keyboard, pressed1, effect, chk_btn, calls, pressed2, request):
    from dcspy.sdk import lcd_sdk
    keyboard = request.getfixturevalue(keyboard)
    keyboard.already_pressed = pressed1
    with patch.object(lcd_sdk, 'logi_lcd_is_button_pressed', side_effect=effect) as lcd_btn_pressed:
        assert keyboard.check_buttons() == chk_btn
    lcd_btn_pressed.assert_has_calls(calls)
    assert keyboard.already_pressed is pressed2


@mark.parametrize('keyboard', ['keyboard_mono', 'keyboard_color'], ids=['Mono Keyboard', 'Color Keyboard'])
def test_keyboard_color_button_handle(keyboard, sock, request):
    from dcspy.sdk import lcd_sdk
    keyboard = request.getfixturevalue(keyboard)
    with patch.object(lcd_sdk, 'logi_lcd_is_button_pressed', side_effect=[True]):
        keyboard.button_handle(sock)
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
    ('F14A135GR', 'F14A135GR', ['Detected aircraft:', 'F-14A Tomcat'], True),
    ('F-14B', 'F14B', ['Detected aircraft:', 'F-14B Tomcat'], True),
    ('AV8BNA', 'AV8BNA', ['Detected aircraft:', 'AV-8B N/A Harrier'], True),
    ('F-117_Nighthawk', 'F117Nighthawk', ['Detected aircraft:', 'F117Nighthawk', 'Not supported yet!'], False),
    ('', '', [], False),
], ids=['FA-18 Hornet',
        'F-16C Viper',
        'Ka-50 Black Shark II',
        'Ka-50 Black Shark III',
        'Mi-8MT Hip',
        'Mi-24P Hind',
        'AH-64D Apache',
        'A-10C Warthog',
        'A-10C II Tank Killer',
        'F-14A',
        'F-14B',
        'AV-8B N/A Harrier',
        'F-117 Nighthawk',
        'Empty'])
def test_keyboard_mono_detecting_plane(plane_str, plane, display, detect, keyboard_mono):
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
        keyboard_mono.detecting_plane(plane_str)
    assert keyboard_mono.plane_name == plane
    assert keyboard_mono._display == display
    assert keyboard_mono.plane_detected is detect


@mark.parametrize('mode, size,  lcd_type, keyboard', [
    (LcdMode.BLACK_WHITE, (160, 43), LcdType.MONO, KeyboardMono),
    (LcdMode.TRUE_COLOR, (320, 240), LcdType.COLOR, KeyboardColor)
], ids=['Mono Keyboard', 'Color Keyboard'])
def test_check_keyboard_display_and_prepare_image(mode, size, lcd_type, keyboard, protocol_parser):
    from dcspy import LcdInfo
    from dcspy.aircraft import Aircraft
    from dcspy.sdk import lcd_sdk

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
    assert img.mode == mode.value
    assert img.size == size


@mark.parametrize('keyboard', [KeyboardMono, KeyboardColor], ids=['Mono Keyboard', 'Color Keyboard'])
def test_check_keyboard_text(keyboard, protocol_parser):
    from dcspy.sdk import lcd_sdk

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        keyboard = keyboard(protocol_parser)

    with patch.object(lcd_sdk, 'update_text', return_value=True) as upd_txt:
        keyboard.text(['1', '2'])
        upd_txt.assert_called()


@mark.parametrize('model', all_plane_list, ids=[
    'FA-18 Hornet',
    'F-16C Viper',
    'Ka-50 Black Shark II',
    'Ka-50 Black Shark III',
    'Mi-8MT Hip',
    'Mi-24P Hind',
    'AH-64D Apache',
    'A-10C Warthog',
    'A-10C II Tank Killer',
    'F-14A',
    'F-14B',
    'AV-8B N/A Harrier'])
def test_keyboard_mono_load_plane(model, keyboard_mono):
    from dcspy.aircraft import Aircraft
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
        keyboard_mono.plane_name = model
        keyboard_mono.load_new_plane()
    assert isinstance(keyboard_mono.plane, Aircraft)
    assert model in keyboard_mono.plane.__class__.__name__
