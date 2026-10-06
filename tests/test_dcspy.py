def test_get_config_yaml_item():
    from dcspy import get_config_yaml_item

    assert get_config_yaml_item('f16_ded_font')
    assert get_config_yaml_item('f16_ded_font', False)
    assert get_config_yaml_item('unknown', True)
