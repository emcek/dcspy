from datetime import datetime
from json import loads
from os import path
from tempfile import gettempdir
from typing import Tuple, List, Union, Dict
from unittest.mock import patch

from requests import get, exceptions

from dcspy.aircraft import Aircraft, BiosValue
from dcspy.sdk import lcd_sdk
try:
    response = get(url='https://api.github.com/repos/DCSFlightpanels/dcs-bios/releases/latest', timeout=2)
    if response.status_code == 200:
        DCS_BIOS_VER = response.json()['tag_name']
except exceptions.ConnectTimeout:
    DCS_BIOS_VER = 'v0.7.47'

all_plane_list = ['FA18Chornet', 'F16C50', 'Ka50', 'Ka503', 'Mi8MT', 'Mi24P', 'AH64DBLKII', 'A10C', 'A10C2', 'F14A135GR', 'F14B', 'AV8BNA']


def check_dcsbios_data(plane_bios: dict, plane_json: str) -> Tuple[dict, str]:
    """
    Verify if all aircraft's data are correct with DCS-BIOS.

    :param plane_bios: BIOS data from plane
    :param plane_json: DCS-BIOS json filename
    :return: result of checks and DCS-BIOS version
    """
    results = {}
    local_json = _get_json_for_plane(plane_json)
    for bios_key in plane_bios:
        bios_ref = _recursive_lookup(bios_key, local_json)
        if not bios_ref:
            results[bios_key] = f'Not found in DCS-BIOS {DCS_BIOS_VER}'
            continue
        output_type = plane_bios[bios_key]['klass'].split('Buffer')[0].lower()
        try:
            bios_outputs = [out for out in bios_ref['outputs'] if output_type == out['type']][0]
        except IndexError:
            results[bios_key] = f'Wrong output type: {output_type}'
            continue
        results = _compare_dcspy_with_bios(bios_key, bios_outputs, plane_bios, results)
    return results, DCS_BIOS_VER


def _compare_dcspy_with_bios(bios_key: str, bios_outputs: dict, plane_bios: dict, results: dict) -> dict:
    """
    Compare DCS-BIOS and Plane data and return all differences.

    :param bios_key: BIOS key
    :param bios_outputs: DCS-BIOS outputs dict
    :param plane_bios: BIOS data from plane
    :param results: dict with differences
    :return: updated dict with differences
    """
    for args_key in plane_bios[bios_key]['args']:
        aircraft_value = plane_bios[bios_key]['args'][args_key]
        dcsbios_value = bios_outputs[args_key]
        if aircraft_value != dcsbios_value:
            bios_issue = {args_key: f"dcspy: {aircraft_value} ({hex(aircraft_value)}) "
                                    f"bios: {dcsbios_value} ({hex(dcsbios_value)})"}
            if results.get(bios_key):
                results[bios_key].update(bios_issue)
            else:
                results[bios_key] = bios_issue
    return results


def _get_json_for_plane(plane: str) -> dict:
    """
    Download json file for plane and write it to temporary directory.

    Json is downloaded when:
    * file doesn't exist
    * file is older the one week

    :param plane: DCS-BIOS json filename
    :return: json as dict
    """
    plane_path = path.join(gettempdir(), plane)
    try:
        m_time = path.getmtime(plane_path)
        week = datetime.fromtimestamp(int(m_time)).strftime('%U')
        if week == datetime.now().strftime('%U'):
            with open(plane_path) as plane_json_file:
                data = plane_json_file.read()
            return loads(data)
        raise ValueError('File is outdated')
    except (FileNotFoundError, ValueError):
        data = get(f'https://raw.githubusercontent.com/DCSFlightpanels/dcs-bios/{DCS_BIOS_VER}/Scripts/DCS-BIOS/doc/json/{plane}')
        with open(plane_path, 'wb+', encoding='utf-8') as plane_json_file:
            plane_json_file.write(data.content)
        return loads(data.content)


def _recursive_lookup(search_key: str, bios_dict: dict) -> dict:
    """
    Search for search_key recursively in dict and return its value.

    :param search_key: search value for this key
    :param bios_dict: dict to be search
    :return: value (dict) for search_key
    """
    if search_key in bios_dict:
        return bios_dict[search_key]
    for value in bios_dict.values():
        if isinstance(value, dict):
            item = _recursive_lookup(search_key, value)
            if item:
                return item


def generate_bios_data_for_plane(plane_bios: dict, plane_json: str) -> Dict[str, BiosValue]:
    """
    generate dict of BIOS values for plane.

    :param plane_bios: BIOS data from plane
    :param plane_json: DCS-BIOS json filename
    :return: dict of BIOS_VALUE for plane
    """
    results = {}
    local_json = _get_json_for_plane(plane_json)
    for bios_key in plane_bios:
        bios_ref = _recursive_lookup(bios_key, local_json)
        if not bios_ref:
            results[bios_key] = f'Not found in DCS-BIOS {DCS_BIOS_VER}'
            continue
        bios_outputs = bios_ref['outputs'][0]
        buff_type = f'{bios_outputs["type"].capitalize()}Buffer'
        if 'String' in buff_type:
            results[bios_key] = {'klass': buff_type,
                                 'args': {'address': hex(bios_outputs['address']),
                                          'max_length': hex(bios_outputs['max_length'])},
                                 'value': ''}
        elif 'Integer' in buff_type:
            results[bios_key] = {'klass': buff_type,
                                 'args': {'address': hex(bios_outputs['address']),
                                          'mask': hex(bios_outputs['mask']),
                                          'shift_by': hex(bios_outputs['shift_by'])},
                                 'value': int()}
    return results


def set_bios_during_test(aircraft_model: Aircraft, bios_pairs: List[Tuple[str, Union[str, int]]]) -> None:
    """
    Set BIOS values for a given aircraft model.

    :param aircraft_model:
    :param bios_pairs:
    """
    if aircraft_model.lcd.type.name == 'COLOR':
        with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=[False, True] * len(bios_pairs)), \
                patch.object(lcd_sdk, 'logi_lcd_color_set_background', return_value=True), \
                patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
            for selector, value in bios_pairs:
                aircraft_model.set_bios(selector, value)
    else:
        with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=[True] * len(bios_pairs)), \
                patch.object(lcd_sdk, 'logi_lcd_mono_set_background', return_value=True), \
                patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
            for selector, value in bios_pairs:
                aircraft_model.set_bios(selector, value)
