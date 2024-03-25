from pytest import mark, raises

from dcspy.models import KEY_DOWN, KEY_UP, LcdButton, LcdColor, LcdMono


# <=><=><=><=><=> Control / ControlKeyData <=><=><=><=><=>
@mark.parametrize('get_ctrl_for_plane, results', [
    (('FA-18C_hornet', 'UFC_COMM1_CHANNEL_SELECT'), [1, True, False, False, False, False]),
    (('Mi-24P', 'PLT_WIPER_OFF'), [2, True, True, False, False, False]),
    (('A-10C', 'AAP_PAGE'), [2, True, True, False, False, False]),
    (('A-10C', 'AAP_CDUPWR'), [3, True, True, False, True, True]),
    (('A-10C', 'TACAN_1'), [1, True, False, False, False, False]),
    (('A-10C', 'AAP_STEER'), [1, False, True, False, False, False]),
    (('F-14B', 'RIO_HCU_DDD'), [3, True, True, False, True, True]),
    (('A-10C', 'ADI_PITCH_TRIM'), [2, False, True, True, False, False]),
    (('A-10C', 'ARC210_CHN_KNB'), [1, False, False, True, False, False]),
    (('A-10C', 'UFC_1'), [3, True, True, False, True, True]),
], ids=[
    'UFC_COMM1_CHANNEL_SELECT', 'PLT_WIPER_OFF', 'AAP_PAGE', 'AAP_CDUPWR', 'TACAN_1', 'AAP_STEER', 'RIO_HCU_DDD', 'ADI_PITCH_TRIM', 'ARC210_CHN_KNB', 'UFC_1',
], indirect=['get_ctrl_for_plane'])
def test_control_input_properties(get_ctrl_for_plane, results):
    assert get_ctrl_for_plane.input.input_len == results[0]
    assert get_ctrl_for_plane.input.has_fixed_step is results[1]
    assert get_ctrl_for_plane.input.has_set_state is results[2]
    assert get_ctrl_for_plane.input.has_variable_step is results[3]
    assert get_ctrl_for_plane.input.has_action is results[4]
    assert get_ctrl_for_plane.input.is_push_button is results[5]


@mark.parametrize('get_ctrl_for_plane, max_value, step', [
    (('A-10C', 'UFC_1'), 1, 1),
    (('FA-18C_hornet', 'UFC_COMM1_CHANNEL_SELECT'), 1, 1),
    (('Mi-24P', 'PLT_WIPER_OFF'), 0, 1),
    (('A-10C', 'AAP_PAGE'), 3, 1),
    (('A-10C', 'AAP_CDUPWR'), 1, 1),
    (('A-10C', 'TACAN_1'), 1, 1),
    (('A-10C', 'AAP_STEER'), 2, 1),
    (('F-14B', 'RIO_HCU_DDD'), 1, 1),
    (('A-10C', 'ADI_PITCH_TRIM'), 65535, 3200),
    (('A-10C', 'ARC210_CHN_KNB'), 65535, 3200),
], ids=[
    'UFC_1', 'UFC_COMM1_CHANNEL_SELECT', 'PLT_WIPER_OFF', 'AAP_PAGE', 'AAP_CDUPWR', 'TACAN_1', 'AAP_STEER', 'RIO_HCU_DDD', 'ADI_PITCH_TRIM', 'ARC210_CHN_KNB',
], indirect=['get_ctrl_for_plane'])
def test_control_key_data_from_control(get_ctrl_for_plane, max_value, step):
    from dcspy.models import ControlKeyData

    ctrl_key = ControlKeyData.from_control(ctrl=get_ctrl_for_plane)
    assert ctrl_key.max_value == max_value
    assert ctrl_key.suggested_step == step
    assert len(ctrl_key.list_dict) == len(get_ctrl_for_plane.inputs)
    assert f'suggested_step={ctrl_key.suggested_step}' in repr(ctrl_key)
    assert f'KeyControl({ctrl_key.name}' in repr(ctrl_key)
    assert f'max_value={ctrl_key.max_value}' in repr(ctrl_key)


@mark.parametrize('get_ctrl_for_plane, result', [
    (('A-10C', 'AAP_PAGE'), 'IntegerBuffer'),
    (('A-10C', 'ARC210_CHN_KNB'), 'IntegerBuffer'),
    (('A-10C', 'ARC210_ACTIVE_CHANNEL'), 'StringBuffer'),
    (('A-10C', 'CMSP1'), 'StringBuffer'),
], ids=[
    'AAP_PAGE', 'ARC210_CHN_KNB', 'ARC210_ACTIVE_CHANNEL', 'CMSP1',
], indirect=['get_ctrl_for_plane'])
def test_control_output(get_ctrl_for_plane, result):
    assert get_ctrl_for_plane.output.klass == result


@mark.parametrize('get_ctrl_for_plane', [('FA-18C_hornet', 'UFC_COMM1_CHANNEL_SELECT')], indirect=True)
def test_control_no_output(get_ctrl_for_plane):
    with raises(IndexError):
        print(get_ctrl_for_plane.output)

    assert get_ctrl_for_plane.input.has_fixed_step


# <=><=><=><=><=> Gkey <=><=><=><=><=>
def test_gkey_from_yaml_success():
    from dcspy.models import Gkey

    gkey = Gkey.from_yaml('G22_M3')
    assert gkey.key == 22
    assert gkey.mode == 3


def test_gkey_from_yaml_value_error():
    from dcspy.models import Gkey

    with raises(ValueError):
        _ = Gkey.from_yaml('G_M1')


def test_generate_gkey():
    from dcspy.models import Gkey

    g_keys = Gkey.generate(key=3, mode=2)
    assert len(g_keys) == 6
    assert g_keys[0].key == 1
    assert g_keys[0].mode == 1
    assert g_keys[-1].key == 3
    assert g_keys[-1].mode == 2


def test_gkey_name():
    from dcspy.models import Gkey

    assert str(Gkey(key=1, mode=2)) == 'G1_M2'
    assert str(Gkey(key=3, mode=1)) == 'G3_M1'


@mark.parametrize('key_name, klass', [
    ('G12_M3', 'Gkey'),
    ('G1_M2', 'Gkey'),
    ('TWO', 'LcdButton'),
    ('MENU', 'LcdButton'),
    ('M_2', 'MouseButton'),
    ('M_12', 'MouseButton'),
])
def test_get_key_instance(key_name, klass):
    from dcspy.models import get_key_instance

    assert get_key_instance(key_name).__class__.__name__ == klass


@mark.parametrize('key_name', ['g12_M3', 'G1_m2', 'G1/M2', 'Two', 'ok', '', 'M_a3', 'm_2', 'M3'])
def test_get_key_instance_error(key_name):
    from dcspy.models import get_key_instance

    with raises(AttributeError):
        get_key_instance(key_name)


@mark.parametrize('key, mode, result', [(0, 0, False), (1, 0, False), (0, 2, False), (2, 3, True)])
def test_get_gkey_bool_test(key, mode, result):
    from dcspy.models import Gkey

    if Gkey(key=key, mode=mode):
        assert result
    else:
        assert not result


def test_get_gkey_as_dict_key():
    from dcspy.models import Gkey

    g1 = Gkey(key=2, mode=1)
    assert len({g1: str(g1)}) == 1


# <=><=><=><=> MouseButton <=><=><=><=>
def test_mouse_button_from_yaml_success():
    from dcspy.models import MouseButton

    m_btn = MouseButton.from_yaml('M_3')
    assert m_btn.button == 3


def test_mouse_button_from_yaml_value_error():
    from dcspy.models import MouseButton

    with raises(ValueError):
        _ = MouseButton.from_yaml('M_a1')


def test_generate_mouse_button():
    from dcspy.models import MouseButton

    mouse = MouseButton.generate((4, 8))
    assert len(mouse) == 5
    assert mouse[0].button == 4
    assert mouse[-1].button == 8


def test_mouse_button_name():
    from dcspy.models import MouseButton

    assert str(MouseButton(button=1)) == 'M_1'
    assert str(MouseButton(button=2)) == 'M_2'


@mark.parametrize('btn, result', [(0, False), (1, True), (2, True)])
def test_get_mouse_button_bool_test(btn, result):
    from dcspy.models import MouseButton

    if MouseButton(button=btn):
        assert result
    else:
        assert not result


def test_get_mouse_button_as_dict_key():
    from dcspy.models import MouseButton

    b_btn = MouseButton(button=2)
    assert len({b_btn: b_btn.button}) == 1


# <=><=><=><=><=> CycleButton <=><=><=><=><=>
def test_cycle_button_default_iter():
    from dcspy.models import CycleButton

    cb = CycleButton(ctrl_name='AAP_PAGE')
    assert cb.max_value == 1
    with raises(StopIteration):
        next(cb.iter)
        next(cb.iter)


def test_cycle_button_custom_iter():
    from dcspy.models import CycleButton

    max_val = 2
    cb = CycleButton(ctrl_name='AAP_PAGE', max_value=max_val, iter=iter(range(max_val + 1)))
    assert cb.max_value == max_val
    with raises(StopIteration):
        assert next(cb.iter) == 0
        assert next(cb.iter) == 1
        assert next(cb.iter) == 2
        next(cb.iter)


@mark.parametrize('name, req, step, max_val', [
    ('IFF_MASTER_KNB', 'CYCLE', 1, 4),
    ('ADI_PITCH_TRIM', 'CYCLE', 3200, 15000),
], ids=['IFF_MASTER_KNB CYCLE 1', 'ADI_PITCH_TRIM CYCLE 3200'])
def test_cycle_button_custom_constructor(name, req, step, max_val):
    from dcspy.models import CycleButton

    cb = CycleButton.from_request(f'{name} {req} {step} {max_val}')
    assert cb.max_value == max_val
    assert cb.step == step
    assert cb.ctrl_name == name
    with raises(StopIteration):
        next(cb.iter)
        next(cb.iter)


@mark.parametrize('name, req, step, max_val, result', [
    ('IFF_MASTER_KNB', 'CYCLE', 1, 4, True),
    ('', 'CYCLE', 0, 0, False),
], ids=['IFF_MASTER_KNB CYCLE 1', 'EMPTY CYCLE 0 0'])
def test_cycle_button_bool_test(name, req, step, max_val, result):
    from dcspy.models import CycleButton

    assert bool(CycleButton.from_request(f'{name} {req} {step} {max_val}')) is result


# <=><=><=><=><=> DeviceRowsNumber <=><=><=><=><=>
def test_device_row_number_model():
    from dcspy.models import DeviceRowsNumber
    device = DeviceRowsNumber(g_key=3, lcd_key=2, mouse_key=1)
    assert device.total == 6


# <=><=><=><=><=> LogitechDeviceModel <=><=><=><=><=>
@mark.parametrize('dev_kwargs, result', [
    ({'klass': '', 'no_g_modes': 2, 'no_g_keys': 4, 'lcd_info': LcdMono, 'lcd_keys': (LcdButton.ONE, LcdButton.TWO), 'btn_m_range': (6, 9)},
     (8, 4, 'mono', 'Mono LCD: 160x43 px\nLCD Buttons: ONE, TWO\nG-Keys: 4 in 2 modes\nMouse Buttons: 6 to 9', 2, 4, 2, 4, 10)),
    ({'klass': '', 'no_g_modes': 3, 'no_g_keys': 1, 'lcd_info': LcdColor, 'lcd_keys': (LcdButton.ONE,)},
     (3, 1, 'color', 'Color LCD: 320x240 px\nLCD Buttons: ONE\nG-Keys: 1 in 3 modes', 3, 1, 1, 0, 2)),
    ({'klass': '', 'no_g_modes': 1, 'no_g_keys': 3, 'lcd_info': LcdMono},
     (3, 1, 'mono', 'Mono LCD: 160x43 px\nG-Keys: 3 in 1 modes', 1, 3, 0, 0, 3)),
    ({'klass': '', 'no_g_modes': 3, 'no_g_keys': 2},
     (6, 1, 'none', 'G-Keys: 2 in 3 modes', 3, 2, 0, 0, 2)),
    ({'klass': '', 'no_g_modes': 2, 'no_g_keys': 4, 'lcd_keys': (LcdButton.ONE, LcdButton.TWO)},
     (8, 1, 'none', 'LCD Buttons: ONE, TWO\nG-Keys: 4 in 2 modes', 2, 4, 2, 0, 6)),
    ({'klass': '', 'no_g_modes': 2, 'no_g_keys': 4, 'btn_m_range': (1, 3)},
     (8, 3, 'none', 'G-Keys: 4 in 2 modes\nMouse Buttons: 1 to 3', 2, 4, 0, 3, 7)),
    ({'klass': '', 'lcd_keys': (LcdButton.ONE, LcdButton.TWO, LcdButton.THREE), 'btn_m_range': (4, 8)},
     (0, 5, 'none', 'LCD Buttons: ONE, TWO, THREE\nMouse Buttons: 4 to 8', 1, 0, 3, 5, 8)),
])
def test_logitech_device_model(dev_kwargs, result):
    from dcspy.models import LogitechDeviceModel
    dev = LogitechDeviceModel(**dev_kwargs)
    assert len(dev.g_keys) == result[0]
    assert len(dev.mouse_keys) == result[1]
    assert dev.lcd_name == result[2]
    assert str(dev) == result[3]
    assert dev.cols == result[4]
    assert dev.rows.g_key == result[5]
    assert dev.rows.lcd_key == result[6]
    assert dev.rows.mouse_key == result[7]
    assert dev.rows.total == result[8]


def test_get_key_at_of_logitech_device_model():
    from dcspy.models import Gkey, LogitechDeviceModel, MouseButton

    kwargs = {'klass': '', 'no_g_modes': 2, 'no_g_keys': 3, 'lcd_info': LcdMono, 'lcd_keys': (LcdButton.ONE, LcdButton.TWO), 'btn_m_range': (2, 4)}
    dev = LogitechDeviceModel(**kwargs)
    assert dev.get_key_at(row=1, col=1) == Gkey(key=2, mode=2)
    assert dev.get_key_at(row=3, col=0) == LcdButton.ONE
    assert dev.get_key_at(row=3, col=1) is None
    assert dev.get_key_at(row=6, col=0) == MouseButton(button=3)
    assert dev.get_key_at(row=6, col=1) is None
    assert dev.get_key_at(row=9, col=9) is None


# <=><=><=><=><=> DcsBiosPlaneData <=><=><=><=><=>
def test_get_ctrl(test_dcs_bios):
    from dcspy.utils import get_full_bios_for_plane

    json_data = get_full_bios_for_plane(plane='A-10C', bios_dir=test_dcs_bios)
    c = json_data.get_ctrl(ctrl_name='TACAN_MODE')
    assert c.output.max_value == 4
    assert c.input.one_input is False


def test_get_empty_ctrl(test_dcs_bios):
    from dcspy.utils import get_full_bios_for_plane

    json_data = get_full_bios_for_plane(plane='A-10C', bios_dir=test_dcs_bios)
    c = json_data.get_ctrl(ctrl_name='WRONG_CTRL')
    assert c is None


def test_get_inputs_for_plane(test_dcs_bios):
    from dcspy.utils import get_full_bios_for_plane

    json_data = get_full_bios_for_plane(plane='A-10C', bios_dir=test_dcs_bios)
    bios = json_data.get_inputs()
    assert len(bios) == 47
    assert sum(len(values) for values in bios.values()) == 487


# <=><=><=><=><=> SystemData <=><=><=><=><=>
def test_get_sha_of_system_data():
    from dcspy.models import SystemData

    sys_data = SystemData(system='Windows', release='10', ver='10.0.19045', proc='Intel64 Family 6 Model 158 Stepping 9, GenuineIntel', dcs_type='openbeta',
                          dcs_ver='2.9.0.47168', dcspy_ver='v2.9.9', bios_ver='0.7.50', dcs_bios_ver='07771667 from: 26-Oct-2023 06:59:50', git_ver='2.41.0')
    assert sys_data.sha == '07771667'


# <=><=><=><=><=> GuiPlaneInputRequest <=><=><=><=><=>
@mark.parametrize('get_ctrl_for_plane, rb_iface, custom_value, req', [
    (('A-10C', 'AAP_PAGE'), 'rb_fixed_step_inc', '', 'AAP_PAGE INC'),
    (('A-10C', 'AAP_PAGE'), 'rb_fixed_step_dec', '', 'AAP_PAGE DEC'),
    (('A-10C', 'AAP_PAGE'), 'rb_cycle', '', 'AAP_PAGE CYCLE 1 3'),
    (('A-10C', 'AAP_CDUPWR'), 'rb_action', '', 'AAP_CDUPWR TOGGLE'),
    (('A-10C', 'ARC210_CHN_KNB'), 'rb_variable_step_plus', '', 'ARC210_CHN_KNB +3200'),
    (('A-10C', 'ARC210_CHN_KNB'), 'rb_variable_step_minus', '', 'ARC210_CHN_KNB -3200'),
    (('A-10C', 'ADI_PITCH_TRIM'), 'rb_cycle', '', 'ADI_PITCH_TRIM CYCLE 3200 65535'),
    (('A-10C', 'AAP_CDUPWR'), 'rb_custom', 'AAP_CDUPWR 1|AAP_CDUPWR 0', 'AAP_CDUPWR CUSTOM AAP_CDUPWR 1|AAP_CDUPWR 0'),
    (('A-10C', 'AAP_CDUPWR'), 'rb_push_button', '', 'AAP_CDUPWR PUSH_BUTTON'),
], ids=[
    'AAP_PAGE INC',
    'AAP_PAGE DEC',
    'AAP_PAGE CYCLE 1 3',
    'AAP_CDUPWR TOGGLE',
    'ARC210_CHN_KNB +',
    'ARC210_CHN_KNB -',
    'ADI_PITCH_TRIM 3200 65535',
    'AAP_CDUPWR CUSTOM 1 0',
    'AAP_CDUPWR PUSH_BUTTON',
], indirect=['get_ctrl_for_plane'])
def test_plane_input_request_from_control_key(get_ctrl_for_plane, rb_iface, custom_value, req):
    from dcspy.models import GuiPlaneInputRequest

    gui_input_req = GuiPlaneInputRequest.from_control_key(ctrl_key=get_ctrl_for_plane.input, rb_iface=rb_iface, custom_value=custom_value)
    assert gui_input_req.identifier == get_ctrl_for_plane.identifier
    assert gui_input_req.request == req


def test_plane_input_request_from_plane_gkeys():
    from dcspy.models import GuiPlaneInputRequest
    plane_gkey = {
        'G1_M1': 'AAP_PAGE INC',
        'G2_M2': 'AAP_PAGE DEC',
        'G3_M3': 'AAP_PAGE CYCLE 1 3',
        'G4_M1': 'AAP_CDUPWR TOGGLE',
        'G5_M2': 'ARC210_CHN_KNB +3200',
        'G6_M3': 'ARC210_CHN_KNB -3200',
        'G7_M1': 'ADI_PITCH_TRIM CYCLE 3200 65535',
        'G8_M1': 'ICP_COM1_BTN CUSTOM ICP_COM1_BTN 1|ICP_COM1_BTN 0|',
        'G8_M2': '',
        'G9_M1': 'ICP_COM2_BTN CUSTOM ICP_COM2_BTN INC|ICP_COM2_BTN DEC|',
        'G9_M2': 'AAP_CDUPWR PUSH_BUTTON',
    }
    gui_input_req = GuiPlaneInputRequest.from_plane_gkeys(plane_gkey)
    assert gui_input_req == {
        'G1_M1': GuiPlaneInputRequest(identifier='AAP_PAGE', request='AAP_PAGE INC', widget_iface='rb_fixed_step_inc'),
        'G2_M2': GuiPlaneInputRequest(identifier='AAP_PAGE', request='AAP_PAGE DEC', widget_iface='rb_fixed_step_dec'),
        'G3_M3': GuiPlaneInputRequest(identifier='AAP_PAGE', request='AAP_PAGE CYCLE 1 3', widget_iface='rb_cycle'),
        'G4_M1': GuiPlaneInputRequest(identifier='AAP_CDUPWR', request='AAP_CDUPWR TOGGLE', widget_iface='rb_action'),
        'G5_M2': GuiPlaneInputRequest(identifier='ARC210_CHN_KNB', request='ARC210_CHN_KNB +3200', widget_iface='rb_variable_step_plus'),
        'G6_M3': GuiPlaneInputRequest(identifier='ARC210_CHN_KNB', request='ARC210_CHN_KNB -3200', widget_iface='rb_variable_step_minus'),
        'G7_M1': GuiPlaneInputRequest(identifier='ADI_PITCH_TRIM', request='ADI_PITCH_TRIM CYCLE 3200 65535', widget_iface='rb_cycle'),
        'G8_M1': GuiPlaneInputRequest(identifier='ICP_COM1_BTN', request='ICP_COM1_BTN CUSTOM ICP_COM1_BTN 1|ICP_COM1_BTN 0|', widget_iface='rb_custom'),
        'G8_M2': GuiPlaneInputRequest(identifier='', request='', widget_iface=''),
        'G9_M1': GuiPlaneInputRequest(identifier='ICP_COM2_BTN', request='ICP_COM2_BTN CUSTOM ICP_COM2_BTN INC|ICP_COM2_BTN DEC|', widget_iface='rb_custom'),
        'G9_M2': GuiPlaneInputRequest(identifier='AAP_CDUPWR', request='AAP_CDUPWR PUSH_BUTTON', widget_iface='rb_push_button'),
    }


def test_plane_input_request_empty():
    from dcspy.models import GuiPlaneInputRequest

    pir = GuiPlaneInputRequest.make_empty()
    assert pir.identifier == ''
    assert pir.request == ''
    assert pir.widget_iface == ''


# <=><=><=><=><=> ZigZagIterator <=><=><=><=><=>
@mark.parametrize('current, max_val, step, result', [
    (2, 4, 1, [3, 4, 3, 2, 1, 0, 1, 2, 3, 4]),
    (0, 4, 1, [1, 2, 3, 4, 3, 2, 1, 0, 1, 2]),
    (4, 4, 1, [3, 2, 1, 0, 1, 2, 3, 4, 3, 2]),
    (1, 15, 3, [4, 7, 10, 13, 15, 12, 9, 6, 3, 0, 3]),
    (1, 15, 4, [5, 9, 13, 15, 11, 7, 3, 0, 4, 8, 12]),
    (0, 15, 6, [6, 12, 15, 9, 3, 0, 6, 12]),
    (15, 15, 4, [11, 7, 3, 0, 4, 8, 12, 15]),
])
def test_zigzag_iterator(current, max_val, step, result):
    from dcspy.models import ZigZagIterator

    zz = ZigZagIterator(current, max_val, step)
    for next_value in result:
        assert next(zz) == next_value


def test_zigzag_iterator_direction():
    from dcspy.models import Direction, ZigZagIterator

    zz = ZigZagIterator(current=5, max_val=10, step=2)
    assert zz.direction == Direction.FORWARD
    assert next(zz) == 7
    assert next(zz) == 9
    zz.direction = Direction.BACKWARD
    assert next(zz) == 7
    assert next(zz) == 5
    assert zz.direction == Direction.BACKWARD


# <=><=><=><=><=> RequestModel <=><=><=><=><=>
@mark.parametrize('str_req, key, key_down, result', [
    ('COM1 CYCLE 1 3', 'G1_M1', KEY_DOWN, [True, False, False, [b'COM1 3\n']]),
    ('COM1 CYCLE 1 3', 'G1_M1', KEY_UP, [True, False, False, []]),
    ('COM1 CYCLE 1 3', 'ONE', KEY_DOWN, [True, False, False, [b'COM1 3\n']]),
    ('COM2 CUSTOM COM2 1|COM2 0|', 'G2_M2', KEY_DOWN, [False, True, False, [b'COM2 1\n', b'COM2 0\n']]),
    ('COM2 CUSTOM COM2 1|COM2 0|', 'G2_M2', KEY_UP, [False, True, False, []]),
    ('COM2 CUSTOM COM2 1|COM2 0|', 'TWO', KEY_DOWN, [False, True, False, [b'COM2 1\n', b'COM2 0\n']]),
    ('RADIO_1 PUSH_BUTTON', 'G3_M3', KEY_DOWN, [False, False, True, [b'RADIO_1 1\n']]),
    ('RADIO_1 PUSH_BUTTON', 'G3_M3', KEY_UP, [False, False, True, [b'RADIO_1 0\n']]),
    ('RADIO_1 PUSH_BUTTON', 'LEFT', KEY_DOWN, [False, False, True, [b'RADIO_1 1\n', b'RADIO_1 0\n']]),
    ('MASTER_ARM 2', 'G1_M2', KEY_DOWN, [False, False, False, [b'MASTER_ARM 2\n']]),
    ('MASTER_ARM 2', 'G1_M2', KEY_UP, [False, False, False, []]),
    ('MASTER_ARM 2', 'RIGHT', KEY_DOWN, [False, False, False, [b'MASTER_ARM 2\n']]),
], ids=[
    'GKey CYCLE down',
    'GKey CYCLE up',
    'Lcd CYCLE',
    'GKey CUSTOM down',
    'GKey CUSTOM up',
    'Lcd CUSTOM',
    'GKey PUSH_BUTTON down',
    'GKey PUSH_BUTTON up',
    'Lcd PUSH_BUTTON',
    'GKey REGULAR down',
    'GKey REGULAR up',
    'Lcd REGULAR',
])
def test_request_model_properties(str_req, key, key_down, result):
    from dcspy.models import RequestModel, get_key_instance

    def get_bios_fn(val: str) -> int:
        return 2

    req = RequestModel.from_request(request=str_req, get_bios_fn=get_bios_fn, key=get_key_instance(key))
    assert req.is_cycle is result[0]
    assert req.is_custom is result[1]
    assert req.is_push_button is result[2]
    assert req.bytes_requests(key_down=key_down) == result[3]
    assert str(req) == f'{req.ctrl_name}: {str_req}'


@mark.parametrize('key, key_down, result', [
    ('ONE', KEY_DOWN, [b'\n']),
    ('G1_M1', KEY_DOWN, [b'\n']),
    ('G1_M1', KEY_UP, []),
])
def test_empty_request_model_(key, key_down, result):
    from dcspy.models import RequestModel, get_key_instance

    empty_req = RequestModel.empty(key=get_key_instance(key))
    assert empty_req.bytes_requests(key_down=key_down) == result
