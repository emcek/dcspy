from pprint import pprint

from pytest import mark

from dcspy import SUPPORTED_CRAFTS
from helpers import check_dcsbios_data


@mark.parametrize('plane', ['hornet_mono', 'viper_mono', 'black_shark_mono', 'warthog_mono', 'tomcat_mono', 'harrier_mono'])
def test_bios_values_all_planes(plane, request):
    plane = request.getfixturevalue(plane)
    name = SUPPORTED_CRAFTS[plane.__class__.__name__]
    results = check_dcsbios_data(plane.bios_data, f'{name}.json')
    print(f'\n{name} BIOS Report\n{"-" * (len(name) + 12)}')
    pprint(results if results else 'No issues found', width=100)
    assert not results
