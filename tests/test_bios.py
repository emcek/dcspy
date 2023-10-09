from pprint import pprint

from pytest import mark

from dcspy.models import SUPPORTED_CRAFTS
from tests.helpers import check_dcsbios_data, generate_bios_data_for_plane


@mark.dcsbios
@mark.parametrize('plane', ['fa18chornet', 'f16c50', 'f15ese', 'ka50', 'mi8mt', 'mi24p', 'ah64dblkii', 'a10c', 'f14b', 'av8bna'])
def test_bios_values_all_planes(plane, request):
    plane = request.getfixturevalue(f'{plane}_mono')
    name = SUPPORTED_CRAFTS[type(plane).__name__]['bios']
    results, dcsbios_ver = check_dcsbios_data(plane_bios=plane.bios_data, plane_name=f'{name}', git_bios=True)
    print(f'\n{name} BIOS {dcsbios_ver}\n{"-" * (len(name) + 13)}')
    pprint(results if results else 'No issues found', width=100)
    if results:
        print('----- Full BIOS entry -----')
        pprint(generate_bios_data_for_plane(plane_bios=plane.bios_data, plane_name=f'{name}', git_bios=True), width=160)
    assert not results
