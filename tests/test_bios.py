from pprint import pprint

from pytest import mark

from dcspy import SUPPORTED_CRAFTS
from tests.helpers import check_dcsbios_data, generate_bios_data_for_plane


@mark.dcsbios
@mark.parametrize('plane', [
    'a10c_mono', 'ah64dblkii_mono', 'av8bna_mono', 'f14a135gr_mono', 'f14b_mono', 'f16c50_mono', 'fa18chornet_mono', 'ka50_mono', 'mi24p_mono', 'mi8mt_mono'
])
def test_bios_values_all_planes(plane, request):
    plane = request.getfixturevalue(plane)
    name = SUPPORTED_CRAFTS[type(plane).__name__]['bios']
    results, dcsbios_ver = check_dcsbios_data(plane_bios=plane.bios_data, plane_name=f'{name}', git_bios=True)
    print(f'\n{name} BIOS {dcsbios_ver}\n{"-" * (len(name) + 13)}')
    pprint(results if results else 'No issues found', width=100)
    if results:
        print('----- Full BIOS entry -----')
        pprint(generate_bios_data_for_plane(plane_bios=plane.bios_data, plane_name=f'{name}', git_bios=True), width=160)
    assert not results
