from unittest.mock import patch, call

from pytest import mark, raises

from dcspy import LcdColor, LcdMono


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50', 'F14B'])
def test_check_all_aircraft_inherit_from_correct_base_class(model, lcd_mono):
    from dcspy import aircraft
    airplane = getattr(aircraft, model)
    aircraft_model = airplane(lcd_mono)
    assert isinstance(aircraft_model, aircraft.Aircraft)
    assert issubclass(airplane, aircraft.Aircraft)


@mark.parametrize('selector, data, value, c_func, effect, lcd', [('field1', {'addr': 0xdeadbeef, 'len': 16, 'value': ''},
                                                                  'val1', 'logi_lcd_mono_set_background',
                                                                  [True], LcdMono),
                                                                 ('field2', {'addr': 0xdeadbeef, 'len': 16, 'value': ''},
                                                                  'val2', 'logi_lcd_color_set_background',
                                                                  [False, True], LcdColor)])
def test_aircraft_base_class_set_bios_with_mono_color_lcd(selector, data, value, c_func, effect, lcd, aircraft):
    from dcspy.sdk import lcd_sdk
    assert aircraft.bios_data == {}
    aircraft.bios_data = {selector: data}
    aircraft.lcd = lcd
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=effect):
        with patch.object(lcd_sdk, c_func, return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                assert aircraft.bios_data[selector]['value'] == ''
                assert aircraft.get_bios('none') == ''
                with raises(NotImplementedError):
                    aircraft.set_bios(selector, value)


@mark.parametrize('mode, c_func, lcd', [('1', 'logi_lcd_mono_set_background', LcdMono),
                                        ('RGBA', 'logi_lcd_color_set_background', LcdColor)])
def test_aircraft_base_class_prepare_img_with_mono_color_lcd(mode, c_func, lcd, aircraft):
    from dcspy.sdk import lcd_sdk
    aircraft.lcd = lcd
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
        with patch.object(lcd_sdk, c_func, return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                with raises(NotImplementedError):
                    aircraft.prepare_image()


def test_aircraft_base_class_other_lcd(aircraft):
    from dcspy import LcdInfo
    from PIL import ImageFont

    font = ImageFont.truetype('consola.ttf', 10)
    aircraft.lcd = LcdInfo(width=3, height=3, type=3, foreground=0, background=128, mode='2', font_s=font, font_l=font)
    img = aircraft.prepare_image()
    assert img is None


@mark.parametrize('button, result', [(0, '\n'),
                                     (16, '\n'),
                                     ('a', '\n'),
                                     (1, 'UFC_COMM1_CHANNEL_SELECT DEC\n'),
                                     (4, 'UFC_COMM2_CHANNEL_SELECT INC\n')])
def test_button_pressed_for_hornet_mono(button, result, hornet_mono):
    assert hornet_mono.button_request(button) == result


@mark.parametrize('button, result', [(0, '\n'),
                                     (16, '\n'),
                                     (' ', '\n'),
                                     (9, 'UFC_COMM1_CHANNEL_SELECT DEC\n'),
                                     (14, 'UFC_COMM2_CHANNEL_SELECT DEC\n')])
def test_button_pressed_for_hornet_color(button, result, hornet_color):
    assert hornet_color.button_request(button) == result


@mark.parametrize('button, result', [(0, '\n'),
                                     (16, '\n'),
                                     ('g', '\n'),
                                     (2, 'UFC_COM1_SEL 3200\n'),
                                     (3, 'UFC_COM2_SEL -3200\n')])
def test_button_pressed_for_harierr_mono(button, result, harrier_mono):
    assert harrier_mono.button_request(button) == result


@mark.parametrize('button, result', [(0, '\n'),
                                     (16, '\n'),
                                     ('.', '\n'),
                                     (10, 'UFC_COM1_SEL 3200\n'),
                                     (13, 'UFC_COM2_SEL 3200\n')])
def test_button_pressed_for_harrier_color(button, result, harrier_color):
    assert harrier_color.button_request(button) == result


@mark.parametrize('selector, value, result', [('UFC_SCRATCHPAD_STRING_2_DISPLAY', '~~', '22'),
                                              ('UFC_COMM1_DISPLAY', '``', '11'),
                                              ('IFEI_FUEL_UP', '104T', '104T')])
def test_set_bios_for_hornet_mono(selector, value, result, hornet_mono):
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
        with patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                hornet_mono.set_bios(selector, value)
                assert hornet_mono.bios_data[selector]['value'] == result


@mark.parametrize('selector, value, result', [('UFC_SCRATCHPAD_STRING_1_DISPLAY', '~~', '22'),
                                              ('UFC_COMM1_DISPLAY', '``', '11'),
                                              ('IFEI_FUEL_UP', '1000T', '1000T')])
def test_set_bios_for_hornet_color(selector, value, result, hornet_color):
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
        with patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                hornet_color.set_bios(selector, value)
                assert hornet_color.bios_data[selector]['value'] == result


@mark.parametrize('button, result', [(0, '\n'),
                                     (16, '\n'),
                                     ('a', '\n'),
                                     (2, 'PVI_FIXPOINTS_BTN 1\nPVI_FIXPOINTS_BTN 0\n'),
                                     (10, 'PVI_FIXPOINTS_BTN 1\nPVI_FIXPOINTS_BTN 0\n'),
                                     (3, 'PVI_AIRFIELDS_BTN 1\nPVI_AIRFIELDS_BTN 0\n')])
def test_button_pressed_for_shark(button, result, black_shark_mono):
    assert black_shark_mono.button_request(button) == result


@mark.parametrize('button, result', [(-1, '\n'),
                                     (44, '\n'),
                                     ('*', '\n'),
                                     (3, 'RIO_CAP_NE 1\nRIO_CAP_NE 0\n'),
                                     (4, 'RIO_CAP_ENTER 1\nRIO_CAP_ENTER 0\n')])
def test_button_pressed_for_tomcat(button, result, tomcat_mono):
    assert tomcat_mono.button_request(button) == result


@mark.parametrize('button, result', [(2, 'IFF_ENABLE_SW 1\n'),
                                     (3, 'IFF_M4_CODE_SW 1\n'),
                                     (4, 'IFF_M4_REPLY_SW 1\n')])
def test_button_pressed_for_viper_mono(button, result, viper_mono):
    assert viper_mono.button_request(button) == result


def test_get_next_value_for_button_in_viper(viper_color):
    from itertools import cycle
    btn9, name9 = 9, 'IFF_MASTER_KNB'
    assert not all([v for v in viper_color.cycle_buttons.values()])
    assert viper_color.button_request(btn9) == f'{name9} 1\n'
    assert viper_color.button_request(btn9) == f'{name9} 2\n'
    assert viper_color.button_request(btn9) == f'{name9} 3\n'
    assert viper_color.button_request(btn9) == f'{name9} 4\n'
    assert viper_color.button_request(btn9) == f'{name9} 3\n'
    assert viper_color.button_request(btn9) == f'{name9} 2\n'
    assert viper_color.button_request(btn9) == f'{name9} 1\n'
    assert viper_color.button_request(btn9) == f'{name9} 0\n'
    assert viper_color.button_request(btn9) == f'{name9} 1\n'
    assert isinstance(viper_color.cycle_buttons[name9], cycle)


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50', 'A10C', 'A10C2', 'F14B', 'AV8BNA'])
def test_prepare_image_for_all_planes_mono(model, lcd_mono):
    from PIL.Image import Image
    from dcspy import aircraft
    aircraft = getattr(aircraft, model)
    aircraft_model = aircraft(lcd_type=lcd_mono)
    if model == 'Ka50':
        from dcspy.sdk import lcd_sdk
        with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True):
                with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                    aircraft_model.set_bios('PVI_LINE1_TEXT', '123456789')
                    aircraft_model.set_bios('PVI_LINE2_TEXT', '987654321')
    img = aircraft_model.prepare_image()
    assert isinstance(img, Image)
    assert img.size == (lcd_mono.width, lcd_mono.height)
    assert img.mode == '1'


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50', 'A10C', 'A10C2', 'F14B', 'AV8BNA'])
def test_prepare_image_for_all_planes_color(model, lcd_color):
    from PIL.Image import Image
    from dcspy import aircraft
    aircraft = getattr(aircraft, model)
    aircraft_model = aircraft(lcd_type=lcd_color)
    if model == 'Ka50':
        from dcspy.sdk import lcd_sdk
        with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True):
                with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                    aircraft_model.set_bios('PVI_LINE1_TEXT', '123456789')
                    aircraft_model.set_bios('PVI_LINE2_TEXT', '987654321')
    img = aircraft_model.prepare_image()
    assert isinstance(img, Image)
    assert img.size == (lcd_color.width, lcd_color.height)
    assert img.mode == 'RGBA'


@mark.parametrize('selector, value, name, rgb, duration, interval, c_func', [('SC_MASTER_CAUTION_LED', 1, 'pulse', (0, 0, 100), 10, 10, 'logi_led_pulse_lighting' )])
def test_basic_led_effect_one_selector_for_shark_mono(selector, value, black_shark_mono, name, rgb, duration, interval, c_func):
    from dcspy.sdk import led_sdk
    with patch.object(led_sdk, 'logi_led_init', return_value=True) as logi_led_init:
        with patch.object(led_sdk, 'logi_led_shutdown', return_value=True) as logi_led_shutdown:
            with patch.object(led_sdk, 'logi_led_set_target_device', return_value=True) as logi_led_set_target_device:
                with patch.object(led_sdk, c_func, return_value=True) as logi_led_lighting:
                    effect = led_sdk.EffectInfo(name=name, rgb=rgb, duration=duration, interval=interval)
                    black_shark_mono.led_handler(selector, value, effect)
                    logi_led_shutdown.assert_called_once()
                    logi_led_init.assert_called_once()
                    logi_led_set_target_device.assert_called_once_with(led_sdk.LOGI_DEVICETYPE_ALL)
                    logi_led_lighting.assert_called_once_with(effect.rgb, effect.duration, effect.interval)
                    assert black_shark_mono.bios_data[selector]['value'] == value
                    assert len(black_shark_mono.led_stack) == 1
                    assert black_shark_mono.led_stack[selector] == effect


def test_led_effect_one_selector_for_shark_mono_on_off(black_shark_mono):
    from dcspy.sdk import led_sdk
    with patch.object(led_sdk, 'logi_led_init', return_value=True) as logi_led_init:
        with patch.object(led_sdk, 'logi_led_shutdown', return_value=True) as logi_led_shutdown:
            with patch.object(led_sdk, 'logi_led_set_target_device', return_value=True) as logi_led_set_target_device:
                with patch.object(led_sdk, 'logi_led_pulse_lighting', return_value=True) as logi_led_pulse_lighting:
                    selector = 'SC_MASTER_CAUTION_LED'
                    effect = led_sdk.EffectInfo(name='pulse', rgb=(0, 0, 100), duration=10, interval=10)
                    black_shark_mono.led_handler(selector, 1, effect)
                    logi_led_shutdown.assert_called_once()
                    logi_led_init.assert_called_once()
                    logi_led_set_target_device.assert_called_once_with(led_sdk.LOGI_DEVICETYPE_ALL)
                    logi_led_pulse_lighting.assert_called_once_with(effect.rgb, effect.duration, effect.interval)
                    assert black_shark_mono.bios_data[selector]['value'] == 1
                    assert len(black_shark_mono.led_stack) == 1
                    assert black_shark_mono.led_stack[selector] == effect

                    black_shark_mono.led_handler(selector, 0, effect)
                    assert black_shark_mono.bios_data[selector]['value'] == 0
                    assert len(black_shark_mono.led_stack) == 0
                    logi_led_shutdown.assert_has_calls([call(), call()])
