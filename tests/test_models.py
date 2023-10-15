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
    assert ctrl.input.cycle_data == results[7]


def get_next_value_for_button(button, curr_val, control):
    # todo: move to Aircraft
    from itertools import chain, cycle

    from dcspy.models import Control

    ctrl = Control.model_validate(control)
    cycle_buttons = {button: ctrl.input.request()}
    bios = ctrl.input.name
    max_val = ctrl.input.max_value
    step = ctrl.input.suggested_step
    range_inc = list(range(0, max_val + step, step))
    range_dec = list(range(max_val - step, 0, -step))
    if range_inc[-1] != max_val:
        del range_inc[-1]
        range_inc.append(max_val)
    full_seed = range_inc + range_dec + range_inc
    if curr_val not in range_inc:
        curr_val = min(range_inc, key=lambda x: abs(curr_val - x))
    seed = full_seed[curr_val // step + 1:2 * (len(range_inc) - 1) + curr_val // step + 1]
    print(f'{bios} full_seed: {full_seed} seed: {seed} curr_val: {curr_val}')
    cycle_buttons[button]['iter'] = cycle(chain(seed))
    return next(cycle_buttons[button]['iter']), full_seed, seed, cycle_buttons


@mark.parametrize('control, curr_val, results', [
    (AAP_PAGE, 0, [1, [0, 1, 2, 3, 2, 1, 0, 1, 2, 3], [1, 2, 3, 2, 1, 0], 'AAP_PAGE']),
    (AAP_PAGE, 2, [3, [0, 1, 2, 3, 2, 1, 0, 1, 2, 3], [3, 2, 1, 0, 1, 2], 'AAP_PAGE']),
    (ARC210_CHN_KNB, 0, [
        3200, [
            0, 3200, 6400, 9600, 12800, 16000, 19200, 22400, 25600, 28800, 32000, 35200, 38400, 41600, 44800, 48000, 51200, 54400, 57600, 60800, 64000, 65535,
            62335, 59135, 55935, 52735, 49535, 46335, 43135, 39935, 36735, 33535, 30335, 27135, 23935, 20735, 17535, 14335, 11135, 7935, 4735, 1535, 0, 3200,
            6400, 9600, 12800, 16000, 19200, 22400, 25600, 28800, 32000, 35200, 38400, 41600, 44800, 48000, 51200, 54400, 57600, 60800, 64000, 65535
        ], [
            3200, 6400, 9600, 12800, 16000, 19200, 22400, 25600, 28800, 32000, 35200, 38400, 41600, 44800, 48000, 51200, 54400, 57600, 60800, 64000, 65535,
            62335, 59135, 55935, 52735, 49535, 46335, 43135, 39935, 36735, 33535, 30335, 27135, 23935, 20735, 17535, 14335, 11135, 7935, 4735, 1535, 0],
        'ARC210_CHN_KNB']),
    (ARC210_CHN_KNB, 9500, [
        12800, [
            0, 3200, 6400, 9600, 12800, 16000, 19200, 22400, 25600, 28800, 32000, 35200, 38400, 41600, 44800, 48000, 51200, 54400, 57600, 60800, 64000, 65535,
            62335, 59135, 55935, 52735, 49535, 46335, 43135, 39935, 36735, 33535, 30335, 27135, 23935, 20735, 17535, 14335, 11135, 7935, 4735, 1535, 0, 3200,
            6400, 9600, 12800, 16000, 19200, 22400, 25600, 28800, 32000, 35200, 38400, 41600, 44800, 48000, 51200, 54400, 57600, 60800, 64000, 65535
        ], [
            12800, 16000, 19200, 22400, 25600, 28800, 32000, 35200, 38400, 41600, 44800, 48000, 51200, 54400, 57600, 60800, 64000, 65535, 62335, 59135, 55935,
            52735, 49535, 46335, 43135, 39935, 36735, 33535, 30335, 27135, 23935, 20735, 17535, 14335, 11135, 7935, 4735, 1535, 0, 3200, 6400, 9600],
        'ARC210_CHN_KNB']),
], ids=['AAP_PAGE 0', 'AAP_PAGE 2', 'ARC210_CHN_KNB 0', 'ARC210_CHN_KNB 3'])
def test_get_next_value_for_button(control, curr_val, results):
    from collections.abc import Iterable

    n, full, seed, cycle_btn = get_next_value_for_button('Button1', curr_val, control)
    assert n == results[0]
    assert full == results[1]
    assert seed == results[2]
    assert cycle_btn['Button1']['bios'] == results[3]
    assert isinstance(cycle_btn['Button1']['iter'], Iterable)


def test_gkey_from_yaml_success():
    from dcspy.models import Gkey

    gkey = Gkey.from_yaml('G22_M3')
    assert gkey.key == 22
    assert gkey.mode == 3


def test_gkey_from_yaml_value_error():
    from dcspy.models import Gkey

    with raises(ValueError):
        _ = Gkey.from_yaml('G_M1')


def test_cycle_button_default_iter():
    from dcspy.models import CycleButton

    cb = CycleButton(ctrl_name='AAP_PAGE')
    with raises(StopIteration):
        next(cb.iter)
        next(cb.iter)


def test_cycle_button_custom_iter():
    from dcspy.models import CycleButton

    cb = CycleButton(ctrl_name='AAP_PAGE', iter=iter([1, 2]))
    with raises(StopIteration):
        assert next(cb.iter) == 1
        assert next(cb.iter) == 2
        next(cb.iter)
