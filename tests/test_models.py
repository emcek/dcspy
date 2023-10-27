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
], ids=['UFC_COMM1_CHANNEL_SELECT', 'PLT_WIPER_OFF', 'AAP_PAGE', 'AAP_CDUPWR', 'TACAN_1', 'AAP_STEER', 'CLOCK_ADJUST_PULL', 'ADI_PITCH_TRIM', 'ARC210_CHN_KNB'])
def test_control_input_properties(control, results):
    from dcspy.models import Control

    ctrl = Control.model_validate(control)
    assert ctrl.input.input_len == results[0]
    assert ctrl.input.has_fixed_step is results[1]
    assert ctrl.input.has_set_state is results[2]
    assert ctrl.input.has_variable_step is results[3]
    assert ctrl.input.has_action is results[4]


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
        next(cb.iter)
        next(cb.iter)
        next(cb.iter)


# <=><=><=><=><=> DcsBiosPlaneData <=><=><=><=><=>

def test_get_ctrl(resources):
    from dcspy.utils import get_full_bios_for_plane

    json_data = get_full_bios_for_plane(plane='A-10C', bios_dir=resources / 'dcs_bios')
    c = json_data.get_ctrl(ctrl_name='TACAN_MODE')
    assert c.output.max_value == 4
    assert c.input.one_input is False


def test_get_inputs_for_plane(resources):
    from dcspy.utils import get_full_bios_for_plane

    json_data = get_full_bios_for_plane(plane='A-10C', bios_dir=resources / 'dcs_bios')
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

@mark.parametrize('control, rb_iface, req', [
    (AAP_PAGE, 'rb_fixed_step_inc', 'AAP_PAGE INC'),
    (AAP_PAGE, 'rb_fixed_step_dec', 'AAP_PAGE DEC'),
    (AAP_PAGE, 'rb_set_state', 'AAP_PAGE CYCLE 1 3'),
    (AAP_CDUPWR, 'rb_action', 'AAP_CDUPWR TOGGLE'),
    (ARC210_CHN_KNB, 'rb_variable_step_plus', 'ARC210_CHN_KNB +3200'),
    (ARC210_CHN_KNB, 'rb_variable_step_minus', 'ARC210_CHN_KNB -3200'),
    (ADI_PITCH_TRIM, 'rb_set_state', 'ADI_PITCH_TRIM CYCLE 3200 65535'),
], ids=['AAP_PAGE INC', 'AAP_PAGE DEC', 'AAP_PAGE CYCLE 1 3', 'AAP_CDUPWR TOGGLE', 'ARC210_CHN_KNB +', 'ARC210_CHN_KNB -', 'ADI_PITCH_TRIM 3200 65535'])
def test_plane_input_request_from_control_key(control, rb_iface, req):
    from dcspy.models import Control, GuiPlaneInputRequest

    ctrl = Control.model_validate(control)
    gui_input_req = GuiPlaneInputRequest.from_control_key(ctrl_key=ctrl.input, rb_iface=rb_iface)
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
        'G8_M2': '',
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
        'G8_M2': GuiPlaneInputRequest(identifier='', request='', widget_iface=''),
    }
