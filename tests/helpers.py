from datetime import datetime
from json import loads
from pathlib import Path
from tempfile import gettempdir
from typing import Dict, List, Tuple, Union
from unittest.mock import patch

from PIL import Image, ImageChops
from requests import exceptions, get

from dcspy import BiosValue, aircraft
from dcspy.sdk import lcd_sdk

all_plane_list = ['fa18chornet', 'f16c50', 'f15ese', 'ka50', 'ka503', 'mi8mt', 'mi24p', 'ah64dblkii', 'a10c', 'a10c2', 'f14a135gr', 'f14b', 'av8bna']


def check_dcsbios_data(plane_bios: dict, plane_name: str, git_bios: bool) -> Tuple[dict, str]:
    """
    Verify if all aircraft's data are correct with DCS-BIOS.

    :param plane_bios: BIOS data from plane
    :param plane_name: DCS-BIOS json filename
    :param git_bios: use live/git DCS-BIOS version
    :return: result of checks and DCS-BIOS version
    """
    results, local_json = {}, {}
    bios_ver = _get_dcs_bios_version(use_git=git_bios)
    aircraft_aliases = _get_dcs_bios_json(json='AircraftAliases', bios_ver=bios_ver)
    for json_file in aircraft_aliases[plane_name]:
        local_json = {**local_json, **_get_dcs_bios_json(json=json_file, bios_ver=bios_ver)}
    for bios_key in plane_bios:
        bios_ref = _recursive_lookup(bios_key, local_json)
        if not bios_ref:
            results[bios_key] = f'Not found in DCS-BIOS {bios_ver}'
            continue
        output_type = plane_bios[bios_key]['klass'].split('Buffer')[0].lower()
        try:
            bios_outputs = [out for out in bios_ref['outputs'] if output_type == out['type']][0]
        except IndexError:
            results[bios_key] = f'Wrong output type: {output_type}'
            continue
        results = _compare_dcspy_with_bios(bios_key, bios_outputs, plane_bios, results)
    return results, bios_ver


def _get_dcs_bios_version(use_git) -> str:
    """
    Fetch stable or live DCS-BIOS version.

    :param use_git: use live/git version
    :return: version as string
    """
    bios_ver = 'master'
    if not use_git:
        try:
            response = get(url='https://api.github.com/repos/DCSFlightpanels/dcs-bios/releases/latest', timeout=2)
            if response.status_code == 200:
                bios_ver = response.json()['tag_name']
        except exceptions.ConnectTimeout:
            bios_ver = 'v0.7.48'
    return bios_ver


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
            bios_issue = {args_key: f'dcspy: {aircraft_value} ({hex(aircraft_value)}) '
                                    f'bios: {dcsbios_value} ({hex(dcsbios_value)})'}
            if results.get(bios_key):
                results[bios_key].update(bios_issue)
            else:
                results[bios_key] = bios_issue
    return results


def _get_dcs_bios_json(json: str, bios_ver: str) -> dict:
    """
    Download json file for plane and write it to temporary directory.

    Json is downloaded when:
    * file doesn't exist
    * file is older the one week

    :param json: DCS-BIOS json filename
    :param bios_ver: DCS-BIOS version
    :return: json as dict
    """
    plane_path = Path(gettempdir()) / f'{json}.json'
    try:
        m_time = plane_path.stat().st_mtime
        week = datetime.fromtimestamp(int(m_time)).strftime('%U')
        if week == datetime.now().strftime('%U'):
            with open(plane_path, encoding='utf-8') as plane_json_file:
                data = plane_json_file.read()
            return loads(data)
        raise ValueError('File is outdated')
    except (FileNotFoundError, ValueError):
        json_data = get(f'https://raw.githubusercontent.com/DCSFlightpanels/dcs-bios/{bios_ver}/Scripts/DCS-BIOS/doc/json/{json}.json')
        with open(plane_path, 'wb+') as plane_json_file:
            plane_json_file.write(json_data.content)
        return loads(json_data.content)


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


def generate_bios_data_for_plane(plane_bios: dict, plane_name: str, git_bios: bool) -> Dict[str, BiosValue]:
    """
    Generate dict of BIOS values for plane.

    :param plane_bios: BIOS data from plane
    :param plane_name: BIOS plane name
    :param git_bios: use live/git DCS-BIOS version
    :return: dict of BIOS_VALUE for plane
    """
    results = {}
    bios_ver = _get_dcs_bios_version(use_git=git_bios)
    local_json = _get_dcs_bios_json(json=plane_name, bios_ver=bios_ver)
    for bios_key in plane_bios:
        bios_ref = _recursive_lookup(search_key=bios_key, bios_dict=local_json)
        if not bios_ref:
            results[bios_key] = f'Not found in DCS-BIOS {bios_ver}'
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


def set_bios_during_test(aircraft_model: aircraft.Aircraft, bios_pairs: List[Tuple[str, Union[str, int]]]) -> None:
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


def compare_images(img: Image.Image, file_path: Path, precision: int) -> bool:
    """
    Compare generated image with saved file.

    :param img: Generated image
    :param file_path: path to reference image
    :param precision: allowed precision of image differences
    :return: True if images are the same
    """
    ref_img = Image.open(file_path)
    percents, len_diff = assert_bytes(test_bytes=img.tobytes(), ref_bytes=ref_img.tobytes())
    pixel_diff = ImageChops.difference(img, ref_img)

    if percents > precision or len_diff > 0:
        pixel_diff.save(f'{file_path}_diff.png')
        print(f'\nDiff percentage: {percents}\nDiff len: {len_diff}\nDiff size: {pixel_diff.getbbox()}')
    return all([percents <= precision, not len_diff])


def assert_bytes(test_bytes: bytes, ref_bytes: bytes) -> Tuple[float, int]:
    """
    Compare bytes and return percentage of differences and differences in size.

    :param test_bytes: bytes to compare
    :param ref_bytes: referenced bytes
    :return: tuple with float of percentage and difference in size
    """
    percents = 0
    try:
        for i, b in enumerate(ref_bytes):
            if b != test_bytes[i]:
                percents += 1
    except IndexError:
        pass
    return float(f'{percents / len(ref_bytes) * 100:.2f}'), len(ref_bytes) - len(test_bytes)
