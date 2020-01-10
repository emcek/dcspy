from pytest import mark, raises

width = 160
height = 43


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50'])
def test_check_all_aircraft_inherit_from_correct_base_class(model):
    from dcspy import aircrafts
    aircraft = getattr(aircrafts, model)
    aircraft_model = aircraft(width, height)
    assert isinstance(aircraft_model, aircrafts.Aircraft)
    assert issubclass(aircraft, aircrafts.Aircraft)


def test_aircraft_base_class():
    from dcspy.aircrafts import Aircraft
    aircraft = Aircraft(width, height)
    aircraft.bios_data = {'abstract_field': {'addr': 0xdeadbeef, 'len': 16, 'val': ''}}

    assert aircraft.button_handle_specific_ac(1) == '\n'

    with raises(NotImplementedError):
        aircraft.prepare_image()

    with raises(NotImplementedError):
        aircraft.set_bios('abstract_field', 'deadbeef', True)

    assert aircraft.get_bios('abstract_field') == 'deadbeef'
    assert aircraft.get_bios('none') == ''


@mark.parametrize('button, result', [(0, '\n'),
                                     (5, '\n'),
                                     ('a', '\n'),
                                     (1, 'UFC_COMM1_CHANNEL_SELECT DEC\n'),
                                     (4, 'UFC_COMM2_CHANNEL_SELECT INC\n')])
def test_button_pressed_for_hornet(button, result):
    from dcspy.aircrafts import FA18Chornet
    aircraft = FA18Chornet(width, height)
    assert aircraft.button_handle_specific_ac(button) == result


@mark.parametrize('selector, value, result', [('ScratchpadStr2', '~~', '22'),
                                              ('COMM1', '``', '11'),
                                              ('FuelTotal', '104T', '104T')])
def test_set_bios_for_hornet(selector, value, result):
    from dcspy.aircrafts import FA18Chornet
    aircraft = FA18Chornet(width, height)
    aircraft.set_bios(selector, value, False)
    assert aircraft.bios_data[selector]['val'] == result


def test_prepare_image_for_hornet():
    from dcspy.aircrafts import FA18Chornet
    from PIL.Image import Image
    aircraft = FA18Chornet(width, height)
    img = aircraft.prepare_image()
    assert img.size == (width, height)
    assert isinstance(img, Image)
