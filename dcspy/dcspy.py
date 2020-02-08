import socket
import struct
import sys
from logging import getLogger
from time import time, gmtime

from packaging import version
from requests import get

from dcspy import RECV_ADDR, MULTICAST_IP, __version__
from dcspy.dcsbios import ProtocolParser
from dcspy.logitech import KeyboardMono

LOG = getLogger(__name__)


def _check_current_version() -> bool:
    """
    Check if version is current.

    :return: True if version is current
    :rtype: bool
    """
    result = False
    try:
        response = get('https://api.github.com/repos/emcek/dcspy/releases/latest')
        if response.status_code == 200:
            online_version = response.json()['tag_name']
            if version.parse(online_version) > version.parse(__version__):
                LOG.info(f'There is new version of dcspy: {online_version}')
            elif version.parse(online_version) == version.parse(__version__):
                LOG.info(f'This is up-to-date version: {__version__}')
                result = True
        else:
            LOG.warning(f'Unable to check version online. Try again later. Status={response.status_code}')
    except Exception as exc:
        LOG.warning(f'Unable to check version online: {exc}')
    return result


def _handle_connection(lcd: KeyboardMono, parser: ProtocolParser, sock: socket.socket) -> None:
    """
    Main loop where all the magic is happened.

    :param lcd: type of Logitech keyboard with LCD
    :type lcd: KeyboardMono
    :param parser: DCS protocol parser
    :type parser: ProtocolParser
    :param sock: multi-cast UDP socket
    :type sock: socket.socket
    """
    start_time = time()
    current_ver = 'current' if _check_current_version() else 'update!'
    LOG.info('Waiting for DCS connection...')
    while True:
        try:
            dcs_bios_resp = sock.recv(2048)
            for int_byte in dcs_bios_resp:
                parser.process_byte(int_byte)
            start_time = time()
            if lcd.plane_detected:
                lcd.load_new_plane()
            lcd.button_handle(sock)
        except socket.error as exp:
            LOG.debug(f'Main loop socket error: {exp}')
            _sock_err_handler(lcd, start_time, current_ver)


def _sock_err_handler(lcd: KeyboardMono, start_time: float, current_ver: str) -> None:
    """
    Show basic data when DCS is disconnected.

    :param lcd: type of Logitech keyboard with LCD
    :type lcd: KeyboardMono
    :param start_time: time when connection to DCS was lost
    :type start_time: float
    :param current_ver: logger.info about current version to show
    :type current_ver: str
    """
    wait_time = gmtime(time() - start_time)
    spacer = ' ' * 13
    lcd.display = ['Logitech LCD OK', 'No new data from DCS:',
                   f'{spacer}{wait_time.tm_min:02d}:{wait_time.tm_sec:02d} [min:s]',
                   f'dcspy: v{__version__} ({current_ver})']


def _prepare_socket() -> socket.socket:
    """
    Preparing multi-cast UDP socket for DCS-BIOS communication.

    :return: socket object
    :rtype: socket.socket
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(RECV_ADDR)
    mreq = struct.pack('=4sl', socket.inet_aton(MULTICAST_IP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(1)
    return sock


def run():
    """Main of running function."""
    LOG.info(f'dcspy {__version__} https://github.com/emcek/dcspy')
    parser = ProtocolParser()
    lcd = KeyboardMono(parser)
    sock = _prepare_socket()
    try:
        _handle_connection(lcd, parser, sock)
    except KeyboardInterrupt:
        LOG.info('Exit due to Ctrl-C')
        sys.exit(0)


if __name__ == '__main__':
    run()
