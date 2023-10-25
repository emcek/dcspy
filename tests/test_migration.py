from pytest import mark

from dcspy.migration import migrate


@mark.parametrize('cfg, result', [
    ({'api_ver': '2.9.9', 'val': 1, 'font_color_s': 66, 'theme_mode': 'system'},
     {'api_ver': '3.0.0-rc1', 'completer_items': 20, 'current_plane': 'A-10C', 'font_color_m': 66, 'font_color_s': 18, 'font_mono_m': 11, 'font_mono_s': 9, 'val': 1}),
    ({'api_ver': '3.0.0-rc1', 'val': 1, 'font_color_s': 66, 'theme_mode': 'system'},
     {'api_ver': '3.0.0-rc1', 'font_color_s': 66, 'theme_mode': 'system', 'val': 1}),
    ({'val': 1, 'font_color_s': 66, 'theme_mode': 'system'},
     {'api_ver': '3.0.0-rc1', 'completer_items': 20, 'current_plane': 'A-10C', 'font_color_m': 66, 'font_color_s': 18, 'font_mono_m': 11, 'font_mono_s': 9, 'val': 1}),
], ids=['API 2.9.9', 'API 3.0.0-rc1', 'API empty'])
def test_migrate(cfg, result):
    migrate(cfg=cfg)
    assert cfg == result
