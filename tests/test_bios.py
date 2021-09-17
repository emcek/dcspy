from pprint import pprint

from dcspy import SUPPORTED_CRAFTS
from helpers import check_dcsbios_data


def test_bios_values_for_shark(black_shark_mono):
    name = SUPPORTED_CRAFTS[black_shark_mono.__class__.__name__]
    results = check_dcsbios_data(black_shark_mono.bios_data, f'{name}.json')
    print(f'\n{name} BIOS Report\n{"-" * (len(name) + 12)}')
    pprint(results)
    assert not results


def test_bios_values_for_viper(viper_mono):
    name = SUPPORTED_CRAFTS[viper_mono.__class__.__name__]
    results = check_dcsbios_data(viper_mono.bios_data, f'{name}.json')
    print(f'\n{name} BIOS Report\n{"-" * (len(name) + 12)}')
    pprint(results)
    assert not results


def test_bios_values_for_hornet(hornet_mono):
    name = SUPPORTED_CRAFTS[hornet_mono.__class__.__name__]
    results = check_dcsbios_data(hornet_mono.bios_data, f'{name}.json')
    print(f'\n{name} BIOS Report\n{"-" * (len(name) + 12)}')
    pprint(results)
    assert not results


def test_bios_values_for_tomcat(tomcat_mono):
    name = SUPPORTED_CRAFTS[tomcat_mono.__class__.__name__]
    results = check_dcsbios_data(tomcat_mono.bios_data, f'{name}.json')
    print(f'\n{name} BIOS Report\n{"-" * (len(name) + 12)}')
    pprint(results)
    assert not results
