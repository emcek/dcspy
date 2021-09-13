from json import loads

from requests import get

response = get('https://api.github.com/repos/DCSFlightpanels/dcs-bios/releases/latest')
if response.status_code == 200:
    dcsbios_ver = response.json()['tag_name']
else:
    dcsbios_ver = '0.7.41'


def check_dcsbios_data(plane_bios: dict, plane_json: str) -> dict:
    results = {}
    local_json = _get_json_for_plane(plane_json)
    for bios_key in plane_bios:
        bios_ref = _recursive_lookup(bios_key, local_json)
        if not bios_ref:
            results[bios_key] = f'Not found in DCS-BIOS {dcsbios_ver}'
            continue
        bios_outputs = bios_ref['outputs'][0]
        for args_key in plane_bios[bios_key]['args']:
            aircraft_value = plane_bios[bios_key]['args'][args_key]
            dcsbios_value = bios_outputs[args_key]
            if not aircraft_value == dcsbios_value:
                bios_issue = {args_key: f"dcspy: {aircraft_value} ({hex(aircraft_value)}) "
                                        f"bios: {dcsbios_value} ({hex(dcsbios_value)})"}
                if results.get(bios_key):
                    results[bios_key].update(bios_issue)
                else:
                    results[bios_key] = bios_issue
    return results


def _get_json_for_plane(plane: str) -> dict:
    data = get(f'https://raw.githubusercontent.com/DCSFlightpanels/dcs-bios/{dcsbios_ver}/Scripts/DCS-BIOS/doc/json/{plane}')
    return loads(data.content)


def _recursive_lookup(k: str, d: dict):
    if k in d:
        return d[k]
    for v in d.values():
        if isinstance(v, dict):
            item = _recursive_lookup(k, v)
            if item:
                return item
