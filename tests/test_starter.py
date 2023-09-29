import socket
from unittest.mock import patch


def test_load_new_plane_if_detected():
    from dcspy import starter
    with patch.object(starter, 'KeyboardManager') as lcd:
        starter._load_new_plane_if_detected(lcd)
        lcd.load_new_plane.assert_called_once_with()


def test_sock_err_handler():
    from time import time

    from dcspy import starter
    ver_string = f'v{starter.__version__} (latest)'
    start_time = time()
    with patch.object(starter, 'KeyboardManager') as logi_key:
        starter._sock_err_handler(manager=logi_key, start_time=start_time, ver_string=ver_string,
                                  support_iter=(i for i in '12'), exp=Exception())
        assert logi_key.display == ['Logitech LCD OK', 'No data from DCS:   00:00', '1', ver_string]


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
