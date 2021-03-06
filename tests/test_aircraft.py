from unittest.mock import patch

from pytest import mark, raises

from dcspy import LcdColor, LcdMono


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50', 'F14B'])
def test_check_all_aircraft_inherit_from_correct_base_class(model, lcd_mono):
    from dcspy import aircrafts
    aircraft = getattr(aircrafts, model)
    aircraft_model = aircraft(lcd_mono)
    assert isinstance(aircraft_model, aircrafts.Aircraft)
    assert issubclass(aircraft, aircrafts.Aircraft)


@mark.parametrize('selector, data, value, c_func, effect, lcd', [('field1', {'addr': 0xdeadbeef, 'len': 16, 'value': ''},
                                                                  'val1', 'logi_lcd_mono_set_background',
                                                                  [True], LcdMono),
                                                                 ('field2', {'addr': 0xdeadbeef, 'len': 16, 'value': ''},
                                                                  'val2', 'logi_lcd_color_set_background',
                                                                  [False, True], LcdColor)])
def test_aircraft_base_class_set_bios_with_mono_color_lcd(selector, data, value, c_func, effect, lcd, aircraft):
    from dcspy import lcd_sdk
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
    from dcspy import lcd_sdk
    aircraft.lcd = lcd
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
        with patch.object(lcd_sdk, c_func, return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                with raises(NotImplementedError):
                    aircraft.prepare_image()


def test_aircraft_base_class_other_lcd(aircraft):
    from dcspy import LcdSize
    aircraft.lcd = LcdSize(width=3, height=3, type=3)
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


@mark.parametrize('selector, value, result', [('ScratchpadStr2', '~~', '22'),
                                              ('COMM1', '``', '11'),
                                              ('IFEI_FUEL_UP', '104T', '104T')])
def test_set_bios_for_hornet_mono(selector, value, result, hornet_mono):
    from dcspy import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
        with patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                hornet_mono.set_bios(selector, value)
                assert hornet_mono.bios_data[selector]['value'] == result


@mark.parametrize('selector, value, result', [('ScratchpadStr1', '~~', '22'),
                                              ('COMM2', '``', '11'),
                                              ('IFEI_FUEL_UP', '1000T', '1000T')])
def test_set_bios_for_hornet_color(selector, value, result, hornet_color):
    from dcspy import lcd_sdk
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


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50', 'F14B'])
def test_prepare_image_for_all_palnes_mono(model, lcd_mono):
    from PIL.Image import Image
    from dcspy import aircrafts
    aircraft = getattr(aircrafts, model)
    aircraft_model = aircraft(lcd_type=lcd_mono)
    if model == 'Ka50':
        from dcspy import lcd_sdk
        with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True):
                with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                    aircraft_model.set_bios('l1_text', '123456789')
                    aircraft_model.set_bios('l2_text', '987654321')
    img = aircraft_model.prepare_image()
    assert isinstance(img, Image)
    assert img.size == (lcd_mono.width, lcd_mono.height)
    assert img.mode == '1'


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50', 'F14B'])
def test_prepare_image_for_all_palnes_color(model, lcd_color):
    from PIL.Image import Image
    from dcspy import aircrafts
    aircraft = getattr(aircrafts, model)
    aircraft_model = aircraft(lcd_type=lcd_color)
    if model == 'Ka50':
        from dcspy import lcd_sdk
        with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True):
                with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                    aircraft_model.set_bios('l1_text', '123456789')
                    aircraft_model.set_bios('l2_text', '987654321')
    img = aircraft_model.prepare_image()
    assert isinstance(img, Image)
    assert img.size == (lcd_color.width, lcd_color.height)
    assert img.mode == 'RGBA'
