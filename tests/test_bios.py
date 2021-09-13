from requests import get
from json import loads
from pprint import pprint

check_convert = {'length': 'max_length',
                  'address': 'address',
                  'mask': 'mask',
                  'shift_by': 'shift_by'}

response = get('https://api.github.com/repos/DCSFlightpanels/dcs-bios/releases/latest')
if response.status_code == 200:
    dcsbios_ver = response.json()['tag_name']
else:
    dcsbios_ver = '0.7.41'


def test_bios_values_for_shark(black_shark_mono):
    local_json = _get_json_for_plane('Ka-50.json')
    results = _check_dcsbios_data(black_shark_mono, local_json)
    print('\nShark BIOS Report\n-----------------')
    pprint(results)
    # assert not results


def test_bios_values_for_viper(viper_mono):
    local_json = _get_json_for_plane('F-16C_50.json')
    results = _check_dcsbios_data(viper_mono, local_json)
    print('\nViper BIOS Report\n-----------------')
    pprint(results)
    # assert not results


def test_bios_values_for_hornet(hornet_mono):
    local_json = _get_json_for_plane('FA-18C_hornet.json')
    results = _check_dcsbios_data(hornet_mono, local_json)
    print('\nHornet BIOS Report\n------------------')
    pprint(results)
    # assert not results


def test_bios_values_for_tomcat(tomcat_mono):
    local_json = _get_json_for_plane('F-14B.json')
    results = _check_dcsbios_data(tomcat_mono, local_json)
    print('\nTomcat BIOS Report\n------------------')
    pprint(results)
    # assert not results


def _get_json_for_plane(plane: str) -> dict:
    data = get(f'https://raw.githubusercontent.com/DCSFlightpanels/dcs-bios/{dcsbios_ver}/Scripts/DCS-BIOS/doc/json/{plane}')
    return loads(data.content)


def _check_dcsbios_data(plane_bios, local_json) -> dict:
    results = {}
    for bios_key in plane_bios.bios_data:
        bios_ref = _recursive_lookup(bios_key, local_json)
        if not bios_ref:
            results[bios_key] = f'Not found in DCS-BIOS {dcsbios_ver}'
            continue
        bios_outputs = bios_ref['outputs'][0]
        for args_key in plane_bios.bios_data[bios_key]['args']:
            aircraft_value = plane_bios.bios_data[bios_key]['args'][args_key]
            dcsbios_value = bios_outputs[check_convert[args_key]]
            if not aircraft_value == dcsbios_value:
                bios_issue = {args_key: f"dcspy: {aircraft_value} ({hex(aircraft_value)}) "
                                        f"bios: {dcsbios_value} ({hex(dcsbios_value)})"}
                if results.get(bios_key):
                    results[bios_key].update(bios_issue)
                else:
                    results[bios_key] = bios_issue
    return results


def _recursive_lookup(k: str, d: dict):
    if k in d:
        return d[k]
    for v in d.values():
        if isinstance(v, dict):
            item = _recursive_lookup(k, v)
            if item:
                return item
