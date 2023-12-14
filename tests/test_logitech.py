from unittest.mock import call, patch

from pytest import mark

from dcspy.logitech import G13, G19, G510, G15v1, G15v2
from dcspy.models import DEFAULT_FONT_NAME, FontsConfig, Gkey, LcdButton, LcdInfo, LcdMode, LcdType


def test_keyboard_base_basic_check(keyboard_base):
    from dcspy.sdk import lcd_sdk

    assert str(keyboard_base) == 'KeyboardManager: 160x43'
    logitech_repr = repr(keyboard_base)
    data = ('parser', 'ProtocolParser', 'plane_name', 'plane_detected', 'lcdbutton_pressed', 'gkey_pressed', 'buttons',
            '_display', 'plane', 'BasicAircraft', 'vert_space', 'lcd', 'LcdInfo', 'gkey', 'buttons', 'model', 'KeyboardModel')
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
], ids=[
    'Mono 4 Button',
    'Color Ok Button',
    'Mono None already_pressed',
    'Color None already_pressed',
    'Mono None Button',
    'Color None Button'])
def test_keyboard_check_buttons(keyboard, pressed1, effect, chk_btn, calls, pressed2, request):
    from dcspy.sdk import lcd_sdk
    keyboard = request.getfixturevalue(keyboard)
    keyboard.lcdbutton_pressed = pressed1
    with patch.object(lcd_sdk, 'logi_lcd_is_button_pressed', side_effect=effect) as lcd_btn_pressed:
        assert keyboard.check_buttons() == chk_btn
    lcd_btn_pressed.assert_has_calls(calls)
    assert keyboard.lcdbutton_pressed is pressed2


@mark.parametrize('keyboard, pressed1, effect1, effect2, chk_btn, calls, pressed2', [
    ('keyboard_mono', False, [False, True], ['G1/M1', 'G2/M1'], Gkey(key=2, mode=1), [call(g_key=1, mode=1), call(g_key=2, mode=1)], True),
    ('keyboard_color', False, [False, True], ['G1/M1', 'G2/M1'], Gkey(key=2, mode=1), [call(g_key=1, mode=1), call(g_key=2, mode=1)], True),
    ('keyboard_mono', True, [True, False, False], ['G1/M1', 'G2/M1', 'G3/M1'], Gkey(key=0, mode=0), [call(g_key=1, mode=1)], True),
    ('keyboard_color', True, [True, False, False], ['G1/M1', 'G2/M1', 'G3/M1'], Gkey(key=0, mode=0), [call(g_key=1, mode=1)], True),
    ('keyboard_mono', False, [False] * 3, [str(i) for i in Gkey.generate(3, 1)], Gkey(key=0, mode=0), [call(g_key=1, mode=1), call(g_key=2, mode=1), call(g_key=3, mode=1)], False),
    ('keyboard_color', False, [False] * 3, [str(i) for i in Gkey.generate(3, 1)], Gkey(key=0, mode=0), [call(g_key=1, mode=1), call(g_key=2, mode=1), call(g_key=3, mode=1)], False),
], ids=['Mono G2/M1', 'color G2/M1', 'Mono G1/M1 already_pressed', 'Color G1/M1 already_pressed', 'Mono None Button', 'Color None Button'])
def test_keyboard_check_gkey(keyboard, pressed1, effect1, effect2, chk_btn, calls, pressed2, request):
    from dcspy.sdk import key_sdk
    keyboard = request.getfixturevalue(keyboard)
    keyboard.gkey_pressed = pressed1
    with patch.object(key_sdk, 'logi_gkey_is_keyboard_gkey_pressed', side_effect=effect1) as gkey_pressed, \
            patch.object(key_sdk, 'logi_gkey_is_keyboard_gkey_string', side_effect=effect2):
        assert keyboard.check_gkey() == chk_btn
    gkey_pressed.assert_has_calls(calls)
    assert keyboard.gkey_pressed is pressed2


@mark.parametrize('keyboard', ['keyboard_mono', 'keyboard_color'], ids=['Mono Keyboard', 'Color Keyboard'])
def test_keyboard_button_handle_lcdbutton(keyboard, sock, request):
    from dcspy.sdk import lcd_sdk
    keyboard = request.getfixturevalue(keyboard)
    with patch.object(lcd_sdk, 'logi_lcd_is_button_pressed', side_effect=[True]):
        keyboard.button_handle(sock)
    sock.sendto.assert_called_once_with(b'\n', ('127.0.0.1', 7778))


@mark.parametrize('keyboard', ['keyboard_mono', 'keyboard_color'], ids=['Mono Keyboard', 'Color Keyboard'])
def test_keyboard_button_handle_gkey(keyboard, sock, request):
    from dcspy.sdk import key_sdk
    keyboard = request.getfixturevalue(keyboard)
    with patch.object(key_sdk, 'logi_gkey_is_keyboard_gkey_pressed', side_effect=[True]), \
            patch.object(key_sdk, 'logi_gkey_is_keyboard_gkey_string', side_effect=['G1/M1']):
        keyboard.button_handle(sock)
    sock.sendto.assert_called_once_with(b'\n', ('127.0.0.1', 7778))


@mark.parametrize('plane_str, bios_name, plane, display, detect', [
    ('FA-18C_hornet', '', 'FA18Chornet', ['Detected aircraft:', 'F/A-18C Hornet'], True),
    ('F-16C_50', '', 'F16C50', ['Detected aircraft:', 'F-16C Viper'], True),
    ('Ka-50', '', 'Ka50', ['Detected aircraft:', 'Ka-50 Black Shark II'], True),
    ('Ka-503', '', 'Ka503', ['Detected aircraft:', 'Ka-50 Black Shark III'], True),
    ('Mi-8MT', '', 'Mi8MT', ['Detected aircraft:', 'Mi-8MTV2 Magnificent Eight'], True),
    ('Mi-24P', '', 'Mi24P', ['Detected aircraft:', 'Mi-24P Hind'], True),
    ('AH-64D_BLKII', '', 'AH64DBLKII', ['Detected aircraft:', 'AH-64D Apache'], True),
    ('A-10C', '', 'A10C', ['Detected aircraft:', 'A-10C Warthog'], True),
    ('A-10C_2', '', 'A10C2', ['Detected aircraft:', 'A-10C II Tank Killer'], True),
    ('F14A135GR', '', 'F14A135GR', ['Detected aircraft:', 'F-14A Tomcat'], True),
    ('F-14B', '', 'F14B', ['Detected aircraft:', 'F-14B Tomcat'], True),
    ('AV8BNA', '', 'AV8BNA', ['Detected aircraft:', 'AV-8B N/A Harrier'], True),
    ('SpitfireLFMkIX', 'SpitfireLFMkIX', 'SpitfireLFMkIX', ['Detected aircraft:', 'SpitfireLFMkIX'], True),
    ('F-22A', 'F-22A', 'F22A', ['Detected aircraft:', 'F-22A'], True),
    ('A-10A', '', 'A10A', ['Detected aircraft:', 'A-10A', 'Not supported yet!'], False),
    ('F-117_Nighthawk', '', 'F117Nighthawk', ['Detected aircraft:', 'F-117_Nighthawk', 'Not supported yet!'], False),
    ('', '', '', [], False),
], ids=[
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
    'AV-8B N/A Harrier',
    'SpitfireLFMkIX',
    'F-22A',
    'A-10A',
    'F-117 Nighthawk',
    'Empty'])
def test_keyboard_mono_detecting_plane(plane_str, bios_name, plane, display, detect, keyboard_mono):
    with patch('dcspy.logitech.get_planes_list', return_value=['SpitfireLFMkIX', 'F-22A']):
        keyboard_mono.detecting_plane(plane_str)
    assert keyboard_mono.plane_name == plane
    assert keyboard_mono.bios_name == bios_name
    assert keyboard_mono._display == display
    assert keyboard_mono.plane_detected is detect


@mark.parametrize('mode, size,  lcd_type, lcd_font, keyboard', [
    (LcdMode.BLACK_WHITE, (160, 43), LcdType.MONO, FontsConfig(name=DEFAULT_FONT_NAME, small=9, medium=11, large=16), G13),
    (LcdMode.BLACK_WHITE, (160, 43), LcdType.MONO, FontsConfig(name=DEFAULT_FONT_NAME, small=9, medium=11, large=16), G510),
    (LcdMode.BLACK_WHITE, (160, 43), LcdType.MONO, FontsConfig(name=DEFAULT_FONT_NAME, small=9, medium=11, large=16), G15v1),
    (LcdMode.BLACK_WHITE, (160, 43), LcdType.MONO, FontsConfig(name=DEFAULT_FONT_NAME, small=9, medium=11, large=16), G15v2),
    (LcdMode.TRUE_COLOR, (320, 240), LcdType.COLOR, FontsConfig(name=DEFAULT_FONT_NAME, small=18, medium=22, large=32), G19),
], ids=['Mono G13', 'Mono G510', 'Mono G15v1', 'Mono G15v2', 'Color G19'])
def test_check_keyboard_display_and_prepare_image(mode, size, lcd_type, lcd_font, keyboard, protocol_parser):
    from dcspy.aircraft import BasicAircraft
    from dcspy.sdk import lcd_sdk

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        keyboard = keyboard(parser=protocol_parser, fonts=lcd_font)
    assert isinstance(keyboard.plane, BasicAircraft)
    assert isinstance(keyboard.lcd, LcdInfo)
    assert keyboard.lcd.type == lcd_type
    assert isinstance(keyboard.display, list)
    with patch.object(lcd_sdk, 'update_display', return_value=True):
        keyboard.display = ['1', '2']
        assert len(keyboard.display) == 2

    img = keyboard._prepare_image()
    assert img.mode == mode.value
    assert img.size == size


@mark.parametrize('lcd_font, keyboard', [
    (FontsConfig(name=DEFAULT_FONT_NAME, small=9, medium=11, large=16), G13),
    (FontsConfig(name=DEFAULT_FONT_NAME, small=9, medium=11, large=16), G510),
    (FontsConfig(name=DEFAULT_FONT_NAME, small=9, medium=11, large=16), G15v1),
    (FontsConfig(name=DEFAULT_FONT_NAME, small=9, medium=11, large=16), G15v2),
    (FontsConfig(name=DEFAULT_FONT_NAME, small=18, medium=22, large=32), G19)
], ids=['Mono G13', 'Mono G510', 'Mono G15v1', 'Mono G15v2', 'Color G19'])
def test_check_keyboard_text(lcd_font, keyboard, protocol_parser):
    from dcspy.sdk import lcd_sdk

    with patch.object(lcd_sdk, 'logi_lcd_init', return_value=True):
        keyboard = keyboard(parser=protocol_parser, fonts=lcd_font)

    with patch.object(lcd_sdk, 'update_text', return_value=True) as upd_txt:
        keyboard.text(['1', '2'])
        upd_txt.assert_called()


@mark.parametrize('model', [
    'FA18Chornet', 'F16C50', 'F15ESE', 'Ka50', 'Ka503', 'Mi8MT', 'Mi24P', 'AH64DBLKII', 'A10C', 'A10C2', 'F14A135GR', 'F14B', 'AV8BNA',
])
def test_keyboard_mono_load_advanced_plane(model, keyboard_mono):
    from dcspy.aircraft import AdvancedAircraft

    keyboard_mono.plane_name = model
    keyboard_mono.load_new_plane()
    assert isinstance(keyboard_mono.plane, AdvancedAircraft)
    assert model in type(keyboard_mono.plane).__name__


def test_test_keyboard_mono_load_basic_plane(keyboard_mono):
    from dcspy.aircraft import BasicAircraft

    keyboard_mono.plane_name = 'Bf109K4'
    keyboard_mono.bios_name = 'Bf-109K-4'
    keyboard_mono.load_new_plane()
    assert isinstance(keyboard_mono.plane, BasicAircraft)
    assert type(keyboard_mono.plane).__name__ == 'Bf109K4'
    assert keyboard_mono.plane.bios_name == 'Bf-109K-4'


@mark.parametrize('model', [
    'FA18Chornet', 'F16C50', 'F15ESE', 'Ka50', 'Ka503', 'Mi8MT', 'Mi24P', 'AH64DBLKII', 'A10C', 'A10C2', 'F14A135GR', 'F14B', 'AV8BNA',
])
def test_keyboard_color_load_advanced_plane(model, keyboard_color):
    from dcspy.aircraft import AdvancedAircraft

    keyboard_color.plane_name = model
    keyboard_color.load_new_plane()
    assert isinstance(keyboard_color.plane, AdvancedAircraft)
    assert model in type(keyboard_color.plane).__name__


def test_test_keyboard_color_load_basic_plane(keyboard_color):
    from dcspy.aircraft import BasicAircraft

    keyboard_color.plane_name = 'P47D30'
    keyboard_color.bios_name = 'P-47D-30'
    keyboard_color.load_new_plane()
    assert isinstance(keyboard_color.plane, BasicAircraft)
    assert type(keyboard_color.plane).__name__ == 'P47D30'
    assert keyboard_color.plane.bios_name == 'P-47D-30'


@mark.parametrize('model', [
    'FA18Chornet', 'F16C50', 'F15ESE', 'Ka50', 'Ka503', 'Mi8MT', 'Mi24P', 'AH64DBLKII', 'A10C', 'A10C2', 'F14A135GR', 'F14B', 'AV8BNA'
])
@mark.parametrize('keyboard', [
    'G13', 'G510', 'G15v1', 'G15v2', 'G19'
])
def test_all_keyboard_all_plane_load(model, keyboard, resources, request):
    from dcspy.aircraft import AdvancedAircraft

    keyboard = request.getfixturevalue(keyboard)
    with patch('dcspy.logitech.get_config_yaml_item', return_value=resources / 'dcs_bios'):
        keyboard.plane_name = model
        keyboard.load_new_plane()

    assert isinstance(keyboard.plane, AdvancedAircraft)
    assert model in type(keyboard.plane).__name__
