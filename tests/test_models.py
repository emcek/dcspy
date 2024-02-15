from pytest import mark, raises

AAP_PAGE = {
    'category': 'AAP',
    'control_type': 'selector',
    'description': 'PAGE OTHER - POSITION - STEER - WAYPT',
    'identifier': 'AAP_PAGE',
    'inputs': [{
        'description': 'switch to previous or next state',
        'interface': 'fixed_step'
    }, {
        'description': 'set position',
        'interface': 'set_state',
        'max_value': 3
    }],
    'momentary_positions': 'none',
    'outputs': [{
        'address': 4346,
        'address_identifier': 'A_10C_AAP_PAGE',
        'address_only_identifier': 'A_10C_AAP_PAGE_ADDR',
        'description': 'selector position',
        'mask': 12288,
        'max_value': 3,
        'shift_by': 12,
        'suffix': '',
        'type': 'integer'
    }],
    'physical_variant': 'limited_rotary'
}
AAP_CDUPWR = {
    'category': 'AAP',
    'control_type': 'selector',
    'description': 'CDU Power',
    'identifier': 'AAP_CDUPWR',
    'inputs': [{
        'description': 'switch to previous or next state',
        'interface': 'fixed_step'
    }, {
        'description': 'set position',
        'interface': 'set_state',
        'max_value': 1
    }, {
        'argument': 'TOGGLE',
        'description': 'Toggle switch state',
        'interface': 'action'
    }],
    'momentary_positions': 'none',
    'outputs': [{
        'address': 4346,
        'address_identifier': 'A_10C_AAP_CDUPWR',
        'address_only_identifier': 'A_10C_AAP_CDUPWR_ADDR',
        'description': 'selector position',
        'mask': 16384,
        'max_value': 1,
        'shift_by': 14,
        'suffix': '',
        'type': 'integer'
    }],
    'physical_variant': 'toggle_switch'}
TACAN_1 = {
    'category': 'TACAN Panel',
    'control_type': 'discrete_dial',
    'description': 'Right Channel Selector',
    'identifier': 'TACAN_1',
    'inputs': [{
        'description': 'switch to previous or next state',
        'interface': 'fixed_step'
    }, {
        'argument': 'TOGGLE_XY',
        'description': 'Toggle TACAN Channel X/Y',
        'interface': 'action'
    }],
    'momentary_positions': 'none',
    'outputs': [{
        'address': 4440,
        'address_identifier': 'A_10C_TACAN_1',
        'address_only_identifier': 'A_10C_TACAN_1_ADDR',
        'description': 'selector position',
        'mask': 61440,
        'max_value': 10,
        'shift_by': 12,
        'suffix': '',
        'type': 'integer'
    }],
    'physical_variant': 'infinite_rotary'}
UFC_COMM1_CHANNEL_SELECT = {
    'category': 'Up Front Controller (UFC)',
    'control_type': 'fixed_step_dial',
    'description': 'COMM 1 Channel Select Knob',
    'identifier': 'UFC_COMM1_CHANNEL_SELECT',
    'inputs': [{
        'description': 'turn left or right',
        'interface': 'fixed_step'
    }],
    'outputs': []}
PLT_WIPER_OFF = {
    'category': 'Wiper',
    'control_type': 'selector',
    'description': 'PILOT Windscreen Wiper Control Switch, OFF',
    'identifier': 'PLT_WIPER_OFF',
    'inputs': [{
        'description': 'switch to previous or next state',
        'interface': 'fixed_step'
    }, {
        'description': 'set position',
        'interface': 'set_state',
        'max_value': 0
    }],
    'momentary_positions': 'none',
    'outputs': [{
        'address': 26624,
        'address_identifier': 'Mi_24P_PLT_WIPER_OFF',
        'address_only_identifier': 'Mi_24P_PLT_WIPER_OFF_ADDR',
        'description': 'selector position',
        'mask': 0,
        'max_value': 0,
        'shift_by': 16,
        'suffix': '',
        'type': 'integer'
    }],
    'physical_variant': 'limited_rotary'
}
AAP_STEER = {
    'category': 'AAP',
    'control_type': '3Pos_2Command_Switch_OpenClose',
    'description': 'Toggle Steerpoint',
    'identifier': 'AAP_STEER',
    'inputs': [{
        'description': 'set the switch position',
        'interface': 'set_state',
        'max_value': 2
    }],
    'outputs': [{
        'address': 4346,
        'address_identifier': 'A_10C_AAP_STEER',
        'address_only_identifier': 'A_10C_AAP_STEER_ADDR',
        'description': 'switch position -- 0 = Down, 1 = Mid,  2 = Up',
        'mask': 3072,
        'max_value': 2,
        'shift_by': 10,
        'suffix': '',
        'type': 'integer'
    }]
}
CLOCK_ADJUST_PULL = {
    'category': 'Clock',
    'control_type': 'action',
    'description': 'Adjustment Dial Pull',
    'identifier': 'CLOCK_ADJUST_PULL',
    'inputs': [{
        'argument': 'TOGGLE',
        'description': 'toggle switch state',
        'interface': 'action'
    }],
    'momentary_positions': 'none',
    'outputs': [{
        'address': 5308,
        'address_identifier': 'UH_1H_CLOCK_ADJUST_PULL',
        'address_only_identifier': 'UH_1H_CLOCK_ADJUST_PULL_ADDR',
        'description': 'selector position',
        'mask': 32768,
        'max_value': 1,
        'shift_by': 15,
        'suffix': '',
        'type': 'integer'
    }],
    'physical_variant': 'limited_rotary'
}
ADI_PITCH_TRIM = {
    'category': 'ADI',
    'control_type': 'limited_dial',
    'description': 'ADI Pitch Trim',
    'identifier': 'ADI_PITCH_TRIM',
    'inputs': [{
        'description': 'set the position of the dial',
        'interface': 'set_state',
        'max_value': 65535
    }, {
        'description': 'turn the dial left or right',
        'interface': 'variable_step',
        'max_value': 65535,
        'suggested_step': 3200
    }],
    'outputs': [{
        'address': 4446,
        'address_identifier': 'A_10C_ADI_PITCH_TRIM',
        'address_only_identifier': 'A_10C_ADI_PITCH_TRIM_ADDR',
        'description': 'position of the potentiometer',
        'mask': 65535,
        'max_value': 65535,
        'shift_by': 0,
        'suffix': '',
        'type': 'integer'
    }]
}
ARC210_CHN_KNB = {
    'api_variant': 'multiturn',
    'category': 'ARC-210',
    'control_type': 'analog_dial',
    'description': 'ARC-210 Channel Selector Knob',
    'identifier': 'ARC210_CHN_KNB',
    'inputs': [{
        'description': 'turn the dial left or right',
        'interface': 'variable_step',
        'max_value': 65535,
        'suggested_step': 3200
    }],
    'outputs': [{
        'address': 4990,
        'address_identifier': 'A_10C_ARC210_CHN_KNB',
        'address_only_identifier': 'A_10C_ARC210_CHN_KNB_ADDR',
        'description': 'the rotation of the knob in the cockpit (not the value that is controlled by this knob!)',
        'mask': 65535,
        'max_value': 65535,
        'shift_by': 0,
        'suffix': '_KNOB_POS',
        'type': 'integer'
    }]
}
ARC210_ACTIVE_CHANNEL = {
    'category': 'ARC-210 Display',
    'control_type': 'display',
    'description': 'Active Channel',
    'identifier': 'ARC210_ACTIVE_CHANNEL',
    'inputs': [],
    'outputs': [{
        'address': 4918,
        'address_identifier': 'A_10C_ARC210_ACTIVE_CHANNEL_A',
        'description': 'Active Channel',
        'max_length': 2,
        'suffix': '',
        'type': 'string'
    }]
}
CMSP1 = {
    'category': 'CMSP',
    'control_type': 'display',
    'description': 'CMSP Display Line 1',
    'identifier': 'CMSP1',
    'inputs': [],
    'outputs': [{
        'address': 4096,
        'address_identifier': 'A_10C_CMSP1_A',
        'description': 'CMSP Display Line 1',
        'max_length': 19,
        'suffix': '',
        'type': 'string'
    }]
}


# <=><=><=><=><=> Control / ControlKeyData <=><=><=><=><=>

@mark.parametrize('control, results', [
    (UFC_COMM1_CHANNEL_SELECT, [1, True, False, False, False]),
    (PLT_WIPER_OFF, [2, True, True, False, False]),
    (AAP_PAGE, [2, True, True, False, False]),
    (AAP_CDUPWR, [3, True, True, False, True]),
    (TACAN_1, [2, True, False, False, True]),
    (AAP_STEER, [1, False, True, False, False]),
    (CLOCK_ADJUST_PULL, [1, False, False, False, True]),
    (ADI_PITCH_TRIM, [2, False, True, True, False]),
    (ARC210_CHN_KNB, [1, False, False, True, False]),
], ids=[
    'UFC_COMM1_CHANNEL_SELECT',
    'PLT_WIPER_OFF',
    'AAP_PAGE',
    'AAP_CDUPWR',
    'TACAN_1',
    'AAP_STEER',
    'CLOCK_ADJUST_PULL',
    'ADI_PITCH_TRIM',
    'ARC210_CHN_KNB'])
def test_control_input_properties(control, results):
    from dcspy.models import Control

    ctrl = Control.model_validate(control)
    assert ctrl.input.input_len == results[0]
    assert ctrl.input.has_fixed_step is results[1]
    assert ctrl.input.has_set_state is results[2]
    assert ctrl.input.has_variable_step is results[3]
    assert ctrl.input.has_action is results[4]


@mark.parametrize('control, max_value, step', [
    (UFC_COMM1_CHANNEL_SELECT, 1, 1),
    (PLT_WIPER_OFF, 0, 1),
    (AAP_PAGE, 3, 1),
    (AAP_CDUPWR, 1, 1),
    (TACAN_1, 1, 1),
    (AAP_STEER, 2, 1),
    (CLOCK_ADJUST_PULL, 1, 1),
    (ADI_PITCH_TRIM, 65535, 3200),
    (ARC210_CHN_KNB, 65535, 3200),
], ids=['UFC_COMM1_CHANNEL_SELECT', 'PLT_WIPER_OFF', 'AAP_PAGE', 'AAP_CDUPWR', 'TACAN_1', 'AAP_STEER', 'CLOCK_ADJUST_PULL', 'ADI_PITCH_TRIM', 'ARC210_CHN_KNB'])
def test_control_key_data_from_dicts(control, max_value, step):
    from dcspy.models import Control, ControlKeyData

    ctrl = Control.model_validate(control)
    ctrl_key = ControlKeyData.from_dicts(name=ctrl.identifier, description=ctrl.description, list_of_dicts=ctrl.inputs)
    assert ctrl_key.max_value == max_value
    assert ctrl_key.suggested_step == step
    assert len(ctrl_key.list_dict) == len(ctrl.inputs)
    assert f'suggested_step={ctrl_key.suggested_step}' in repr(ctrl_key)
    assert f'KeyControl({ctrl_key.name}' in repr(ctrl_key)
    assert f'max_value={ctrl_key.max_value}' in repr(ctrl_key)


@mark.parametrize('control, result', [
    (AAP_PAGE, 'IntegerBuffer'),
    (ARC210_CHN_KNB, 'IntegerBuffer'),
    (ARC210_ACTIVE_CHANNEL, 'StringBuffer'),
    (CMSP1, 'StringBuffer'),
], ids=['AAP_PAGE', 'ARC210_CHN_KNB', 'ARC210_ACTIVE_CHANNEL', 'CMSP1'])
def test_control_output(control, result):
    from dcspy.models import Control

    ctrl = Control.model_validate(control)
    assert ctrl.output.klass == result


def test_control_no_output():
    from dcspy.models import Control

    ctrl = Control.model_validate(UFC_COMM1_CHANNEL_SELECT)
    with raises(IndexError):
        print(ctrl.output)

    assert ctrl.input.has_fixed_step


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

    assert Gkey.name(0, 1) == 'G1_M2'
    assert Gkey.name(2, 0) == 'G3_M1'


@mark.parametrize('key_name, klass', [
    ('G12_M3', 'Gkey'),
    ('G1_M2', 'Gkey'),
    ('TWO', 'LcdButton'),
    ('MENU', 'LcdButton'),
])
def test_get_key_instance(key_name, klass):
    from dcspy.models import get_key_instance

    assert get_key_instance(key_name).__class__.__name__ == klass


@mark.parametrize('key_name', ['g12_M3', 'G1_m2', 'G1/M2', 'Two', 'ok', '',])
def test_get_key_instance_error(key_name):
    from dcspy.models import get_key_instance

    with raises(AttributeError):
        get_key_instance(key_name)


@mark.parametrize('key, mode, result', [(0, 0, False), (1, 0, False), (0, 2, False), (2, 3, True)])
def test_get_key_bool_test(key, mode, result):
    from dcspy.models import Gkey

    if Gkey(key=key, mode=mode):
        assert result
    else:
        assert not result


def test_get_key_as_dict_key():
    from dcspy.models import Gkey

    g1 = Gkey(key=2, mode=1)
    assert len({g1: g1.name}) == 1

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

@mark.parametrize('control, rb_iface, custom_value, req', [
    (AAP_PAGE, 'rb_fixed_step_inc', '', 'AAP_PAGE INC'),
    (AAP_PAGE, 'rb_fixed_step_dec', '', 'AAP_PAGE DEC'),
    (AAP_PAGE, 'rb_set_state', '', 'AAP_PAGE CYCLE 1 3'),
    (AAP_CDUPWR, 'rb_action', '', 'AAP_CDUPWR TOGGLE'),
    (ARC210_CHN_KNB, 'rb_variable_step_plus', '', 'ARC210_CHN_KNB +3200'),
    (ARC210_CHN_KNB, 'rb_variable_step_minus', '', 'ARC210_CHN_KNB -3200'),
    (ADI_PITCH_TRIM, 'rb_set_state', '', 'ADI_PITCH_TRIM CYCLE 3200 65535'),
    (AAP_CDUPWR, 'rb_custom', 'AAP_CDUPWR 1|AAP_CDUPWR 0', 'AAP_CDUPWR CUSTOM AAP_CDUPWR 1|AAP_CDUPWR 0'),
], ids=[
    'AAP_PAGE INC',
    'AAP_PAGE DEC',
    'AAP_PAGE CYCLE 1 3',
    'AAP_CDUPWR TOGGLE',
    'ARC210_CHN_KNB +',
    'ARC210_CHN_KNB -',
    'ADI_PITCH_TRIM 3200 65535',
    'AAP_CDUPWR CUSTOM 1 0'])
def test_plane_input_request_from_control_key(control, rb_iface, custom_value, req):
    from dcspy.models import Control, GuiPlaneInputRequest

    ctrl = Control.model_validate(control)
    gui_input_req = GuiPlaneInputRequest.from_control_key(ctrl_key=ctrl.input, rb_iface=rb_iface, custom_value=custom_value)
    assert gui_input_req.identifier == ctrl.identifier
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
    }
    gui_input_req = GuiPlaneInputRequest.from_plane_gkeys(plane_gkey)
    assert gui_input_req == {
        'G1_M1': GuiPlaneInputRequest(identifier='AAP_PAGE', request='AAP_PAGE INC', widget_iface='rb_fixed_step_inc'),
        'G2_M2': GuiPlaneInputRequest(identifier='AAP_PAGE', request='AAP_PAGE DEC', widget_iface='rb_fixed_step_dec'),
        'G3_M3': GuiPlaneInputRequest(identifier='AAP_PAGE', request='AAP_PAGE CYCLE 1 3', widget_iface='rb_set_state'),
        'G4_M1': GuiPlaneInputRequest(identifier='AAP_CDUPWR', request='AAP_CDUPWR TOGGLE', widget_iface='rb_action'),
        'G5_M2': GuiPlaneInputRequest(identifier='ARC210_CHN_KNB', request='ARC210_CHN_KNB +3200', widget_iface='rb_variable_step_plus'),
        'G6_M3': GuiPlaneInputRequest(identifier='ARC210_CHN_KNB', request='ARC210_CHN_KNB -3200', widget_iface='rb_variable_step_minus'),
        'G7_M1': GuiPlaneInputRequest(identifier='ADI_PITCH_TRIM', request='ADI_PITCH_TRIM CYCLE 3200 65535', widget_iface='rb_set_state'),
        'G8_M1': GuiPlaneInputRequest(identifier='ICP_COM1_BTN', request='ICP_COM1_BTN CUSTOM ICP_COM1_BTN 1|ICP_COM1_BTN 0|', widget_iface='rb_custom'),
        'G8_M2': GuiPlaneInputRequest(identifier='', request='', widget_iface=''),
        'G9_M1': GuiPlaneInputRequest(identifier='ICP_COM2_BTN', request='ICP_COM2_BTN CUSTOM ICP_COM2_BTN INC|ICP_COM2_BTN DEC|', widget_iface='rb_custom'),
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
