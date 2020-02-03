import socket
import struct
import sys
from logging import info, debug, warning
from time import time, gmtime

from packaging import version
from requests import get

from dcspy import RECV_ADDR, MULTICAST_IP, __version__
from dcspy.dcsbios import ProtocolParser
from dcspy.logitech import G13


def check_current_version() -> None:
    """Check if version is current."""
    try:
        response = get('https://api.github.com/repos/emcek/dcspy/releases/latest')
        if response.status_code == 200:
            online_version = response.json()['tag_name']
            if version.parse(online_version) > version.parse(__version__):
                info(f'There is new version of dcspy: {online_version}')
            elif version.parse(online_version) == version.parse(__version__):
                info(f'This is up-to-date version: {__version__}')
        else:
            warning(f'Unable to check version online. Try again later. Status={response.status_code}')
    except Exception as exc:
        warning(f'Unable to check version online: {exc}')


def _handle_connection(g13: G13, parser: ProtocolParser, sock: socket.socket) -> None:
    """
    Main loop where all the magic is happened.

    :param g13: type of Logitech keyboard with LCD
    :type g13: G13
    :param parser: DCS protocol parser
    :type parser: ProtocolParser
    :param sock: multi-cast UDP socket
    :type sock: socket.socket
    """
    start = time()
    while True:
        try:
            dcs_bios_resp = sock.recv(2048)
            for int_byte in dcs_bios_resp:
                parser.process_byte(int_byte)
                start = time()
            if g13.plane_detected:
                g13.load_new_plane()
            g13.button_handle(sock)
        except socket.error as exp:
            _sock_err_handler(g13, start)
            debug(f'Main loop socket error: {exp}')
            info('Waiting for DCS connection...')


def _sock_err_handler(g13, start):
    wait_time = gmtime(time() - start)
    spacer = ' ' * 13
    g13.display = ['Logitech G13 OK', 'No new data from DCS:',
                   f'{spacer}{wait_time.tm_min:02d}:{wait_time.tm_sec:02d} [min:s]', f'dcspy: v{__version__}']


def _prepare_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(RECV_ADDR)
    mreq = struct.pack('=4sl', socket.inet_aton(MULTICAST_IP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(1)
    return sock


def run():
    """Main of running function."""
    info(f'dcspy {__version__} https://github.com/emcek/dcspy')
    check_current_version()
    parser = ProtocolParser()
    g13 = G13(parser)
    sock = _prepare_socket()
    try:
        _handle_connection(g13, parser, sock)
    except KeyboardInterrupt:
        info('Exit due to Ctrl-C')
        sys.exit(0)


if __name__ == '__main__':
    run()
