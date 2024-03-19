import socket
from unittest.mock import patch

from pytest import mark


def test_load_new_plane_if_detected():
    from dcspy import starter
    with patch.object(starter, 'LogitechDevice') as lcd:
        starter._load_new_plane_if_detected(lcd)
        lcd.load_new_plane.assert_called_once_with()


def test_sock_err_handler(keyboard_mono):
    from time import time

    from dcspy import starter
    ver_string = f'v{starter.__version__} (latest)'
    start_time = time()
    starter._sock_err_handler(manager=keyboard_mono, start_time=start_time, ver_string=ver_string,
                              support_iter=(i for i in '12'), exp=Exception())
    assert keyboard_mono.display == ['Logitech LCD OK', 'No data from DCS:   00:00', '1', ver_string]


def test_supporters():
    from dcspy import starter
    sup_iter = starter._supporters(text='123456', width=5)
    assert next(sup_iter) == '12345'
    assert next(sup_iter) == '23456'
    assert next(sup_iter) == '34561'


def test_prepare_socket():
    from dcspy import starter
    sock = starter._prepare_socket()
    assert isinstance(sock, socket.socket)
    assert sock.proto == 17
    assert sock.type in (2050, 2)
    assert sock.family == 2


@mark.slow
@mark.e2e
def test_run_dcs_with_bios_data(resources):
    from threading import Event, Thread

    from dcspy.models import DEFAULT_FONT_NAME, FontsConfig
    from dcspy.starter import dcspy_run
    from tests.helpers import send_bios_data

    event = Event()
    fonts_cfg = FontsConfig(name=DEFAULT_FONT_NAME, small=9, medium=11, large=16)
    app_params = {'lcd_type': 'G13', 'event': event, 'fonts_cfg': fonts_cfg}
    app_thread = Thread(target=dcspy_run, kwargs=app_params)
    app_thread.name = 'dcspy-test-app'
    app_thread.start()

    send_bios_data(data_file=resources / 'dcs_bios_data.json')
    event.set()
