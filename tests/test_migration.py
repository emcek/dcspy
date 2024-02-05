from pytest import mark

from dcspy.migration import migrate


@mark.parametrize('cfg, result', [
    ({'api_ver': '2.9.9', 'val': 1, 'font_color_s': 66, 'theme_mode': 'system'},
     {'api_ver': '3.1.4', 'completer_items': 20, 'current_plane': 'A-10C', 'font_color_m': 66, 'font_color_s': 18, 'font_mono_m': 11, 'font_mono_s': 9, 'val': 1}),
    ({'api_ver': '3.0.0', 'val': 1, 'font_color_s': 66, 'theme_mode': 'system'},
     {'api_ver': '3.1.4', 'font_color_s': 66, 'theme_mode': 'system', 'val': 1}),
    ({'val': 1, 'font_color_s': 66, 'theme_mode': 'system'},
     {'api_ver': '3.1.4', 'completer_items': 20, 'current_plane': 'A-10C', 'font_color_m': 66, 'font_color_s': 18, 'font_mono_m': 11, 'font_mono_s': 9, 'val': 1}),
], ids=['API 2.9.9', 'API 3.0.0', 'API empty'])
def test_migrate(cfg, result):
    migrated_cfg = migrate(cfg=cfg)
    assert all(result[key] == migrated_cfg[key] for key in result)


def test_generate_config():
    from os import environ

    migrated_cfg = migrate(cfg={})
    assert migrated_cfg == {
        'api_ver': '3.1.4',
        'autostart': False,
        'check_bios': True,
        'check_ver': True,
        'completer_items': 20,
        'current_plane': 'A-10C',
        'dcs': 'C:/Program Files/Eagle Dynamics/DCS World OpenBeta',
        'dcsbios': f'C:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
        'f16_ded_font': True,
        'font_color_l': 32,
        'font_color_m': 22,
        'font_color_s': 18,
        'font_mono_l': 16,
        'font_mono_m': 11,
        'font_mono_s': 9,
        'font_name': 'consola.ttf',
        'git_bios': True,
        'git_bios_ref': 'master',
        'gkeys_area': 2,
        'gkeys_float': False,
        'keyboard': 'G13',
        'save_lcd': False,
        'show_gui': True,
        'toolbar_area': 4,
        'toolbar_style': 0,
        'verbose': False,
    }
