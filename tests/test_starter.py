import socket
from unittest.mock import patch

from pytest import mark


def test_load_new_plane_if_detected(g13_starter):
    from dcspy import starter
    with patch.object(starter, 'LogitechDevice') as lcd:
        g13_starter._load_new_plane_if_detected(lcd)
        lcd.load_new_plane.assert_called_once_with()


@mark.parametrize('keyboard, dcspy_starter', [
    ('keyboard_mono', 'g13_starter'), ('keyboard_color', 'g19_starter')
], ids=['mono', 'color'])
def test_sock_err_handler(keyboard, dcspy_starter, request):
    from time import time

    from dcspy import starter

    ver_string = f'v{starter.__version__} (latest)'
    start_time = time()
    dcspy_starter = request.getfixturevalue(dcspy_starter)
    keyboard = request.getfixturevalue(keyboard)

    dcspy_starter._sock_err_handler(logi_device=keyboard, start_time=start_time, ver_string=ver_string,
                                    support_iter=(i for i in '12'), exp=Exception())
    assert keyboard.messages == ['Logitech LCD OK', 'No data from DCS:      00:00', '1', ver_string]
    assert len(keyboard.text) == 5


def test_supporters(g13_starter):
    sup_iter = g13_starter._supporters(text='123456', width=5)
    assert next(sup_iter) == '12345'
    assert next(sup_iter) == '23456'
    assert next(sup_iter) == '34561'


def test_prepare_socket(g13_starter):
    sock = g13_starter._prepare_socket()
    assert isinstance(sock, socket.socket)
    assert sock.proto == 17
    assert sock.type in (2050, 2)
    assert sock.family == 2


@mark.slow
@mark.e2e
def test_run_dcs_with_bios_data(resources):
    from threading import Event, Thread

    from dcspy.models import DEFAULT_FONT_NAME, G13, FontsConfig
    from dcspy.starter import DCSpyStarter
    from tests.helpers import send_bios_data

    event = Event()
    fonts_cfg = FontsConfig(name=DEFAULT_FONT_NAME, small=9, medium=11, large=16, ded_font=False)
    G13.lcd_info.set_fonts(fonts_cfg)
    app_thread = Thread(target=DCSpyStarter(model=G13, event=event))
    app_thread.name = 'dcspy-test-app'
    app_thread.start()

    send_bios_data(data_file=resources / 'dcs_bios_data.json')
    event.set()
