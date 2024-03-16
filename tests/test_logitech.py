from unittest.mock import call, patch

from pytest import mark

from dcspy.logitech import G13, G19, G510, G15v1, G15v2
from dcspy.models import DEFAULT_FONT_NAME, FontsConfig, LcdButton, LcdInfo, LcdMode, LcdType


def test_keyboard_base_basic_check(keyboard_base):
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    assert str(keyboard_base) == 'KeyboardManager: 160x43'
    logitech_repr = repr(keyboard_base)
    data = ('parser', 'ProtocolParser', 'plane_name', 'plane_detected', 'lcdbutton_pressed', 'buttons',
            '_display', 'plane', 'BasicAircraft', 'vert_space', 'lcd', 'LcdInfo', 'gkey', 'buttons', 'model', 'KeyboardModel',
            'lcd_sdk', 'key_sdk')
    for test_string in data:
        assert test_string in logitech_repr

    with patch.object(LcdSdkManager, 'clear_display', return_value=True):
        keyboard_base.clear()


@mark.parametrize('keyboard, pressed1, effect, chk_btn, calls, pressed2', [
    ('keyboard_mono', False, [False] * 3 + [True], LcdButton.FOUR, [call(LcdButton.ONE), call(LcdButton.TWO), call(LcdButton.THREE), call(LcdButton.FOUR)], True),
    ('keyboard_color', False, [False] * 4 + [True] + [False] * 2, LcdButton.OK, [call(LcdButton.LEFT), call(LcdButton.RIGHT), call(LcdButton.UP), call(LcdButton.DOWN), call(LcdButton.OK)], True),
    ('keyboard_mono', True, [True, False, False, False], LcdButton.NONE, [call(LcdButton.ONE)], True),
    ('keyboard_color', True, [True] + [False] * 6, LcdButton.NONE, [call(LcdButton.LEFT)], True),
    ('keyboard_mono', False, [False] * 4, LcdButton.NONE, [call(LcdButton.ONE), call(LcdButton.TWO), call(LcdButton.THREE), call(LcdButton.FOUR)], False),
    ('keyboard_color', False, [False] * 8, LcdButton.NONE, [call(LcdButton.LEFT), call(LcdButton.RIGHT), call(LcdButton.UP), call(LcdButton.DOWN), call(LcdButton.OK), call(LcdButton.CANCEL), call(LcdButton.MENU)], False),
], ids=[
    'Mono 4 Button',
    'Color Ok Button',
    'Mono None already_pressed',
    'Color None already_pressed',
    'Mono None Button',
    'Color None Button'])
def test_keyboard_check_buttons(keyboard, pressed1, effect, chk_btn, calls, pressed2, request):
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    keyboard = request.getfixturevalue(keyboard)
    keyboard.lcdbutton_pressed = pressed1
    with patch.object(LcdSdkManager, 'logi_lcd_is_button_pressed', side_effect=effect) as lcd_btn_pressed:
        assert keyboard.check_buttons() == chk_btn
    lcd_btn_pressed.assert_has_calls(calls)
    assert keyboard.lcdbutton_pressed is pressed2


@mark.parametrize('keyboard', ['keyboard_mono', 'keyboard_color'], ids=['Mono Keyboard', 'Color Keyboard'])
def test_keyboard_button_handle_lcdbutton(keyboard, request):
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    keyboard = request.getfixturevalue(keyboard)
    with patch.object(LcdSdkManager, 'logi_lcd_is_button_pressed', side_effect=[True]):
        keyboard.button_handle()
    keyboard.socket.sendto.assert_called_once_with(b'TEST 1\n', ('127.0.0.1', 7778))


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
def test_check_keyboard_display_and_prepare_image(mode, size, lcd_type, lcd_font, keyboard, protocol_parser, sock):
    from dcspy.aircraft import BasicAircraft
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    with patch.object(LcdSdkManager, 'update_text', return_value=True):
        keyboard = keyboard(parser=protocol_parser, sock=sock, fonts=lcd_font)
        assert isinstance(keyboard.plane, BasicAircraft)
        assert isinstance(keyboard.lcd, LcdInfo)
        assert keyboard.lcd.type == lcd_type
        assert isinstance(keyboard.display, list)
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
def test_check_keyboard_text(lcd_font, keyboard, protocol_parser, sock):
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    with patch.object(LcdSdkManager, 'update_text', return_value=True) as upd_txt:
        keyboard = keyboard(parser=protocol_parser, sock=sock, fonts=lcd_font)
        keyboard.text(['1', '2'])
        upd_txt.assert_called()


@mark.parametrize('model', [
    'FA18Chornet', 'F16C50', 'F15ESE', 'Ka50', 'Ka503', 'Mi8MT', 'Mi24P', 'AH64DBLKII', 'A10C', 'A10C2', 'F14A135GR', 'F14B', 'AV8BNA',
])
def test_keyboard_mono_load_advanced_plane(model, keyboard_mono, test_config_yaml):
    from dcspy.aircraft import AdvancedAircraft

    with patch('dcspy.aircraft.default_yaml', test_config_yaml):
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
def test_keyboard_color_load_advanced_plane(model, keyboard_color, test_config_yaml):
    from dcspy.aircraft import AdvancedAircraft

    with patch('dcspy.aircraft.default_yaml', test_config_yaml):
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
def test_all_keyboard_all_plane_load(model, keyboard, test_dcs_bios, test_config_yaml, request):
    from dcspy.aircraft import AdvancedAircraft

    keyboard = request.getfixturevalue(keyboard)
    with patch('dcspy.logitech.get_config_yaml_item', return_value=test_dcs_bios):
        with patch('dcspy.aircraft.default_yaml', test_config_yaml):
            keyboard.plane_name = model
            keyboard.load_new_plane()

    assert isinstance(keyboard.plane, AdvancedAircraft)
    assert model in type(keyboard.plane).__name__


@mark.parametrize('keyboard, models', [('G13', ('A10C', 'Ka50'))])
def test_unload_plane(keyboard, models, test_dcs_bios, test_config_yaml, request):
    from dcspy.aircraft import A10C, Ka50

    keyboard = request.getfixturevalue(keyboard)
    with patch('dcspy.logitech.get_config_yaml_item', return_value=test_dcs_bios):
        with patch('dcspy.aircraft.default_yaml', test_config_yaml):
            args_list = []
            keyboard.plane_name = models[0]
            keyboard.load_new_plane()
            assert isinstance(keyboard.plane, A10C)
            for partial_obj in keyboard.parser.write_callbacks:
                for callback in partial_obj.func.__self__.callbacks:
                    args_list.extend([arg for arg in callback.args])
            assert set(args_list) == set(keyboard.plane.bios_data.keys())

            keyboard.unload_old_plane()
            assert len(keyboard.parser.write_callbacks) == 1

            args_list = []
            keyboard.plane_name = models[1]
            keyboard.load_new_plane()
            assert isinstance(keyboard.plane, Ka50)
            for partial_obj in keyboard.parser.write_callbacks:
                for callback in partial_obj.func.__self__.callbacks:
                    args_list.extend([arg for arg in callback.args])
            assert set(args_list) == set(keyboard.plane.bios_data.keys())
