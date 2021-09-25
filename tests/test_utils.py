def test_dummy_save_load_set_defaults():
    from dcspy import utils
    from os import makedirs, remove, rmdir, environ
    makedirs(name='./tmp', exist_ok=True)
    test_tmp_yaml = './tmp/c.yaml'

    utils.save_cfg({'1': 1}, test_tmp_yaml)
    d_cfg = utils.load_cfg(test_tmp_yaml)
    assert d_cfg == {'1': 1}
    d_cfg = utils.set_defaults(d_cfg)
    assert d_cfg == {'keyboard': 'G13', 'dcsbios': f'D:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
                     'fontname': 'consola.ttf', 'fontsize': [11, 16, 22, 32]}
    with open(test_tmp_yaml, 'w+') as f:
        f.write('')
    d_cfg = utils.load_cfg(test_tmp_yaml)
    assert len(d_cfg) == 0

    remove(test_tmp_yaml)
    rmdir('./tmp/')
