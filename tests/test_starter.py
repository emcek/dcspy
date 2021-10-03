import socket

from dcspy import starter


def test_prepare_socket():
    sock = starter._prepare_socket()
    assert isinstance(sock, socket.socket)
    assert sock.proto == 17
    assert sock.gettimeout() == 1.0
    assert sock.type in (2050, 2)
    assert sock.family == 2
