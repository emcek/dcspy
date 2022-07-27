from os import path
from sys import platform
from unittest.mock import patch

import PIL
from PIL import ImageChops
from pytest import mark, raises

from dcspy import LcdColor, LcdMono, LcdButton
from tests.helpers import all_plane_list, set_bios_during_test

resources = path.join(path.dirname(path.abspath(__file__)), 'resources')


# <=><=><=><=><=> Base Class <=><=><=><=><=>
@mark.parametrize('model', all_plane_list)
def test_check_all_aircraft_inherit_from_correct_base_class(model, lcd_mono):
    from dcspy import aircraft
    airplane = getattr(aircraft, model)
    aircraft_model = airplane(lcd_mono)
    assert isinstance(aircraft_model, aircraft.Aircraft)
    assert issubclass(airplane, aircraft.Aircraft)


@mark.parametrize('selector, data, value, c_func, effect, lcd', [
    ('field1', {'addr': 0xdeadbeef, 'len': 16, 'value': ''}, 'val1', 'logi_lcd_mono_set_background', [True], LcdMono),
    ('field2', {'addr': 0xdeadbeef, 'len': 16, 'value': ''}, 'val2', 'logi_lcd_color_set_background', [False, True], LcdColor),
])
def test_aircraft_base_class_set_bios_with_mono_color_lcd(selector, data, value, c_func, effect, lcd, aircraft):
    from dcspy.sdk import lcd_sdk
    assert aircraft.bios_data == {}
    aircraft.bios_data = {selector: data}
    aircraft.lcd = lcd
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=effect), \
            patch.object(lcd_sdk, c_func, return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
        assert aircraft.bios_data[selector]['value'] == ''
        assert aircraft.get_bios('none') == ''
        with raises(NotImplementedError):
            aircraft.set_bios(selector, value)


@mark.parametrize('mode, c_func, lcd', [('1', 'logi_lcd_mono_set_background', LcdMono),
                                        ('RGBA', 'logi_lcd_color_set_background', LcdColor)])
def test_aircraft_base_class_prepare_img_with_mono_color_lcd(mode, c_func, lcd, aircraft):
    from dcspy.sdk import lcd_sdk
    aircraft.lcd = lcd
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True), \
            patch.object(lcd_sdk, c_func, return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_update', return_value=True), \
            raises(NotImplementedError):
        aircraft.prepare_image()


# <=><=><=><=><=> Button Requests <=><=><=><=><=>
@mark.parametrize('plane, button, result', [
    ('hornet_mono', LcdButton.NONE, '\n'),
    ('hornet_mono', LcdButton.ONE, 'UFC_COMM1_CHANNEL_SELECT DEC\n'),
    ('hornet_mono', LcdButton.TWO, 'UFC_COMM1_CHANNEL_SELECT INC\n'),
    ('hornet_mono', LcdButton.THREE, 'UFC_COMM2_CHANNEL_SELECT DEC\n'),
    ('hornet_mono', LcdButton.FOUR, 'UFC_COMM2_CHANNEL_SELECT INC\n'),
    ('hornet_color', LcdButton.NONE, '\n'),
    ('hornet_color', LcdButton.LEFT, 'UFC_COMM1_CHANNEL_SELECT DEC\n'),
    ('hornet_color', LcdButton.RIGHT, 'UFC_COMM1_CHANNEL_SELECT INC\n'),
    ('hornet_color', LcdButton.DOWN, 'UFC_COMM2_CHANNEL_SELECT DEC\n'),
    ('hornet_color', LcdButton.UP, 'UFC_COMM2_CHANNEL_SELECT INC\n'),
    ('hornet_color', LcdButton.MENU, 'IFEI_DWN_BTN 1\n'),
    ('hornet_color', LcdButton.CANCEL, 'IFEI_UP_BTN 1\n'),
    ('hornet_color', LcdButton.OK, 'HUD_ATT_SW 1\n'),
    ('harrier_mono', LcdButton.NONE, '\n'),
    ('harrier_mono', LcdButton.ONE, 'UFC_COM1_SEL -3200\n'),
    ('harrier_mono', LcdButton.TWO, 'UFC_COM1_SEL 3200\n'),
    ('harrier_mono', LcdButton.THREE, 'UFC_COM2_SEL -3200\n'),
    ('harrier_mono', LcdButton.FOUR, 'UFC_COM2_SEL 3200\n'),
    ('harrier_color', LcdButton.NONE, '\n'),
    ('harrier_color', LcdButton.LEFT, 'UFC_COM1_SEL -3200\n'),
    ('harrier_color', LcdButton.RIGHT, 'UFC_COM1_SEL 3200\n'),
    ('harrier_color', LcdButton.DOWN, 'UFC_COM2_SEL -3200\n'),
    ('harrier_color', LcdButton.UP, 'UFC_COM2_SEL 3200\n'),
    ('harrier_color', LcdButton.MENU, '\n'),
    ('harrier_color', LcdButton.CANCEL, '\n'),
    ('harrier_color', LcdButton.OK, '\n'),
    ('shark_mono', LcdButton.NONE, '\n'),
    ('shark_mono', LcdButton.ONE, 'PVI_WAYPOINTS_BTN 1\nPVI_WAYPOINTS_BTN 0\n'),
    ('shark_mono', LcdButton.TWO, 'PVI_FIXPOINTS_BTN 1\nPVI_FIXPOINTS_BTN 0\n'),
    ('shark_mono', LcdButton.THREE, 'PVI_AIRFIELDS_BTN 1\nPVI_AIRFIELDS_BTN 0\n'),
    ('shark_mono', LcdButton.FOUR, 'PVI_TARGETS_BTN 1\nPVI_TARGETS_BTN 0\n'),
    ('shark_color', LcdButton.NONE, '\n'),
    ('shark_color', LcdButton.LEFT, 'PVI_WAYPOINTS_BTN 1\nPVI_WAYPOINTS_BTN 0\n'),
    ('shark_color', LcdButton.RIGHT, 'PVI_FIXPOINTS_BTN 1\nPVI_FIXPOINTS_BTN 0\n'),
    ('shark_color', LcdButton.DOWN, 'PVI_AIRFIELDS_BTN 1\nPVI_AIRFIELDS_BTN 0\n'),
    ('shark_color', LcdButton.UP, 'PVI_TARGETS_BTN 1\nPVI_TARGETS_BTN 0\n'),
    ('shark_color', LcdButton.MENU, '\n'),
    ('shark_color', LcdButton.CANCEL, '\n'),
    ('shark_color', LcdButton.OK, '\n'),
    ('tomcat_mono', LcdButton.NONE, '\n'),
    ('tomcat_mono', LcdButton.ONE, 'RIO_CAP_CLEAR 1\nRIO_CAP_CLEAR 0\n'),
    ('tomcat_mono', LcdButton.TWO, 'RIO_CAP_SW 1\nRIO_CAP_SW 0\n'),
    ('tomcat_mono', LcdButton.THREE, 'RIO_CAP_NE 1\nRIO_CAP_NE 0\n'),
    ('tomcat_mono', LcdButton.FOUR, 'RIO_CAP_ENTER 1\nRIO_CAP_ENTER 0\n'),
    ('tomcat_color', LcdButton.NONE, '\n'),
    ('tomcat_color', LcdButton.LEFT, 'RIO_CAP_CLEAR 1\nRIO_CAP_CLEAR 0\n'),
    ('tomcat_color', LcdButton.RIGHT, 'RIO_CAP_SW 1\nRIO_CAP_SW 0\n'),
    ('tomcat_color', LcdButton.DOWN, 'RIO_CAP_NE 1\nRIO_CAP_NE 0\n'),
    ('tomcat_color', LcdButton.UP, 'RIO_CAP_ENTER 1\nRIO_CAP_ENTER 0\n'),
    ('tomcat_color', LcdButton.MENU, '\n'),
    ('tomcat_color', LcdButton.CANCEL, '\n'),
    ('tomcat_color', LcdButton.OK, '\n'),
    ('viper_mono', LcdButton.NONE, '\n'),
    ('viper_mono', LcdButton.ONE, 'IFF_MASTER_KNB 1\n'),
    ('viper_mono', LcdButton.TWO, 'IFF_ENABLE_SW 1\n'),
    ('viper_mono', LcdButton.THREE, 'IFF_M4_CODE_SW 1\n'),
    ('viper_mono', LcdButton.FOUR, 'IFF_M4_REPLY_SW 1\n'),
    ('viper_color', LcdButton.NONE, '\n'),
    ('viper_color', LcdButton.LEFT, 'IFF_MASTER_KNB 1\n'),
    ('viper_color', LcdButton.RIGHT, 'IFF_ENABLE_SW 1\n'),
    ('viper_color', LcdButton.DOWN, 'IFF_M4_CODE_SW 1\n'),
    ('viper_color', LcdButton.UP, 'IFF_M4_REPLY_SW 1\n'),
    ('viper_color', LcdButton.MENU, '\n'),
    ('viper_color', LcdButton.CANCEL, '\n'),
    ('viper_color', LcdButton.OK, '\n'),
    ('apache_mono', LcdButton.NONE, '\n'),
    ('apache_mono', LcdButton.ONE, 'PLT_EUFD_IDM 0\nPLT_EUFD_IDM 1\n'),
    ('apache_mono', LcdButton.TWO, 'PLT_EUFD_RTS 0\nPLT_EUFD_RTS 1\n'),
    ('apache_mono', LcdButton.THREE, 'PLT_EUFD_PRESET 0\nPLT_EUFD_PRESET 1\n'),
    ('apache_mono', LcdButton.FOUR, 'PLT_EUFD_ENT 0\nPLT_EUFD_ENT 1\n'),
])
def test_button_pressed_for_plane(plane, button, result, request):
    plane = request.getfixturevalue(plane)
    assert plane.button_request(button) == result


@mark.parametrize('button, result', [
    (LcdButton.NONE, '\n'),
    (LcdButton.LEFT, 'PLT_EUFD_WCA 0\nPLT_EUFD_WCA 1\n'),
    (LcdButton.RIGHT, 'PLT_EUFD_RTS 0\nPLT_EUFD_RTS 1\n'),
    (LcdButton.DOWN, 'PLT_EUFD_PRESET 0\nPLT_EUFD_PRESET 1\n'),
    (LcdButton.UP, 'PLT_EUFD_ENT 0\nPLT_EUFD_ENT 1\n'),
    (LcdButton.MENU, '\n'),
    (LcdButton.CANCEL, '\n'),
    (LcdButton.OK, '\n'),
])
def test_button_pressed_for_apache_color(button, result, apache_color):
    from dcspy.aircraft import ApacheEufdMode
    apache_color.mode = ApacheEufdMode.WCA
    assert apache_color.button_request(button) == result


@mark.parametrize('plane, btn_name, btn, values', [
    ('viper_mono', 'IFF_MASTER_KNB', LcdButton.ONE, (1, 2, 3, 4, 3, 2, 1, 0, 1)),
    ('viper_mono', 'IFF_ENABLE_SW', LcdButton.TWO, (1, 2, 1, 0, 1)),
    ('viper_mono', 'IFF_M4_CODE_SW', LcdButton.THREE, (1, 2, 1, 0, 1)),
    ('viper_mono', 'IFF_M4_REPLY_SW', LcdButton.FOUR, (1, 2, 1, 0, 1)),
    ('viper_color', 'IFF_MASTER_KNB', LcdButton.LEFT, (1, 2, 3, 4, 3, 2, 1, 0, 1)),
    ('viper_color', 'IFF_ENABLE_SW', LcdButton.RIGHT, (1, 2, 1, 0, 1)),
    ('viper_color', 'IFF_M4_CODE_SW', LcdButton.DOWN, (1, 2, 1, 0, 1)),
    ('viper_color', 'IFF_M4_REPLY_SW', LcdButton.UP, (1, 2, 1, 0, 1)),
    ('hornet_color', 'HUD_ATT_SW', LcdButton.OK, (1, 2, 1, 0, 1)),
    ('hornet_color', 'IFEI_DWN_BTN', LcdButton.MENU, (1, 0, 1)),
    ('hornet_color', 'IFEI_UP_BTN', LcdButton.CANCEL, (1, 0, 1)),
])
def test_get_next_value_for_cycle_buttons(plane, btn_name, btn, values, request):
    from itertools import cycle
    plane = request.getfixturevalue(plane)
    assert not all([cyc_btn for cyc_btn in plane.cycle_buttons.values()])
    for val in values:
        assert plane.button_request(btn) == f'{btn_name} {val}\n'
    assert isinstance(plane.cycle_buttons[btn_name], cycle)


# <=><=><=><=><=> Set BIOS <=><=><=><=><=>
@mark.parametrize('plane, bios_pairs, result', [
    ('hornet_mono', [('UFC_SCRATCHPAD_STRING_2_DISPLAY', '~~')], '22'),
    ('hornet_mono', [('UFC_COMM1_DISPLAY', '``')], '11'),
    ('hornet_mono', [('IFEI_FUEL_UP', '104T')], '104T'),
    ('hornet_color', [('UFC_SCRATCHPAD_STRING_1_DISPLAY', '~~')], '22'),
    ('hornet_color', [('UFC_COMM1_DISPLAY', '``')], '11'),
    ('hornet_color', [('IFEI_FUEL_UP', '1000T')], '1000T'),
    ('viper_mono', [('DED_LINE_1', 'a')], '\u2666'),
    ('viper_mono', [('DED_LINE_2', 'o')], '\u00b0'),
    ('viper_color', [('DED_LINE_3', 'a')], '\u2666'),
    ('viper_color', [('DED_LINE_4', 'o')], '\u00b0'),
    ('viper_mono', [('DED_LINE_1', '       *      *CMD STRG  \x80@')], '       \u25d9      \u25d9CMD STRG  '),
    ('viper_mono', [('DED_LINE_2', '1DEST 2BNGO 3VIP  RINTG  A\x10\x04')], '1DEST 2BNGO 3VIP  RINTG  '),
    ('viper_mono', [('DED_LINE_1', ' MARK *HUD *    26a      @')], ' MARK \u25d9HUD \u25d9    26\u2666      '),
    ('viper_mono', [('DED_LINE_5', 'M3 :7000 *     *DCPL(9)  \x03\x82')], 'M3 :7000 \u25d9     \u25d9DCPL(9)  '),
    ('apache_mono', [('PLT_EUFD_LINE8', '~=>VHF*  121.000   -----              121.500   -----   ')], '\u25a0\u2219\u25b8VHF*  121.000   -----              121.500   -----   '),
    ('apache_mono', [('PLT_EUFD_LINE9', ' <=UHF*  305.000   -----              305.000   -----   ')], ' \u25c2\u2219UHF*  305.000   -----              305.000   -----   '),
    ('apache_mono', [('PLT_EUFD_LINE10', ' <>FM1*   30.000   -----    NORM       30.000   -----   ')], ' \u25c2\u25b8FM1*   30.000   -----    NORM       30.000   -----   '),
    ('apache_color', [('PLT_EUFD_LINE11', '[==FM2*   30.000   -----               30.000   -----   ')], '\u25ca\u2219\u2219FM2*   30.000   -----               30.000   -----   '),
    ('apache_color', [('PLT_EUFD_LINE12', ' ==HF *    2.0000A -----    LOW         2.0000A -----   ')], ' \u2219\u2219HF *    2.0000A -----    LOW         2.0000A -----   '),
    ('apache_color', [('PLT_EUFD_LINE12', ']==HF *    2.0000A -----    LOW         2.0000A -----   ')], '\u2666\u2219\u2219HF *    2.0000A -----    LOW         2.0000A -----   '),
])
def test_set_bios_for_airplane(plane, bios_pairs, result, request):
    plane = request.getfixturevalue(plane)
    set_bios_during_test(plane, bios_pairs)
    assert plane.bios_data[bios_pairs[0][0]]['value'] == result


@mark.parametrize('plane, bios_pairs, mode', [
    ('apache_mono', [('PLT_EUFD_LINE1', 'ENGINE 1 OUT      |AFT FUEL LOW      |TAIL WHL LOCK SEL ')], 'IDM'),
    ('apache_mono', [('PLT_EUFD_LINE1', '                  |AFT FUEL LOW      |PRESET TUNE VHS ')], 'PRE'),
    ('apache_color', [('PLT_EUFD_LINE1', '                  |                  |TAIL WHL LOCK SEL ')], 'IDM'),
    ('apache_color', [('PLT_EUFD_LINE1', '                  |AFT FUEL LOW      |TAIL WHL LOCK SEL ')], 'IDM'),
    ('apache_color', [('PLT_EUFD_LINE1', 'ENGINE 1 OUT      |AFT FUEL LOW      |PRESET TUNE FM1 ')], 'PRE'),
])
def test_mode_switch_idm_pre_for_apache(plane, bios_pairs, mode, request):
    plane = request.getfixturevalue(plane)
    set_bios_during_test(plane, bios_pairs)
    assert plane.mode.name == mode


# <=><=><=><=><=> Prepare Image <=><=><=><=><=>
hornet_bios = [
    ('UFC_SCRATCHPAD_STRING_1_DISPLAY', '11'),
    ('UFC_SCRATCHPAD_STRING_2_DISPLAY', '22'),
    ('UFC_SCRATCHPAD_NUMBER_DISPLAY', '1234567890'),
    ('UFC_OPTION_DISPLAY_1', '1234'),
    ('UFC_OPTION_DISPLAY_2', '2345'),
    ('UFC_OPTION_DISPLAY_3', '3456'),
    ('UFC_OPTION_DISPLAY_4', '4567'),
    ('UFC_OPTION_DISPLAY_5', '5678'),
    ('UFC_COMM1_DISPLAY', '11'),
    ('UFC_COMM2_DISPLAY', '22'),
    ('UFC_OPTION_CUEING_1', '1'),
    ('UFC_OPTION_CUEING_2', '2'),
    ('UFC_OPTION_CUEING_3', '3'),
    ('UFC_OPTION_CUEING_4', '4'),
    ('UFC_OPTION_CUEING_5', '5'),
    ('IFEI_FUEL_DOWN', '123456'),
    ('IFEI_FUEL_UP', '234567')
]
viper_bios = [
    ('DED_LINE_1', 'a2345678901234567890123456789'),
    ('DED_LINE_2', 'b2345678901234567890123456789'),
    ('DED_LINE_3', 'c2345678901234567890123456789'),
    ('DED_LINE_4', 'd2345678901234567890123456789'),
    ('DED_LINE_5', 'f2345678901234567890123456789')
]
shark_bios = [
    ('PVI_LINE1_APOSTROPHE1', '`'),
    ('PVI_LINE1_APOSTROPHE2', '`'),
    ('PVI_LINE1_POINT', '1'),
    ('PVI_LINE1_SIGN', '-'),
    ('PVI_LINE1_TEXT', '123456'),
    ('PVI_LINE2_APOSTROPHE1', '`'),
    ('PVI_LINE2_APOSTROPHE2', '`'),
    ('PVI_LINE2_POINT', '2'),
    ('PVI_LINE2_SIGN', ' '),
    ('PVI_LINE2_TEXT', '654321'),
    ('AP_ALT_HOLD_LED', 1),
    ('AP_BANK_HOLD_LED', 0),
    ('AP_FD_LED', 1),
    ('AP_HDG_HOLD_LED', 0),
    ('AP_PITCH_HOLD_LED', 1)
]
apache_bios = [
    ('PLT_EUFD_LINE8', '~<>VHF*  121.000   -----              121.500   -----   '),
    ('PLT_EUFD_LINE9', ' ==UHF*  305.000   -----              305.000   -----   '),
    ('PLT_EUFD_LINE10', ' ==FM1*   30.000   -----    NORM       30.000   -----   '),
    ('PLT_EUFD_LINE11', ' ==FM2*   30.000   -----               30.000   -----   '),
    ('PLT_EUFD_LINE12', ' ==HF *    2.0000A -----    LOW         2.0000A -----   ')
]
warthog_bios = [
    ('VHFAM_FREQ1', '20'),
    ('VHFAM_FREQ2', 1),
    ('VHFAM_FREQ3', 1),
    ('VHFAM_FREQ4', '30'),
    ('VHFFM_FREQ1', '40'),
    ('VHFFM_FREQ2', 2),
    ('VHFFM_FREQ3', 2),
    ('VHFFM_FREQ4', '50'),
    ('UHF_100MHZ_SEL', '5'),
    ('UHF_10MHZ_SEL', 3),
    ('UHF_1MHZ_SEL', 2),
    ('UHF_POINT1MHZ_SEL', 1),
    ('UHF_POINT25_SEL', '25')
]
harrier_bios = [
    ('UFC_SCRATCHPAD', '123456789012'),
    ('UFC_COMM1_DISPLAY', '11'),
    ('UFC_COMM2_DISPLAY', '22'),
    ('AV8BNA_ODU_1_SELECT', '1'),
    ('AV8BNA_ODU_1_Text', '1234'),
    ('AV8BNA_ODU_2_SELECT', '2'),
    ('AV8BNA_ODU_2_Text', '2345'),
    ('AV8BNA_ODU_3_SELECT', '3'),
    ('AV8BNA_ODU_3_Text', '3456'),
    ('AV8BNA_ODU_4_SELECT', '4'),
    ('AV8BNA_ODU_4_Text', '4567'),
    ('AV8BNA_ODU_5_SELECT', '5'),
    ('AV8BNA_ODU_5_Text', '5678')
]


@mark.parametrize('model, bios_pairs', [
    ('hornet_mono', hornet_bios),
    ('hornet_color', hornet_bios),
    ('viper_mono', viper_bios),
    ('viper_color', viper_bios),
    ('shark_mono', shark_bios),
    ('shark_color', shark_bios),
    ('apache_mono', apache_bios),
    ('apache_color', apache_bios),
    ('warthog_mono', warthog_bios),
    ('warthog_color', warthog_bios),
    ('warthog2_mono', warthog_bios),
    ('warthog2_color', warthog_bios),
    ('tomcat_mono', []),
    ('tomcat_color', []),
    ('harrier_mono', harrier_bios),
    ('harrier_color', harrier_bios),
])
def test_prepare_image_for_all_planes(model, bios_pairs, request):
    aircraft_model = request.getfixturevalue(model)
    set_bios_during_test(aircraft_model, bios_pairs)
    img = aircraft_model.prepare_image()
    assert isinstance(img, PIL.Image.Image)
    ref_img = PIL.Image.open(path.join(resources, f'{platform}_{model}_{aircraft_model.__class__.__name__}.png'))
    assert img.tobytes() == ref_img.tobytes()
    assert not ImageChops.difference(img, ref_img).getbbox()


def test_prepare_image_for_apache_mono_wca_mode(apache_mono):
    from dcspy.aircraft import ApacheEufdMode
    bios_pairs = [
        ('PLT_EUFD_LINE1', 'LOW ROTOR RPM     |RECTIFIER 2 FAIL  |CHARGER           '),
        ('PLT_EUFD_LINE2', 'ENGINE 2 OUT      |GENERATOR 2 FAIL  |TAIL WHL LOCK SEL '),
        ('PLT_EUFD_LINE3', 'ENGINE 1 OUT      |AFT FUEL LOW      |                  '),
        ('PLT_EUFD_LINE4', '                  |FORWARD FUEL LOW  |                  '),
        ('PLT_EUFD_LINE5', '                  |                  |                  ')
    ]
    set_bios_during_test(apache_mono, bios_pairs)
    apache_mono.mode = ApacheEufdMode.WCA
    img = apache_mono.prepare_image()
    assert isinstance(img, PIL.Image.Image)
    ref_img = PIL.Image.open(path.join(resources, 'apache_mono_wca_mode.png'))
    # assert img.tobytes() == ref_img.tobytes()
    diff = ImageChops.difference(img, ref_img)
    if platform == 'win32':
        img.save(f'{platform}_apache_mono_wca_mode.png')
    assert not ImageChops.difference(img, ref_img).getbbox()


# <=><=><=><=><=> Apache special <=><=><=><=><=>
def test_apache_mono_wca_more_then_one_screen(apache_mono):
    from dcspy.aircraft import ApacheEufdMode
    bios_pairs = [
        ('PLT_EUFD_LINE1', 'LOW ROTOR RPM     |RECTIFIER 2 FAIL  |CHARGER           '),
        ('PLT_EUFD_LINE2', 'ENGINE 2 OUT      |GENERATOR 2 FAIL  |TAIL WHL LOCK SEL '),
        ('PLT_EUFD_LINE3', 'ENGINE 1 OUT      |AFT FUEL LOW      |                  ')
    ]
    set_bios_during_test(apache_mono, bios_pairs)
    apache_mono.mode = ApacheEufdMode.WCA

    for i in range(1, 5):
        assert apache_mono.warning_line == i
        apache_mono.warning_line += 1
        apache_mono.prepare_image()
    assert apache_mono.warning_line == 1
    img = apache_mono.prepare_image()
    assert isinstance(img, PIL.Image.Image)
    ref_img = PIL.Image.open(path.join(resources, 'apache_mono_wca_mode.png'))
    diff = ImageChops.difference(img, ref_img)
    if platform == 'win32':
        img.save(f'{platform}_apache_mono_wca_mode.png')
    # assert img.tobytes() == ref_img.tobytes()
    assert not ImageChops.difference(img, ref_img).getbbox()


apache_pre_mono_bios = [
    ('PLT_EUFD_LINE1', 'LOW ROTOR RPM     |RECTIFIER 2 FAIL  |PRESET TUNE VHF   '),
    ('PLT_EUFD_LINE2', 'ENGINE 2 OUT      |GENERATOR 2 FAIL  |!CO CMD   127.000 '),
    ('PLT_EUFD_LINE3', 'ENGINE 1 OUT      |AFT FUEL LOW      | D/1/227  135.000 '),
    ('PLT_EUFD_LINE4', '                  |FORWARD FUEL LOW  | JAAT     136.000 '),
    ('PLT_EUFD_LINE5', '                  |                  | BDE/HIG  127.000 '),
    ('PLT_EUFD_LINE6', '                                     | FAAD     125.000 '),
    ('PLT_EUFD_LINE7', '                                     | JTAC     121.000 '),
    ('PLT_EUFD_LINE8', '~<>VHF*  127.000   -----             | AWACS    141.000 '),
    ('PLT_EUFD_LINE9', ' ==UHF*  305.000   -----             | FLIGHT   128.000 '),
    ('PLT_EUFD_LINE10', ' ==FM1*   30.000   -----    NORM     | BATUMI   126.000 '),
    ('PLT_EUFD_LINE11', ' ==FM2*   30.000   -----             | COMMAND  137.000 ')
]
apache_pre_color_bios = [
    ('PLT_EUFD_LINE1', 'LOW ROTOR RPM     |RECTIFIER 2 FAIL  |PRESET TUNE VHF   '),
    ('PLT_EUFD_LINE2', 'ENGINE 2 OUT      |GENERATOR 2 FAIL  |!CO CMD   127.000 '),
    ('PLT_EUFD_LINE3', 'ENGINE 1 OUT      |AFT FUEL LOW      | D/1/227  135.000 '),
    ('PLT_EUFD_LINE4', '                  |FORWARD FUEL LOW  | JAAT     136.000 '),
    ('PLT_EUFD_LINE5', '                  |                  | BDE/HIG  127.000 '),
    ('PLT_EUFD_LINE6', '                                     | FAAD     125.000 '),
    ('PLT_EUFD_LINE7', '                                     | JTAC     121.000 '),
    ('PLT_EUFD_LINE8', '~<>VHF*  127.000   -----             | AWACS    141.000 '),
    ('PLT_EUFD_LINE9', ' ==UHF*  305.000   -----             | FLIGHT   128.000 '),
    ('PLT_EUFD_LINE10', ' ==FM1*   30.000   -----    NORM     | BATUMI   126.000 '),
    ('PLT_EUFD_LINE11', ' ==FM2*   30.000   -----             | COMMAND  137.000 ')
]


@mark.parametrize('model, bios_pairs, filename', [
    ('apache_mono', apache_pre_mono_bios, 'apache_mono_pre_mode.png'),
    ('apache_color', apache_pre_color_bios, 'apache_color_pre_mode.png')
])
def test_apache_pre_mode(model, bios_pairs, filename, request):
    aircraft_model = request.getfixturevalue(model)
    set_bios_during_test(aircraft_model, bios_pairs)
    img = aircraft_model.prepare_image()
    assert isinstance(img, PIL.Image.Image)
    ref_img = PIL.Image.open(path.join(resources, filename))
    diff = ImageChops.difference(img, ref_img)
    if platform == 'win32':
        img.save(f'{platform}_filename')
    # assert img.tobytes() == ref_img.tobytes()
    assert not ImageChops.difference(img, ref_img).getbbox()
