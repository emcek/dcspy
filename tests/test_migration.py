from pytest import mark

from dcspy import migration


@mark.parametrize('cfg, result', [
    ({'api_ver': '2.9.9', 'v': 1, 'font_color_s': 6, 'theme_mode': 'system'},
     {'api_ver': '3.6.3', 'completer_items': 20, 'current_plane': 'A-10C', 'font_color_m': 6, 'font_color_s': 18, 'font_mono_m': 11, 'font_mono_s': 9, 'v': 1}),
    ({'api_ver': '3.0.0', 'v': 1, 'font_color_s': 6, 'theme_mode': 'system', 'git_bios_ref': 'master'},
     {'api_ver': '3.6.3', 'font_color_s': 6, 'theme_mode': 'system', 'v': 1, 'git_bios_ref': 'main'}),
    ({'v': 1, 'font_color_s': 6, 'theme_mode': 'system'},
     {'api_ver': '3.6.3', 'completer_items': 20, 'current_plane': 'A-10C', 'font_color_m': 6, 'font_color_s': 18, 'font_mono_m': 11, 'font_mono_s': 9, 'v': 1}),
], ids=['API 2.9.9', 'API 3.0.0', 'API empty'])
def test_migrate(cfg, result):
    migrated_cfg = migration.migrate(cfg=cfg)
    assert all(result[key] == migrated_cfg[key] for key in result), migrated_cfg


def test_generate_config():
    from os import environ

    migrated_cfg = migration.migrate(cfg={})
    assert migrated_cfg == {
        'api_ver': '3.6.3',
        'autostart': False,
        'check_bios': True,
        'check_ver': True,
        'color_mode': 'system',
        'completer_items': 20,
        'current_plane': 'A-10C',
        'dcs': 'C:/Program Files/Eagle Dynamics/DCS World',
        'dcsbios': f'C:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS\\Scripts\\DCS-BIOS',
        'f16_ded_font': True,
        'font_color_l': 32,
        'font_color_m': 22,
        'font_color_s': 18,
        'font_mono_l': 16,
        'font_mono_m': 11,
        'font_mono_s': 9,
        'font_name': 'consola.ttf',
        'git_bios': True,
        'git_bios_ref': 'main',
        'gkeys_area': 2,
        'gkeys_float': False,
        'gui_debug': False,
        'debug_font_size': 10,
        'device': 'G13',
        'save_lcd': False,
        'show_gui': True,
        'toolbar_area': 4,
        'toolbar_style': 0,
        'verbose': False,
    }


def test_replace_line_in_file(migration_file, resources):
    import re

    migration.replace_line_in_file(filename='migration.txt', dir_path=resources, pattern=re.compile('before'), new_text='after')
    with open(resources / 'migration.txt') as f:
        assert 'after' in f.read()
        assert 'before' not in f.read()


def test_replace_line_in_file_file_not_exist(resources):
    import re

    migration.replace_line_in_file(filename='not_a_file.txt', dir_path=resources, pattern=re.compile('before'), new_text='after')
    assert not (resources / 'not_a_file.txt').exists()
