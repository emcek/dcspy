import socket
from unittest.mock import patch, PropertyMock, MagicMock

from pytest import mark

from dcspy import starter


@mark.parametrize('online_tag, result', [('v1.1.1', True), ('v3.2.1', False)])
def test_check_ver_is_possible(online_tag, result):
    with patch.object(starter, 'get') as response_get:
        starter.__version__ = '1.1.1'
        type(response_get.return_value).status_code = PropertyMock(return_value=200)
        type(response_get.return_value).json = MagicMock(return_value={'tag_name': online_tag})
        assert starter._check_current_version() is result


def test_check_ver_can_not_check():
    with patch.object(starter, 'get') as response_get:
        type(response_get.return_value).status_code = PropertyMock(return_value=202)
        assert starter._check_current_version() is False


def test_check_ver_exception():
    with patch.object(starter, 'get', side_effect=Exception('Connection error')):
        assert starter._check_current_version() is False


def test_prepare_socket():
    sock = starter._prepare_socket()
    assert isinstance(sock, socket.socket)
    assert sock.proto == 17
    assert sock.gettimeout() == 1.0
    assert sock.type == 2
    assert sock.family == 2
