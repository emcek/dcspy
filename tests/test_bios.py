from pprint import pprint

from pytest import mark

from dcspy import SUPPORTED_CRAFTS
from tests.helpers import check_dcsbios_data, generate_bios_data_for_plane, all_plane_list


@mark.dcsbios
@mark.parametrize('lcd', ['mono', 'color'])
@mark.parametrize('plane', all_plane_list)
def test_bios_values_all_planes(plane, lcd, request):
    plane = request.getfixturevalue(f'{plane}_{lcd}')
    name = SUPPORTED_CRAFTS[type(plane).__name__]['bios']
    results, dcsbios_ver = check_dcsbios_data(plane_bios=plane.bios_data, plane_name=f'{name}', git_bios=True)
    print(f'\n{name} {lcd} BIOS {dcsbios_ver}\n{"-" * (len(name) + len(lcd) + 14)}')
    pprint(results if results else 'No issues found', width=100)
    if results:
        print('----- Full BIOS entry -----')
        pprint(generate_bios_data_for_plane(plane_bios=plane.bios_data, plane_name=f'{name}', git_bios=True), width=160)
    assert not results
