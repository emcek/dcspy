from collections.abc import Sequence
from pathlib import Path
from socket import AF_INET, SOCK_DGRAM, socket
from time import sleep
from typing import Union
from unittest.mock import patch

from PIL import Image, ImageChops

from dcspy.aircraft import BasicAircraft
from dcspy.models import MULTICAST_IP, UDP_PORT
from dcspy.sdk.lcd_sdk import LcdSdkManager
from dcspy.utils import load_json

all_plane_list = ['fa18chornet', 'f16c50', 'f15ese', 'ka50', 'ka503', 'mi8mt', 'mi24p', 'ah64dblkii', 'a10c', 'a10c2', 'f14a135gr', 'f14b', 'av8bna']


def set_bios_during_test(aircraft_model: BasicAircraft, bios_pairs: Sequence[tuple[str, Union[str, int]]]) -> None:
    """
    Set BIOS values for a given aircraft model.

    :param aircraft_model:
    :param bios_pairs:
    """
    if aircraft_model.lcd.type.name == 'COLOR':
        with patch.object(LcdSdkManager, 'logi_lcd_color_set_background', return_value=True), \
                patch.object(LcdSdkManager, 'logi_lcd_update', return_value=True):
            for selector, value in bios_pairs:
                aircraft_model.set_bios(selector, value)
    else:
        with patch.object(LcdSdkManager, 'logi_lcd_mono_set_background', return_value=True), \
                patch.object(LcdSdkManager, 'logi_lcd_update', return_value=True):
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
        print(f'\nDiff percentage: {percents}%\nDiff len: {len_diff}\nDiff size: {pixel_diff.getbbox()}')
    return all([percents <= precision, not len_diff])


def assert_bytes(test_bytes: bytes, ref_bytes: bytes) -> tuple[float, int]:
    """
    Compare bytes and return percentage of differences and differences in size.

    :param test_bytes: Bytes to compare
    :param ref_bytes: Referenced bytes
    :return: Tuple with float of percentage and difference in size
    """
    percents = []
    try:
        percents = [1 for i, b in enumerate(ref_bytes) if b != test_bytes[i]]
    except IndexError:
        pass
    return float(f'{sum(percents) / len(ref_bytes) * 100:.2f}'), len(ref_bytes) - len(test_bytes)


def send_bios_data(data_file: Path) -> None:
    """
    Read the BIOS data from the given JSON file.

    Converts it into a list of tuples containing the timing and data, and sends the data over UDP socket using elapsed time.

    :param data_file: The file path of the JSON file containing the BIOS data.
    """
    json_payload = load_json(full_path=data_file)
    messages = [(item['timing'], bytes.fromhex(item['data'])) for item in json_payload]

    with socket(AF_INET, SOCK_DGRAM) as sock:
        for elapsed_time, data in messages:
            elapsed_time_float = float(elapsed_time)
            print(f'Sending message of {len(data)} bytes with elapsed time {elapsed_time_float} seconds')
            sock.sendto(data, (MULTICAST_IP, UDP_PORT))
            sleep(elapsed_time_float)
