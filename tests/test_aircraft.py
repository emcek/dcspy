from pytest import mark

width = 160
height = 43


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50'])
def test_check_all_aircraft_inherit_from_correct_base_class(model):
    from dcspy import aircrafts
    aircraft = getattr(aircrafts, model)
    aircraft_model = aircraft(width, height)
    assert isinstance(aircraft_model, aircrafts.Aircraft)
    assert issubclass(aircraft, aircrafts.Aircraft)


@mark.parametrize('button, result', [(0, '\n'),
                                     (5, '\n'),
                                     ('a', '\n'),
                                     (1, 'UFC_COMM1_CHANNEL_SELECT DEC\n'),
                                     (4, 'UFC_COMM2_CHANNEL_SELECT INC\n')])
def test_button_pressed_for_hornet(button, result):
    from dcspy import aircrafts
    aircraft = aircrafts.FA18Chornet(width, height)
    assert aircraft.button_handle_specific_ac(button) == result
