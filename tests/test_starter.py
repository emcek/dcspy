import socket


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
    assert sock.gettimeout() == 1.0
    assert sock.type in (2050, 2)
    assert sock.family == 2
