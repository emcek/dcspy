from pathlib import Path
from sys import platform
from unittest.mock import patch

from pytest import mark, raises

from dcspy.models import KEY_DOWN, LcdButton
from tests.helpers import all_plane_list, compare_images, set_bios_during_test


# <=><=><=><=><=> Base Class <=><=><=><=><=>
@mark.parametrize('plane', all_plane_list)
def test_check_all_aircraft_inherit_from_correct_base_class(plane, request):
    from dcspy import aircraft
    plane = request.getfixturevalue(f'{plane}_mono')
    assert isinstance(plane, aircraft.BasicAircraft)


@mark.parametrize('selector, data, value, c_func, effect, plane', [
    ('field1', {'addr': 0xdeadbeef, 'len': 16, 'value': ''}, 'val1', 'logi_lcd_mono_set_background', [True], 'advancedaircraft_mono'),
    ('field2', {'addr': 0xdeadbeef, 'len': 16, 'value': ''}, 'val2', 'logi_lcd_color_set_background', [False, True], 'advancedaircraft_color'),
], ids=['Mono LCD', 'Color LCD'])
def test_aircraft_base_class_set_bios(selector, data, value, c_func, effect, plane, request):
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    aircraft = request.getfixturevalue(plane)
    assert aircraft.bios_data == {}
    aircraft.bios_data = {selector: data}

    with patch.object(LcdSdkManager, c_func, return_value=True), \
            patch.object(LcdSdkManager, 'logi_lcd_update', return_value=True):
        assert aircraft.bios_data[selector]['value'] == ''
        assert aircraft.get_bios('none') == ''
        with raises(NotImplementedError):
            aircraft.set_bios(selector, value)


@mark.parametrize('c_func, plane', [
    ('logi_lcd_mono_set_background', 'advancedaircraft_mono'),
    ('logi_lcd_color_set_background', 'advancedaircraft_color'),
], ids=['Mono LCD', 'Color LCD'])
def test_aircraft_base_class_prepare_img(c_func, plane, request):
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    aircraft = request.getfixturevalue(plane)
    with patch.object(LcdSdkManager, c_func, return_value=True), \
            patch.object(LcdSdkManager, 'logi_lcd_update', return_value=True), \
            raises(NotImplementedError):
        aircraft.prepare_image()


@mark.parametrize('keyboard, plane_name', [
    ('keyboard_mono', 'F-22A'),
    ('keyboard_color', 'UH-60L'),
], ids=['F-22A Mono Keyboard', 'UH-60L Color Keyboard'])
def test_meta_plane(keyboard, plane_name, request):
    from dcspy.aircraft import BasicAircraft, MetaAircraft
    from dcspy.logitech import LogitechDevice

    keyboard: LogitechDevice = request.getfixturevalue(keyboard)
    plane = MetaAircraft(plane_name, (BasicAircraft,), {})(keyboard.model.lcd_info)
    assert isinstance(plane, BasicAircraft)
    assert type(plane).__name__ == plane_name


# <=><=><=><=><=> Button Requests <=><=><=><=><=>
@mark.parametrize('plane, button, result', [
    ('fa18chornet_mono', LcdButton.NONE, [b'\n']),
    ('fa18chornet_mono', LcdButton.ONE, [b'UFC_COMM1_CHANNEL_SELECT DEC\n']),
    ('fa18chornet_mono', LcdButton.TWO, [b'UFC_COMM1_CHANNEL_SELECT INC\n']),
    ('fa18chornet_mono', LcdButton.THREE, [b'UFC_COMM2_CHANNEL_SELECT DEC\n']),
    ('fa18chornet_mono', LcdButton.FOUR, [b'UFC_COMM2_CHANNEL_SELECT INC\n']),
    ('fa18chornet_color', LcdButton.NONE, [b'\n']),
    ('fa18chornet_color', LcdButton.LEFT, [b'UFC_COMM1_CHANNEL_SELECT DEC\n']),
    ('fa18chornet_color', LcdButton.RIGHT, [b'UFC_COMM1_CHANNEL_SELECT INC\n']),
    ('fa18chornet_color', LcdButton.DOWN, [b'UFC_COMM2_CHANNEL_SELECT DEC\n']),
    ('fa18chornet_color', LcdButton.UP, [b'UFC_COMM2_CHANNEL_SELECT INC\n']),
    ('fa18chornet_color', LcdButton.MENU, [b'IFEI_DWN_BTN 1\n']),
    ('fa18chornet_color', LcdButton.CANCEL, [b'IFEI_UP_BTN 1\n']),
    ('fa18chornet_color', LcdButton.OK, [b'HUD_ATT_SW 1\n']),
    ('av8bna_mono', LcdButton.NONE, [b'\n']),
    ('av8bna_mono', LcdButton.ONE, [b'UFC_COM1_SEL -3200\n']),
    ('av8bna_mono', LcdButton.TWO, [b'UFC_COM1_SEL +3200\n']),
    ('av8bna_mono', LcdButton.THREE, [b'UFC_COM2_SEL -3200\n']),
    ('av8bna_mono', LcdButton.FOUR, [b'UFC_COM2_SEL +3200\n']),
    ('av8bna_color', LcdButton.NONE, [b'\n']),
    ('av8bna_color', LcdButton.LEFT, [b'UFC_COM1_SEL -3200\n']),
    ('av8bna_color', LcdButton.RIGHT, [b'UFC_COM1_SEL +3200\n']),
    ('av8bna_color', LcdButton.DOWN, [b'UFC_COM2_SEL -3200\n']),
    ('av8bna_color', LcdButton.UP, [b'UFC_COM2_SEL +3200\n']),
    ('av8bna_color', LcdButton.MENU, [b'\n']),
    ('av8bna_color', LcdButton.CANCEL, [b'\n']),
    ('av8bna_color', LcdButton.OK, [b'\n']),
    ('f15ese_mono', LcdButton.NONE, [b'\n']),
    ('f15ese_mono', LcdButton.ONE, [b'F_UFC_PRE_CHAN_L_SEL -3200\n']),
    ('f15ese_mono', LcdButton.TWO, [b'F_UFC_PRE_CHAN_L_SEL +3200\n']),
    ('f15ese_mono', LcdButton.THREE, [b'F_UFC_PRE_CHAN_R_SEL -3200\n']),
    ('f15ese_mono', LcdButton.FOUR, [b'F_UFC_PRE_CHAN_R_SEL +3200\n']),
    ('f15ese_color', LcdButton.NONE, [b'\n']),
    ('f15ese_color', LcdButton.LEFT, [b'F_UFC_PRE_CHAN_L_SEL -3200\n']),
    ('f15ese_color', LcdButton.RIGHT, [b'F_UFC_PRE_CHAN_L_SEL +3200\n']),
    ('f15ese_color', LcdButton.DOWN, [b'F_UFC_PRE_CHAN_R_SEL -3200\n']),
    ('f15ese_color', LcdButton.UP, [b'F_UFC_PRE_CHAN_R_SEL +3200\n']),
    ('f15ese_color', LcdButton.MENU, [b'F_UFC_KEY_L_GUARD 1\n', b'F_UFC_KEY_L_GUARD 0\n']),
    ('f15ese_color', LcdButton.CANCEL, [b'F_UFC_KEY_R_GUARD 1\n', b'F_UFC_KEY_R_GUARD 0\n']),
    ('f15ese_color', LcdButton.OK, [b'\n']),
    ('ka50_mono', LcdButton.NONE, [b'\n']),
    ('ka50_mono', LcdButton.ONE, [b'PVI_WAYPOINTS_BTN 1\n', b'PVI_WAYPOINTS_BTN 0\n']),
    ('ka50_mono', LcdButton.TWO, [b'PVI_FIXPOINTS_BTN 1\n', b'PVI_FIXPOINTS_BTN 0\n']),
    ('ka50_mono', LcdButton.THREE, [b'PVI_AIRFIELDS_BTN 1\n', b'PVI_AIRFIELDS_BTN 0\n']),
    ('ka50_mono', LcdButton.FOUR, [b'PVI_TARGETS_BTN 1\n', b'PVI_TARGETS_BTN 0\n']),
    ('ka50_color', LcdButton.NONE, [b'\n']),
    ('ka50_color', LcdButton.LEFT, [b'PVI_WAYPOINTS_BTN 1\n', b'PVI_WAYPOINTS_BTN 0\n']),
    ('ka50_color', LcdButton.RIGHT, [b'PVI_FIXPOINTS_BTN 1\n', b'PVI_FIXPOINTS_BTN 0\n']),
    ('ka50_color', LcdButton.DOWN, [b'PVI_AIRFIELDS_BTN 1\n', b'PVI_AIRFIELDS_BTN 0\n']),
    ('ka50_color', LcdButton.UP, [b'PVI_TARGETS_BTN 1\n', b'PVI_TARGETS_BTN 0\n']),
    ('ka50_color', LcdButton.MENU, [b'\n']),
    ('ka50_color', LcdButton.CANCEL, [b'\n']),
    ('ka50_color', LcdButton.OK, [b'\n']),
    ('ka503_mono', LcdButton.NONE, [b'\n']),
    ('ka503_mono', LcdButton.ONE, [b'PVI_WAYPOINTS_BTN 1\n', b'PVI_WAYPOINTS_BTN 0\n']),
    ('ka503_mono', LcdButton.TWO, [b'PVI_FIXPOINTS_BTN 1\n', b'PVI_FIXPOINTS_BTN 0\n']),
    ('ka503_mono', LcdButton.THREE, [b'PVI_AIRFIELDS_BTN 1\n', b'PVI_AIRFIELDS_BTN 0\n']),
    ('ka503_mono', LcdButton.FOUR, [b'PVI_TARGETS_BTN 1\n', b'PVI_TARGETS_BTN 0\n']),
    ('ka503_color', LcdButton.NONE, [b'\n']),
    ('ka503_color', LcdButton.LEFT, [b'PVI_WAYPOINTS_BTN 1\n', b'PVI_WAYPOINTS_BTN 0\n']),
    ('ka503_color', LcdButton.RIGHT, [b'PVI_FIXPOINTS_BTN 1\n', b'PVI_FIXPOINTS_BTN 0\n']),
    ('ka503_color', LcdButton.DOWN, [b'PVI_AIRFIELDS_BTN 1\n', b'PVI_AIRFIELDS_BTN 0\n']),
    ('ka503_color', LcdButton.UP, [b'PVI_TARGETS_BTN 1\n', b'PVI_TARGETS_BTN 0\n']),
    ('ka503_color', LcdButton.MENU, [b'\n']),
    ('ka503_color', LcdButton.CANCEL, [b'\n']),
    ('ka503_color', LcdButton.OK, [b'\n']),
    ('f14a135gr_mono', LcdButton.NONE, [b'\n']),
    ('f14a135gr_mono', LcdButton.ONE, [b'RIO_CAP_CLEAR 1\n', b'RIO_CAP_CLEAR 0\n']),
    ('f14a135gr_mono', LcdButton.TWO, [b'RIO_CAP_SW 1\n', b'RIO_CAP_SW 0\n']),
    ('f14a135gr_mono', LcdButton.THREE, [b'RIO_CAP_NE 1\n', b'RIO_CAP_NE 0\n']),
    ('f14a135gr_mono', LcdButton.FOUR, [b'RIO_CAP_ENTER 1\n', b'RIO_CAP_ENTER 0\n']),
    ('f14a135gr_color', LcdButton.NONE, [b'\n']),
    ('f14a135gr_color', LcdButton.LEFT, [b'RIO_CAP_CLEAR 1\n', b'RIO_CAP_CLEAR 0\n']),
    ('f14a135gr_color', LcdButton.RIGHT, [b'RIO_CAP_SW 1\n', b'RIO_CAP_SW 0\n']),
    ('f14a135gr_color', LcdButton.DOWN, [b'RIO_CAP_NE 1\n', b'RIO_CAP_NE 0\n']),
    ('f14a135gr_color', LcdButton.UP, [b'RIO_CAP_ENTER 1\n', b'RIO_CAP_ENTER 0\n']),
    ('f14a135gr_color', LcdButton.MENU, [b'\n']),
    ('f14a135gr_color', LcdButton.CANCEL, [b'\n']),
    ('f14a135gr_color', LcdButton.OK, [b'\n']),
    ('f14b_mono', LcdButton.NONE, [b'\n']),
    ('f14b_mono', LcdButton.ONE, [b'RIO_CAP_CLEAR 1\n', b'RIO_CAP_CLEAR 0\n']),
    ('f14b_mono', LcdButton.TWO, [b'RIO_CAP_SW 1\n', b'RIO_CAP_SW 0\n']),
    ('f14b_mono', LcdButton.THREE, [b'RIO_CAP_NE 1\n', b'RIO_CAP_NE 0\n']),
    ('f14b_mono', LcdButton.FOUR, [b'RIO_CAP_ENTER 1\n', b'RIO_CAP_ENTER 0\n']),
    ('f14b_color', LcdButton.NONE, [b'\n']),
    ('f14b_color', LcdButton.LEFT, [b'RIO_CAP_CLEAR 1\n', b'RIO_CAP_CLEAR 0\n']),
    ('f14b_color', LcdButton.RIGHT, [b'RIO_CAP_SW 1\n', b'RIO_CAP_SW 0\n']),
    ('f14b_color', LcdButton.DOWN, [b'RIO_CAP_NE 1\n', b'RIO_CAP_NE 0\n']),
    ('f14b_color', LcdButton.UP, [b'RIO_CAP_ENTER 1\n', b'RIO_CAP_ENTER 0\n']),
    ('f14b_color', LcdButton.MENU, [b'\n']),
    ('f14b_color', LcdButton.CANCEL, [b'\n']),
    ('f14b_color', LcdButton.OK, [b'\n']),
    ('f16c50_mono', LcdButton.NONE, [b'\n']),
    ('f16c50_mono', LcdButton.ONE, [b'IFF_MASTER_KNB 1\n']),
    ('f16c50_mono', LcdButton.TWO, [b'IFF_ENABLE_SW 1\n']),
    ('f16c50_mono', LcdButton.THREE, [b'IFF_M4_CODE_SW 1\n']),
    ('f16c50_mono', LcdButton.FOUR, [b'IFF_M4_REPLY_SW 1\n']),
    ('f16c50_color', LcdButton.NONE, [b'\n']),
    ('f16c50_color', LcdButton.LEFT, [b'IFF_MASTER_KNB 1\n']),
    ('f16c50_color', LcdButton.RIGHT, [b'IFF_ENABLE_SW 1\n']),
    ('f16c50_color', LcdButton.DOWN, [b'IFF_M4_CODE_SW 1\n']),
    ('f16c50_color', LcdButton.UP, [b'IFF_M4_REPLY_SW 1\n']),
    ('f16c50_color', LcdButton.MENU, [b'\n']),
    ('f16c50_color', LcdButton.CANCEL, [b'\n']),
    ('f16c50_color', LcdButton.OK, [b'\n']),
    ('ah64dblkii_mono', LcdButton.NONE, [b'\n']),
    ('ah64dblkii_mono', LcdButton.ONE, [b'PLT_EUFD_IDM 0\n', b'PLT_EUFD_IDM 1\n']),
    ('ah64dblkii_mono', LcdButton.TWO, [b'PLT_EUFD_RTS 0\n', b'PLT_EUFD_RTS 1\n']),
    ('ah64dblkii_mono', LcdButton.THREE, [b'PLT_EUFD_PRESET 0\n', b'PLT_EUFD_PRESET 1\n']),
    ('ah64dblkii_mono', LcdButton.FOUR, [b'PLT_EUFD_ENT 0\n', b'PLT_EUFD_ENT 1\n']),
])
def test_button_pressed_for_planes(plane, button, result, request):
    plane = request.getfixturevalue(plane)
    key_req = plane.button_request(button)
    assert list(key_req.bytes_requests(key_down=KEY_DOWN)) == result


@mark.parametrize('button, result', [
    (LcdButton.NONE, [b'\n']),
    (LcdButton.LEFT, [b'PLT_EUFD_WCA 0\n', b'PLT_EUFD_WCA 1\n']),
    (LcdButton.RIGHT, [b'PLT_EUFD_RTS 0\n', b'PLT_EUFD_RTS 1\n']),
    (LcdButton.DOWN, [b'PLT_EUFD_PRESET 0\n', b'PLT_EUFD_PRESET 1\n']),
    (LcdButton.UP, [b'PLT_EUFD_ENT 0\n', b'PLT_EUFD_ENT 1\n']),
    (LcdButton.MENU, [b'\n']),
    (LcdButton.CANCEL, [b'\n']),
    (LcdButton.OK, [b'\n']),
], ids=['NONE', 'LEFT', 'RIGHT', 'DOWN', 'UP', 'MENU', 'CANCEL', 'OK'])
def test_button_pressed_for_apache_color(button, result, ah64dblkii_color):
    from dcspy.aircraft import ApacheEufdMode
    ah64dblkii_color.mode = ApacheEufdMode.WCA
    key_req = ah64dblkii_color.button_request(button)
    assert list(key_req.bytes_requests(key_down=KEY_DOWN)) == result


@mark.parametrize('plane, ctrl_name, btn, values', [
    ('f16c50_mono', 'IFF_MASTER_KNB', LcdButton.ONE, (1, 2, 3, 4, 3, 2, 1, 0, 1)),
    ('f16c50_mono', 'IFF_ENABLE_SW', LcdButton.TWO, (1, 2, 1, 0, 1)),
    ('f16c50_mono', 'IFF_M4_CODE_SW', LcdButton.THREE, (1, 2, 1, 0, 1)),
    ('f16c50_mono', 'IFF_M4_REPLY_SW', LcdButton.FOUR, (1, 2, 1, 0, 1)),
    ('f16c50_color', 'IFF_MASTER_KNB', LcdButton.LEFT, (1, 2, 3, 4, 3, 2, 1, 0, 1)),
    ('f16c50_color', 'IFF_ENABLE_SW', LcdButton.RIGHT, (1, 2, 1, 0, 1)),
    ('f16c50_color', 'IFF_M4_CODE_SW', LcdButton.DOWN, (1, 2, 1, 0, 1)),
    ('f16c50_color', 'IFF_M4_REPLY_SW', LcdButton.UP, (1, 2, 1, 0, 1)),
    ('fa18chornet_color', 'HUD_ATT_SW', LcdButton.OK, (1, 2, 1, 0, 1)),
    ('fa18chornet_color', 'IFEI_DWN_BTN', LcdButton.MENU, (1, 0, 1)),
    ('fa18chornet_color', 'IFEI_UP_BTN', LcdButton.CANCEL, (1, 0, 1)),
], ids=[
    'ONE - Viper Mono',
    'TWO - Viper Mono',
    'THREE - Viper Mono',
    'FOUR - Viper Mono',
    'LEFT - Viper Color',
    'RIGHT - Viper Color',
    'DOWN - Viper Color',
    'UP - Viper Color',
    'OK - Hornet Color',
    'MENU - Hornet Color',
    'CANCEL - Hornet Color'])
def test_get_next_value_for_cycle_buttons(plane, ctrl_name, btn, values, request):
    plane = request.getfixturevalue(plane)
    generated_out = []
    expected_out = []
    for val in values:
        key_req = plane.button_request(btn)
        generated_out.extend(key_req.bytes_requests(key_down=KEY_DOWN))
        expected_out.extend([f'{ctrl_name} {val}\n'.encode('ascii')])
    assert generated_out == expected_out


# <=><=><=><=><=> Set BIOS <=><=><=><=><=>
@mark.parametrize('plane, bios_pairs, result', [
    ('fa18chornet_mono', [('UFC_SCRATCHPAD_STRING_2_DISPLAY', '~~')], '22'),
    ('fa18chornet_mono', [('UFC_COMM1_DISPLAY', '``')], '11'),
    ('fa18chornet_mono', [('IFEI_FUEL_UP', '104T')], '104T'),
    ('fa18chornet_color', [('UFC_SCRATCHPAD_STRING_1_DISPLAY', '~~')], '22'),
    ('fa18chornet_color', [('UFC_COMM1_DISPLAY', '``')], '11'),
    ('fa18chornet_color', [('IFEI_FUEL_UP', '1000T')], '1000T'),
    ('f16c50_mono', [('DED_LINE_1', 'a')], '\u2666'),
    ('f16c50_mono', [('DED_LINE_2', 'o')], '\u00b0'),
    ('f16c50_mono', [('DED_LINE_3', '*')], '\u25d9'),
    ('f16c50_mono', [('DED_LINE_5', '\x07')], ''),
    ('f16c50_mono', [('DED_LINE_4', '\x10')], ''),
    ('f16c50_mono', [('DED_LINE_2', '   @')], '   '),
    ('f16c50_color', [('DED_LINE_3', 'a')], '\u0040'),
    ('f16c50_color', [('DED_LINE_4', 'o')], '\u005e'),
    ('f16c50_color', [('DED_LINE_3', '*')], '\u00d7'),
    ('f16c50_color', [('DED_LINE_5', '\xfe')], ''),
    ('f16c50_color', [('DED_LINE_1', '\xfc')], ''),
    ('f16c50_color', [('DED_LINE_2', '   @')], '   '),
    ('f16c50_color', [('DED_LINE_2', '1DEST 2BNGO 3VIP  RINTG  A\x10\x04')], 'ÁDEST ÂBNGO ÃVIP  rINTG  '),
    ('f16c50_color', [('DED_LINE_3', '4NAV  5MAN  6INS  EDLNK  A\x10\x04')], 'ÄNAV  ÅMAN  ÆINS  eDLNK  '),
    ('f16c50_color', [('DED_LINE_4', '7CMDS 8MODE 9VRP  0MISC  A\x10\x04')], 'ÇCMDS ÈMODE ÉVRP  ÀMISC  '),
    ('f16c50_mono', [('DED_LINE_1', '       *      *CMD STRG  \x80@')], '       \u25d9      \u25d9CMD STRG  '),
    ('f16c50_mono', [('DED_LINE_2', '1DEST 2BNGO 3VIP  RINTG  A\x10\x04')], '1DEST 2BNGO 3VIP  RINTG  '),
    ('f16c50_mono', [('DED_LINE_1', ' MARK *HUD *    26a      @')], ' MARK \u25d9HUD \u25d9    26\u2666      '),
    ('f16c50_mono', [('DED_LINE_5', 'M3 :7000 *     *DCPL(9)  \x03\x82')], 'M3 :7000 \u25d9     \u25d9DCPL(9)  '),
    ('ah64dblkii_mono', [('PLT_EUFD_LINE8', '~=>VHF*  121.000   -----              121.500   -----   ')], '\u25a0\u2219\u25b8VHF*  121.000   -----              121.500   -----   '),
    ('ah64dblkii_mono', [('PLT_EUFD_LINE9', ' <=UHF*  305.000   -----              305.000   -----   ')], ' \u25c2\u2219UHF*  305.000   -----              305.000   -----   '),
    ('ah64dblkii_mono', [('PLT_EUFD_LINE10', ' <>FM1*   30.000   -----    NORM       30.000   -----   ')], ' \u25c2\u25b8FM1*   30.000   -----    NORM       30.000   -----   '),
    ('ah64dblkii_color', [('PLT_EUFD_LINE11', '[==FM2*   30.000   -----               30.000   -----   ')], '\u25ca\u2219\u2219FM2*   30.000   -----               30.000   -----   '),
    ('ah64dblkii_color', [('PLT_EUFD_LINE12', ' ==HF *    2.0000A -----    LOW         2.0000A -----   ')], ' \u2219\u2219HF *    2.0000A -----    LOW         2.0000A -----   '),
    ('ah64dblkii_color', [('PLT_EUFD_LINE12', ']==HF *    2.0000A -----    LOW         2.0000A -----   ')], '\u2666\u2219\u2219HF *    2.0000A -----    LOW         2.0000A -----   '),
])
def test_set_bios_for_airplane(plane, bios_pairs, result, request):
    plane = request.getfixturevalue(plane)
    set_bios_during_test(plane, bios_pairs)
    assert plane.bios_data[bios_pairs[0][0]] == result


@mark.parametrize('plane, bios_pairs, mode', [
    ('ah64dblkii_mono', [('PLT_EUFD_LINE1', 'ENGINE 1 OUT      |AFT FUEL LOW      |TAIL WHL LOCK SEL ')], 'IDM'),
    ('ah64dblkii_mono', [('PLT_EUFD_LINE1', '                  |AFT FUEL LOW      |PRESET TUNE VHS ')], 'PRE'),
    ('ah64dblkii_color', [('PLT_EUFD_LINE1', '                  |                  |TAIL WHL LOCK SEL ')], 'IDM'),
    ('ah64dblkii_color', [('PLT_EUFD_LINE1', '                  |AFT FUEL LOW      |TAIL WHL LOCK SEL ')], 'IDM'),
    ('ah64dblkii_color', [('PLT_EUFD_LINE1', 'ENGINE 1 OUT      |AFT FUEL LOW      |PRESET TUNE FM1 ')], 'PRE'),
], ids=['Mono IDM', 'Mono PRE', 'Color IDM 1', 'Color IDM 2', 'Color PRE'])
def test_apache_mode_switch_idm_pre_for_apache(plane, bios_pairs, mode, request):
    plane = request.getfixturevalue(plane)
    set_bios_during_test(plane, bios_pairs)
    assert plane.mode.name == mode


# <=><=><=><=><=> Prepare Image <=><=><=><=><=>
@mark.parametrize('lcd', ['mono', 'color'])
@mark.parametrize('model', all_plane_list)
def test_prepare_image_for_all_planes(model, lcd, resources, img_precision, request):
    aircraft_model = request.getfixturevalue(f'{model}_{lcd}')
    bios_pairs = request.getfixturevalue(f'{model}_{lcd}_bios')
    set_bios_during_test(aircraft_model, bios_pairs)
    img = aircraft_model.prepare_image()
    # if 'ka50' in model or 'mi8' in model or 'mi24' in model:
    #     img.save(resources / platform / f'new_{model}_{lcd}_{type(aircraft_model).__name__}.png')
    # else:
    assert compare_images(img=img, file_path=resources / platform / f'{model}_{lcd}_{type(aircraft_model).__name__}.png', precision=img_precision)


@mark.parametrize('model', ['ah64dblkii_mono', 'ah64dblkii_color'], ids=['Mono LCD', 'Color LCD'])
def test_prepare_image_for_apache_wca_mode(model, resources, img_precision, request):
    from itertools import repeat
    from tempfile import gettempdir

    from dcspy.aircraft import ApacheEufdMode

    apache = request.getfixturevalue(model)
    apache._debug_img = repeat(999)
    bios_pairs = [
        ('PLT_EUFD_LINE1', 'LOW ROTOR RPM     |RECTIFIER 2 FAIL  |CHARGER           '),
        ('PLT_EUFD_LINE2', 'ENGINE 2 OUT      |GENERATOR 2 FAIL  |TAIL WHL LOCK SEL '),
        ('PLT_EUFD_LINE3', 'ENGINE 1 OUT      |AFT FUEL LOW      |                  '),
        ('PLT_EUFD_LINE4', '                  |FORWARD FUEL LOW  |                  '),
        ('PLT_EUFD_LINE5', '                  |                  |                  '),
    ]
    set_bios_during_test(apache, bios_pairs)
    apache.mode = ApacheEufdMode.WCA
    apache.cfg['save_lcd'] = True
    img = apache.prepare_image()
    assert (Path(gettempdir()) / f'{type(apache).__name__}_999.png').exists()
    assert compare_images(img=img, file_path=resources / platform / f'{model}_wca_mode.png', precision=img_precision)


# <=><=><=><=><=> Apache special <=><=><=><=><=>
@mark.parametrize('model', ['ah64dblkii_mono', 'ah64dblkii_color'], ids=['Mono LCD', 'Color LCD'])
def test_apache_wca_more_then_one_screen_scrolled(model, resources, img_precision, request):
    from dcspy.aircraft import ApacheEufdMode
    apache = request.getfixturevalue(model)
    bios_pairs = [
        ('PLT_EUFD_LINE1', 'LOW ROTOR RPM     |RECTIFIER 2 FAIL  |CHARGER           '),
        ('PLT_EUFD_LINE2', 'ENGINE 2 OUT      |GENERATOR 2 FAIL  |TAIL WHL LOCK SEL '),
        ('PLT_EUFD_LINE3', 'ENGINE 1 OUT      |AFT FUEL LOW      |                  '),
    ]
    set_bios_during_test(apache, bios_pairs)
    apache.mode = ApacheEufdMode.WCA

    for i in range(1, 3):
        assert apache.warning_line == i
        apache.warning_line += 1
        apache.prepare_image()
    assert apache.warning_line == 3
    img = apache.prepare_image()
    assert compare_images(img=img, file_path=resources / platform / f'{model}_wca_mode_scroll_3.png', precision=img_precision)

    for i in range(1, 3):
        apache.warning_line += 1
        apache.prepare_image()

    img = apache.prepare_image()
    assert apache.warning_line == 1
    assert compare_images(img=img, file_path=resources / platform / f'{model}_wca_mode_scroll_1.png', precision=img_precision)


@mark.parametrize('model', ['ah64dblkii_mono', 'ah64dblkii_color'], ids=['Mono LCD', 'Color LCD'])
def test_apache_pre_mode(model, apache_pre_mode_bios_data, resources, img_precision, request):
    apache = request.getfixturevalue(model)
    set_bios_during_test(apache, apache_pre_mode_bios_data)
    img = apache.prepare_image()
    assert compare_images(img=img, file_path=resources / platform / f'{model}_pre_mode.png', precision=img_precision)
