from datetime import datetime
from json import loads
from os import path
from tempfile import gettempdir
from typing import Tuple, List, Union
from unittest.mock import patch

from requests import get, exceptions

from dcspy.aircraft import Aircraft

try:
    response = get(url='https://api.github.com/repos/DCSFlightpanels/dcs-bios/releases/latest', timeout=1)
    if response.status_code == 200:
        dcsbios_ver = response.json()['tag_name']
except exceptions.ConnectTimeout:
    dcsbios_ver = '0.7.46'

all_plane_list = ['FA18Chornet', 'F16C50', 'Ka50', 'AH64D', 'A10C', 'A10C2', 'F14A135GR', 'F14B', 'AV8BNA']


def check_dcsbios_data(plane_bios: dict, plane_json: str) -> Tuple[dict, str]:
    results = {}
    local_json = _get_json_for_plane(plane_json)
    for bios_key in plane_bios:
        bios_ref = _recursive_lookup(bios_key, local_json)
        if not bios_ref:
            results[bios_key] = f'Not found in DCS-BIOS {dcsbios_ver}'
            continue
        output_type = plane_bios[bios_key]['class'].split('Buffer')[0].lower()
        try:
            bios_outputs = [out for out in bios_ref['outputs'] if output_type == out['type']][0]
        except IndexError:
            results[bios_key] = f'Wrong output type: {output_type}'
            continue
        results = _compare_dcspy_with_bios(bios_key, bios_outputs, plane_bios, results)
    return results, dcsbios_ver


def _compare_dcspy_with_bios(bios_key: str, bios_outputs: dict, plane_bios: dict, results: dict) -> dict:
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
    plane_path = path.join(gettempdir(), plane)
    try:
        m_time = path.getmtime(plane_path)
        week = datetime.fromtimestamp(int(m_time)).strftime('%U')
        if week == datetime.now().strftime('%U'):
            with open(plane_path) as plane_json_file:
                data = plane_json_file.read()
            return loads(data)
        else:
            raise ValueError('File is outdated')
    except (FileNotFoundError, ValueError):
        data = get(f'https://raw.githubusercontent.com/DCSFlightpanels/dcs-bios/{dcsbios_ver}/Scripts/DCS-BIOS/doc/json/{plane}')
        with open(plane_path, 'wb+') as plane_json_file:
            plane_json_file.write(data.content)
        return loads(data.content)


def _recursive_lookup(search_key: str, bios_dict: dict) -> dict:
    if search_key in bios_dict:
        return bios_dict[search_key]
    for value in bios_dict.values():
        if isinstance(value, dict):
            item = _recursive_lookup(search_key, value)
            if item:
                return item


def set_bios_during_test(aircraft_model: Aircraft, bios_pairs: List[Tuple[str, Union[str, int]]]) -> None:
    """
    Set BIOS values for a given aircraft model.

    :param aircraft_model:
    :param bios_pairs:
    """
    from dcspy.sdk import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True), \
            patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
        for selector, value in bios_pairs:
            aircraft_model.set_bios(selector, value)
