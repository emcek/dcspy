from pprint import pprint

from pytest import mark

from dcspy import SUPPORTED_CRAFTS
from tests.helpers import check_dcsbios_data, generate_bios_data_for_plane


@mark.dcsbios
@mark.parametrize('plane', ['hornet_mono', 'viper_mono', 'shark_mono', 'hip_mono', 'hind_mono', 'warthog_mono', 'tomcatb_mono', 'harrier_mono', 'apache_mono'])
def test_bios_values_all_planes(plane, request):
    plane = request.getfixturevalue(plane)
    name = SUPPORTED_CRAFTS[plane.__class__.__name__]['bios']
    results, dcsbios_ver = check_dcsbios_data(plane_bios=plane.bios_data, plane_json=f'{name}.json', git_bios=True)
    print(f'\n{name} BIOS {dcsbios_ver}\n{"-" * (len(name) + 13)}')
    pprint(results if results else 'No issues found', width=100)
    if results:
        print('----- Full BIOS entry -----')
        pprint(generate_bios_data_for_plane(plane_bios=plane.bios_data, plane_json=f'{name}.json', git_bios=True), width=160)
    assert not results
