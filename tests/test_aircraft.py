from pytest import mark


@mark.parametrize('model', ['FA18Chornet', 'F16C50', 'Ka50'])
def test_check_all_aircraft_inherit_from_correct_base_class(model):
    from dcspy import aircrafts
    aircraft = getattr(aircrafts, model)
    aircraft_model = aircraft(160, 43)
    assert isinstance(aircraft_model, aircrafts.Aircraft)
    assert issubclass(aircraft, aircrafts.Aircraft)
