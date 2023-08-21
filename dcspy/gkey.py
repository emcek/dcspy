import os
from pprint import pprint
from typing import Any, Dict, List

import requests

from dcspy.models import Control, ControlKeyData, DcsBios

json_directory_url = 'https://raw.githubusercontent.com/DCSFlightpanels/dcs-bios/master/Scripts/DCS-BIOS/doc/json/'


def parse_json(url: str) -> Dict[str, Any]:
    data = {}
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            _ = DcsBios.model_validate(data)
    except Exception as e:
        print(f'Error parsing JSON from {url}: {e}')
    return data


def get_inputs_for_plane_url(json_file: str) -> Dict[str, Dict[str, ControlKeyData]]:
    ctrl_key: Dict[str, Dict[str, ControlKeyData]] = {}
    json_data = parse_json(os.path.join(json_directory_url, f'{json_file}.json'))

    for section, controllers in json_data.items():
        ctrl_key[section] = {}
        for ctrl_name, ctrl_data in controllers.items():
            try:
                Control.model_validate(ctrl_data)
            except ValueError:
                print(json_file, section, ctrl_name)
            ctrl = Control(**ctrl_data)
            if ctrl.inputs:
                ctrl_key[section][ctrl_name] = ControlKeyData.from_dicts(ctrl_data['description'], ctrl_data['inputs'])

        if not len(ctrl_key[section]):
            del ctrl_key[section]
    return ctrl_key


if __name__ == '__main__':
    json_files = [
        # "A-10C.json",
        # "A-29B.json",
        # "A-4E-C.json",
        # "AH-64D.json",
        # "AH-6J.json",
        # "AJS37.json",
        # "Alphajet.json",
        # "AV8BNA.json",
        # "Bf-109K-4.json",
        # "C-101.json",
        # "Christen Eagle II.json",
        # "CommonData.json",
        # "Edge540.json",
        # "F-14.json",
        # "F-15E.json",
        "F-16C_50.json",
        # "F-22A.json",
        # "F-5E-3.json",
        # "F-86F Sabre.json",
        "FA-18C_hornet.json",
        # "FC3.json",
        # "FW-190A8.json",
        # "FW-190D9.json",
        # "I-16.json",
        # "JF-17.json",
        # "Ka-50.json",
        # "L-39.json",
        # "M-2000C.json",
        # "MB-339.json",
        # "Mi-24P.json",
        # "Mi-8MT.json",
        # "MiG-15bis.json",
        # "MiG-19P.json",
        # "MiG-21Bis.json",
        # "MirageF1.json",
        # "Mosquito.json",
        # "NS430.json",
        # "P-47D.json",
        # "P-51D.json",
        # "SA342.json",
        # "SpitfireLFMkIX.json",
        # "SuperCarrier.json",
        # "UH-1H.json",
        # "VNAO_Room.json",
        # "VNAO_T-45.json",
        # "Yak-52.json",
    ]
    pprint(get_inputs_for_plane_url('F-16C_50'))
