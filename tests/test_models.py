from pytest import mark


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
    "category": "ADI",
    "control_type": "limited_dial",
    "description": "ADI Pitch Trim",
    "identifier": "ADI_PITCH_TRIM",
    "inputs": [{
        "description": "set the position of the dial",
        "interface": "set_state",
        "max_value": 65535
    }, {
        "description": "turn the dial left or right",
        "interface": "variable_step",
        "max_value": 65535,
        "suggested_step": 3200
    }],
    "outputs": [{
        "address": 4446,
        "address_identifier": "A_10C_ADI_PITCH_TRIM",
        "address_only_identifier": "A_10C_ADI_PITCH_TRIM_ADDR",
        "description": "position of the potentiometer",
        "mask": 65535,
        "max_value": 65535,
        "shift_by": 0,
        "suffix": "",
        "type": "integer"
    }]
}
ARC210_CHN_KNB = {
    "api_variant": "multiturn",
    "category": "ARC-210",
    "control_type": "analog_dial",
    "description": "ARC-210 Channel Selector Knob",
    "identifier": "ARC210_CHN_KNB",
    "inputs": [{
        "description": "turn the dial left or right",
        "interface": "variable_step",
        "max_value": 65535,
        "suggested_step": 3200
    }],
    "outputs": [{
        "address": 4990,
        "address_identifier": "A_10C_ARC210_CHN_KNB",
        "address_only_identifier": "A_10C_ARC210_CHN_KNB_ADDR",
        "description": "the rotation of the knob in the cockpit (not the value that is controlled by this knob!)",
        "mask": 65535,
        "max_value": 65535,
        "shift_by": 0,
        "suffix": "_KNOB_POS",
        "type": "integer"
    }]
}


@mark.parametrize('control, results', [
    (UFC_COMM1_CHANNEL_SELECT, [True, 1, True, False, False, False, 'UFC_COMM1_CHANNEL_SELECT INC\n']),
    (PLT_WIPER_OFF, [False, 2, True, True, False, False, 'PLT_WIPER_OFF 0\n']),
], ids=['UFC_COMM1_CHANNEL_SELECT', 'PLT_WIPER_OFF'])
def test_get_input_request_for_regular_button(control, results):
    from dcspy.models import Control

    ctrl = Control.model_validate(control)
    assert ctrl.input.one_input is results[0]
    assert ctrl.input.input_len == results[1]
    assert ctrl.input.has_fixed_step is results[2]
    assert ctrl.input.has_set_state is results[3]
    assert ctrl.input.has_variable_step is results[4]
    assert ctrl.input.has_action is results[5]
    assert ctrl.input.request() == results[6]


@mark.parametrize('control, results', [
    (AAP_PAGE, [False, 2, True, True, False, False, {'bios': 'AAP_PAGE'}, (3, 1)]),
    (AAP_CDUPWR, [False, 3, True, True, False, True, {'bios': 'AAP_CDUPWR'}, (1, 1)]),
    (TACAN_1, [False, 2, True, False, False, True, {'bios': 'TACAN_1'}, (1, 1)]),
    (AAP_STEER, [True, 1, False, True, False, False, {'bios': 'AAP_STEER'}, (2, 1)]),
    (CLOCK_ADJUST_PULL, [True, 1, False, False, False, True, {'bios': 'CLOCK_ADJUST_PULL'}, (1, 1)]),
    (ADI_PITCH_TRIM, [False, 2, False, True, True, False, {'bios': 'ADI_PITCH_TRIM'}, (65535, 3200)]),
    (ARC210_CHN_KNB, [True, 1, False, False, True, False, {'bios': 'ARC210_CHN_KNB'}, (65535, 3200)]),
], ids=['AAP_PAGE', 'AAP_CDUPWR', 'TACAN_1', 'AAP_STEER', 'CLOCK_ADJUST_PULL', 'ADI_PITCH_TRIM', 'ARC210_CHN_KNB'])
def test_get_input_request_for_cycle_button(control, results):
    from collections.abc import Iterable
    from dcspy.models import Control

    ctrl = Control.model_validate(control)
    assert ctrl.input.one_input is results[0]
    assert ctrl.input.input_len == results[1]
    assert ctrl.input.has_fixed_step is results[2]
    assert ctrl.input.has_set_state is results[3]
    assert ctrl.input.has_variable_step is results[4]
    assert ctrl.input.has_action is results[5]
    assert ctrl.input.request()['bios'] == results[6]['bios']
    assert isinstance(ctrl.input.request()['iter'], Iterable)
    assert ctrl.input.cycle_data() == results[7]
