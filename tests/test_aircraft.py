from unittest.mock import patch

from pytest import mark, raises

from dcspy import LcdColor, LcdMono

all_plane_list = ['FA18Chornet', 'F16C50', 'Ka50', 'AH64DBLKII', 'A10C', 'A10C2', 'F14B', 'AV8BNA']


# <=><=><=><=><=> Base Class <=><=><=><=><=>
@mark.parametrize('model', all_plane_list)
def test_check_all_aircraft_inherit_from_correct_base_class(model, lcd_mono):
    from dcspy import aircraft
    airplane = getattr(aircraft, model)
    aircraft_model = airplane(lcd_mono)
    assert isinstance(aircraft_model, aircraft.Aircraft)
    assert issubclass(airplane, aircraft.Aircraft)


@mark.parametrize('selector, data, value, c_func, effect, lcd',
                  [('field1', {'addr': 0xdeadbeef, 'len': 16, 'value': ''}, 'val1', 'logi_lcd_mono_set_background', [True], LcdMono),
                   ('field2', {'addr': 0xdeadbeef, 'len': 16, 'value': ''}, 'val2', 'logi_lcd_color_set_background', [False, True], LcdColor)])
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
    aircraft.lcd = LcdInfo(width=3, height=3, type=3, foreground=0, background=128, mode='2', font_xs=font, font_s=font, font_l=font)
    img = aircraft.prepare_image()
    assert img is None


# <=><=><=><=><=> Button Requests <=><=><=><=><=>
@mark.parametrize('plane, button, result', [('hornet_mono', 0, '\n'),
                                            ('hornet_mono', 16, '\n'),
                                            ('hornet_mono', 'a', '\n'),
                                            ('hornet_mono', 1, 'UFC_COMM1_CHANNEL_SELECT DEC\n'),
                                            ('hornet_mono', 4, 'UFC_COMM2_CHANNEL_SELECT INC\n'),
                                            ('hornet_color', 0, '\n'),
                                            ('hornet_color', 16, '\n'),
                                            ('hornet_color', ' ', '\n'),
                                            ('hornet_color', 9, 'UFC_COMM1_CHANNEL_SELECT DEC\n'),
                                            ('hornet_color', 14, 'UFC_COMM2_CHANNEL_SELECT DEC\n'),
                                            ('harrier_mono', 0, '\n'),
                                            ('harrier_mono', 16, '\n'),
                                            ('harrier_mono', 'g', '\n'),
                                            ('harrier_mono', 2, 'UFC_COM1_SEL 3200\n'),
                                            ('harrier_mono', 3, 'UFC_COM2_SEL -3200\n'),
                                            ('harrier_color', 0, '\n'),
                                            ('harrier_color', 16, '\n'),
                                            ('harrier_color', '.', '\n'),
                                            ('harrier_color', 10, 'UFC_COM1_SEL 3200\n'),
                                            ('harrier_color', 13, 'UFC_COM2_SEL 3200\n'),
                                            ('black_shark_mono', 0, '\n'),
                                            ('black_shark_mono', 16, '\n'),
                                            ('black_shark_mono', 2, 'PVI_FIXPOINTS_BTN 1\nPVI_FIXPOINTS_BTN 0\n'),
                                            ('black_shark_mono', 3, 'PVI_AIRFIELDS_BTN 1\nPVI_AIRFIELDS_BTN 0\n'),
                                            ('black_shark_color', 'a', '\n'),
                                            ('black_shark_color', 9, 'PVI_WAYPOINTS_BTN 1\nPVI_WAYPOINTS_BTN 0\n'),
                                            ('black_shark_color', 13, 'PVI_TARGETS_BTN 1\nPVI_TARGETS_BTN 0\n'),
                                            ('tomcat_mono', -1, '\n'),
                                            ('tomcat_mono', 44, '\n'),
                                            ('tomcat_mono', 3, 'RIO_CAP_NE 1\nRIO_CAP_NE 0\n'),
                                            ('tomcat_mono', 4, 'RIO_CAP_ENTER 1\nRIO_CAP_ENTER 0\n'),
                                            ('tomcat_color', '*', '\n'),
                                            ('tomcat_color', 9, 'RIO_CAP_CLEAR 1\nRIO_CAP_CLEAR 0\n'),
                                            ('tomcat_color', 10, 'RIO_CAP_SW 1\nRIO_CAP_SW 0\n'),
                                            ('viper_mono', 2, 'IFF_ENABLE_SW 1\n'),
                                            ('viper_mono', 3, 'IFF_M4_CODE_SW 1\n'),
                                            ('viper_mono', 4, 'IFF_M4_REPLY_SW 1\n'),
                                            ('viper_color', 9, 'IFF_MASTER_KNB 1\n'),
                                            ('viper_color', 10, 'IFF_ENABLE_SW 1\n'),
                                            ('viper_color', 14, 'IFF_M4_CODE_SW 1\n'),
                                            ('apache_mono', 0, '\n'),
                                            ('apache_mono', 16, '\n'),
                                            ('apache_mono', 'a', '\n'),
                                            ('apache_mono', 2, 'PLT_EUFD_IDM 0\nPLT_EUFD_IDM 1\n'),
                                            ('apache_mono', 4, 'PLT_EUFD_ENT 0\nPLT_EUFD_ENT 1\n')])
def test_button_pressed_for_plane(plane, button, result, request):
    plane = request.getfixturevalue(plane)
    assert plane.button_request(button) == result


@mark.parametrize('button, result', [(0, '\n'),
                                     (16, '\n'),
                                     (' ', '\n'),
                                     (10, 'PLT_EUFD_WCA 0\nPLT_EUFD_WCA 1\n'),
                                     (14, 'PLT_EUFD_PRESET 0\nPLT_EUFD_PRESET 1\n')])
def test_button_pressed_for_apache_color(button, result, apache_color):
    apache_color.rocker = 'WCA'
    assert apache_color.button_request(button) == result


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


# <=><=><=><=><=> Set BIOS <=><=><=><=><=>
@mark.parametrize('plane, selector, value, result', [('hornet_mono', 'UFC_SCRATCHPAD_STRING_2_DISPLAY', '~~', '22'),
                                                     ('hornet_mono', 'UFC_COMM1_DISPLAY', '``', '11'),
                                                     ('hornet_mono', 'IFEI_FUEL_UP', '104T', '104T'),
                                                     ('hornet_color', 'UFC_SCRATCHPAD_STRING_1_DISPLAY', '~~', '22'),
                                                     ('hornet_color', 'UFC_COMM1_DISPLAY', '``', '11'),
                                                     ('hornet_color', 'IFEI_FUEL_UP', '1000T', '1000T'),
                                                     ('viper_mono', 'DED_LINE_1', 'a', '\u2666'),
                                                     ('viper_mono', 'DED_LINE_2', 'o', '\u00b0'),
                                                     ('viper_color', 'DED_LINE_3', 'a', '\u2666'),
                                                     ('viper_color', 'DED_LINE_4', 'o', '\u00b0'),
                                                     ('viper_mono', 'DED_LINE_1', '       *      *CMD STRG  \x80@', '       *      *CMD STRG  '),
                                                     ('viper_mono', 'DED_LINE_2', '1DEST 2BNGO 3VIP  RINTG  A\x10\x04', '1DEST 2BNGO 3VIP  RINTG  '),
                                                     ('viper_mono', 'DED_LINE_1',' MARK *HUD *    26a      @', ' MARK *HUD *    26\u2666      '),
                                                     ('viper_mono', 'DED_LINE_5', 'M3 :7000 *     *DCPL(9)  \x03\x82', 'M3 :7000 *     *DCPL(9)  '),
                                                     ('apache_mono', 'PLT_EUFD_LINE8', '~=>VHF*  121.000   -----              121.500   -----   ', '\u25a0\u2219\u25b8VHF*  121.000   -----              121.500   -----   '),
                                                     ('apache_mono', 'PLT_EUFD_LINE9', ' <=UHF*  305.000   -----              305.000   -----   ', ' \u25c2\u2219UHF*  305.000   -----              305.000   -----   '),
                                                     ('apache_mono', 'PLT_EUFD_LINE10', ' <>FM1*   30.000   -----    NORM       30.000   -----   ', ' \u25c2\u25b8FM1*   30.000   -----    NORM       30.000   -----   '),
                                                     ('apache_color', 'PLT_EUFD_LINE11', '[==FM2*   30.000   -----               30.000   -----   ', '\u25ca\u2219\u2219FM2*   30.000   -----               30.000   -----   '),
                                                     ('apache_color', 'PLT_EUFD_LINE12', ' ==HF *    2.0000A -----    LOW         2.0000A -----   ', ' \u2219\u2219HF *    2.0000A -----    LOW         2.0000A -----   '),
                                                     ('apache_color', 'PLT_EUFD_LINE12', ']==HF *    2.0000A -----    LOW         2.0000A -----   ', '\u2666\u2219\u2219HF *    2.0000A -----    LOW         2.0000A -----   ')])
def test_set_bios_for_airplane(plane, selector, value, result, request):
    plane = request.getfixturevalue(plane)
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True):
        with patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True):
            with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                plane.set_bios(selector, value)
                assert plane.bios_data[selector]['value'] == result


@mark.parametrize('plane, selector, value, rocker', [('apache_mono', 'PLT_EUFD_LINE1', '  |   |                ', 'IDM'),
                                                     ('apache_mono', 'PLT_EUFD_LINE1', '  |   |PRESET TUNE VHS ', 'WCA'),
                                                     ('apache_color', 'PLT_EUFD_LINE1', '  |   |                ', 'IDM'),
                                                     ('apache_color', 'PLT_EUFD_LINE1', '  |   |PRESET TUNE VHS ', 'WCA')])
def test_rocker_state_for_apache(plane, selector, value, rocker, request):
    plane = request.getfixturevalue(plane)
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
        plane.set_bios(selector, value)
        assert plane.rocker == rocker


# <=><=><=><=><=> Prepare Image <=><=><=><=><=>
@mark.parametrize('model', all_plane_list)
def test_prepare_image_for_all_planes_mono(model, lcd_mono):
    from PIL.Image import Image
    from dcspy import aircraft
    aircraft_model = getattr(aircraft, model)(lcd_type=lcd_mono)
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


@mark.parametrize('model', all_plane_list)
def test_prepare_image_for_all_planes_color(model, lcd_color):
    from PIL.Image import Image
    from dcspy import aircraft
    aircraft_model = getattr(aircraft, model)(lcd_type=lcd_color)
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
