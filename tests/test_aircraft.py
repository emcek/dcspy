from unittest import mock

from pytest import mark, raises


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50', 'F14B'])
def test_check_all_aircraft_inherit_from_correct_base_class(model, lcd_mono):
    from dcspy import aircrafts
    aircraft = getattr(aircrafts, model)
    aircraft_model = aircraft(lcd_mono)
    assert isinstance(aircraft_model, aircrafts.Aircraft)
    assert issubclass(aircraft, aircrafts.Aircraft)


def test_aircraft_base_class(lcd_mono):
    from dcspy import aircrafts
    from PIL import Image
    with mock.patch.object(aircrafts, 'lcd_sdk', return_value=None) as lcd_sdk_mock:
        aircraft = aircrafts.Aircraft(lcd_type=lcd_mono)
        aircraft.bios_data = {'abstract_field': {'addr': 0xdeadbeef, 'len': 16, 'val': ''}}

        assert aircraft.button_request(1) == '\n'

        with raises(NotImplementedError):
            aircraft.prepare_image()

        with raises(NotImplementedError):
            aircraft.set_bios('abstract_field', 'deadbeef', True)

        assert aircraft.get_bios('abstract_field') == 'deadbeef'
        assert aircraft.get_bios('none') == ''
        img = Image.new('1', (aircraft.lcd.width, aircraft.lcd.height), 0)
        assert aircraft.update_display(img) is None
        lcd_sdk_mock.update_display.assert_called_once_with(img)


@mark.parametrize('button, result', [(0, '\n'),
                                     (16, '\n'),
                                     ('a', '\n'),
                                     (1, 'UFC_COMM1_CHANNEL_SELECT DEC\n'),
                                     (9, 'UFC_COMM1_CHANNEL_SELECT DEC\n'),
                                     (4, 'UFC_COMM2_CHANNEL_SELECT INC\n')])
def test_button_pressed_for_hornet(button, result, hornet_mono):
    assert hornet_mono.button_request(button) == result


@mark.parametrize('selector, value, result', [('ScratchpadStr2', '~~', '22'),
                                              ('COMM1', '``', '11'),
                                              ('FuelTotal', '104T', '104T')])
def test_set_bios_for_hornet(selector, value, result, hornet_mono):
    hornet_mono.set_bios(selector, value, False)
    assert hornet_mono.bios_data[selector]['value'] == result


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50', 'F14B'])
def test_prepare_image_for_all_palnes(model, lcd_mono):
    from PIL.Image import Image
    from dcspy import aircrafts
    aircraft = getattr(aircrafts, model)
    aircraft_model = aircraft(lcd_type=lcd_mono)
    if model == 'Ka50':
        aircraft_model.set_bios('l1_text', '123456789', False)
        aircraft_model.set_bios('l2_text', '987654321', False)
    img = aircraft_model.prepare_image()
    assert img.size == (aircraft_model.lcd.width, aircraft_model.lcd.height)
    assert isinstance(img, Image)


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
