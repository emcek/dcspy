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
    data = get(f'https://raw.githubusercontent.com/DCSFlightpanels/dcs-bios/{dcsbios_ver}/Scripts/DCS-BIOS/doc/json/Ka-50.json')
    local_json = loads(data.content)
    results = _check_dcsbios_data(black_shark_mono, local_json)
    print('\nShark BIOS Report\n-----------------')
    pprint(results)
    # assert not results


def test_bios_values_for_viper(viper_mono):
    data = get(f'https://raw.githubusercontent.com/DCSFlightpanels/dcs-bios/{dcsbios_ver}/Scripts/DCS-BIOS/doc/json/F-16C_50.json')
    local_json = loads(data.content)
    results = _check_dcsbios_data(viper_mono, local_json)
    print('\nViper BIOS Report\n-----------------')
    pprint(results)
    # assert not results


def test_bios_values_for_hornet(hornet_mono):
    data = get(f'https://raw.githubusercontent.com/DCSFlightpanels/dcs-bios/{dcsbios_ver}/Scripts/DCS-BIOS/doc/json/FA-18C_hornet.json')
    local_json = loads(data.content)
    results = _check_dcsbios_data(hornet_mono, local_json)
    print('\nHornet BIOS Report\n------------------')
    pprint(results)
    # assert not results


def test_bios_values_for_tomcat(tomcat_mono):
    data = get(f'https://raw.githubusercontent.com/DCSFlightpanels/dcs-bios/{dcsbios_ver}/Scripts/DCS-BIOS/doc/json/F-14B.json')
    local_json = loads(data.content)
    results = _check_dcsbios_data(tomcat_mono, local_json)
    print('\nTomcat BIOS Report\n------------------')
    pprint(results)
    # assert not results


def _check_dcsbios_data(black_shark_mono, local_json):
    results = {}
    for bios_key in black_shark_mono.bios_data:
        bios_ref = _recursive_lookup(bios_key, local_json)
        if not bios_ref:
            results[bios_key] = f'Not found in DCS-BIOS {dcsbios_ver}'
            continue
        bios_outputs = bios_ref['outputs'][0]
        for args_key in black_shark_mono.bios_data[bios_key]['args']:
            aircraft_value = black_shark_mono.bios_data[bios_key]['args'][args_key]
            dcsbios_value = bios_outputs[check_convert[args_key]]
            if not aircraft_value == dcsbios_value:
                if results.get(bios_key):
                    results[bios_key].update({
                                                 args_key: f"dcspy: {aircraft_value} ({hex(aircraft_value)}) bios: {dcsbios_value} ({hex(dcsbios_value)})"})
                else:
                    results[bios_key] = {
                        args_key: f"dcspy: {aircraft_value} ({hex(aircraft_value)}) bios: {dcsbios_value} ({hex(dcsbios_value)})"}
    return results


def _recursive_lookup(k: str, d: dict):
    if k in d:
        return d[k]
    for v in d.values():
        if isinstance(v, dict):
            item = _recursive_lookup(k, v)
            if item:
                return item
