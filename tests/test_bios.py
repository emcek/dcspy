from pprint import pprint

from utils import check_dcsbios_data


def test_bios_values_for_shark(black_shark_mono):
    name = 'Ka-50'
    results = check_dcsbios_data(black_shark_mono.bios_data, f'{name}.json')
    print(f'\n{name} BIOS Report\n{"-" * (len(name) + 12)}')
    pprint(results)
    # assert not results


def test_bios_values_for_viper(viper_mono):
    name = 'F-16C_50'
    results = check_dcsbios_data(viper_mono.bios_data, f'{name}.json')
    print(f'\n{name} BIOS Report\n{"-" * (len(name) + 12)}')
    pprint(results)
    # assert not results


def test_bios_values_for_hornet(hornet_mono):
    name = 'FA-18C_hornet'
    results = check_dcsbios_data(hornet_mono.bios_data, f'{name}.json')
    print(f'\n{name} BIOS Report\n{"-" * (len(name) + 12)}')
    pprint(results)
    # assert not results


def test_bios_values_for_tomcat(tomcat_mono):
    name = 'F-14B'
    results = check_dcsbios_data(tomcat_mono.bios_data, f'{name}.json')
    print(f'\n{name} BIOS Report\n{"-" * (len(name) + 12)}')
    pprint(results)
    # assert not results
