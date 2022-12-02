import socket
import struct
from collections import deque
from importlib import import_module
from logging import getLogger
from threading import Event
from time import time, gmtime
from typing import Iterator

from dcspy import RECV_ADDR, MULTICAST_IP
from dcspy.dcsbios import ProtocolParser
from dcspy.logitech import LogitechKeyboard
from dcspy.utils import check_ver_at_github

LOG = getLogger(__name__)
LOOP_FLAG = True
__version__ = '1.7.5'


def _handle_connection(lcd: LogitechKeyboard, parser: ProtocolParser, sock: socket.socket, event: Event) -> None:
    """
    Main loop where all the magic is happened.

    :param lcd: type of Logitech keyboard with LCD
    :param parser: DCS protocol parser
    :param sock: multi-cast UDP socket
    :param event: stop event for main loop
    """
    start_time = time()
    result = check_ver_at_github(repo='emcek/dcspy', current_ver=__version__)
    current_ver = 'latest' if result[0] else 'please update!'
    LOG.info('Waiting for DCS connection...')
    support_banner = _supporters(text='Huge thanks to: Sireyn, Nick Thain, BrotherBloat and others! For support and help! ', width=26)
    while not event.is_set():
        try:
            dcs_bios_resp = sock.recv(2048)
            for int_byte in dcs_bios_resp:
                parser.process_byte(int_byte)
            start_time = time()
            _load_new_plane_if_detected(lcd)
            lcd.button_handle(sock)
        except OSError as exp:
            _sock_err_handler(lcd, start_time, current_ver, support_banner, exp)


def _load_new_plane_if_detected(lcd: LogitechKeyboard) -> None:
    """
    Load instance when new plane detected.

    :param lcd: type of Logitech keyboard with LCD
    """
    global LOOP_FLAG
    if lcd.plane_detected:
        lcd.load_new_plane()
        LOOP_FLAG = True


def _supporters(text: str, width: int) -> Iterator[str]:
    """
    Scroll text with widow width.

    :param text: text to scroll
    :param width: width of window
    """
    queue = deque(text)
    while True:
        yield ''.join(queue)[:width]
        queue.rotate(-1)


def _sock_err_handler(lcd: LogitechKeyboard, start_time: float, current_ver: str, support_iter: Iterator[str], exp: Exception) -> None:
    """
    Show basic data when DCS is disconnected.

    :param lcd: type of Logitech keyboard with LCD
    :param start_time: time when connection to DCS was lost
    :param current_ver: logger.info about current version to show
    :param support_iter: iterator for banner supporters
    :param exp: caught exception instance
    """
    global LOOP_FLAG
    if LOOP_FLAG:
        LOG.debug(f'Main loop socket error: {exp}')
        LOOP_FLAG = False
    wait_time = gmtime(time() - start_time)
    lcd.display = ['Logitech LCD OK',
                   f'No data from DCS:   {wait_time.tm_min:02d}:{wait_time.tm_sec:02d}',
                   f'{next(support_iter)}',
                   f'v{__version__} ({current_ver})']


def _prepare_socket() -> socket.socket:
    """
    Preparing multi-cast UDP socket for DCS-BIOS communication.

    :return: socket object
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(RECV_ADDR)
    mreq = struct.pack('=4sl', socket.inet_aton(MULTICAST_IP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(1)
    return sock


def dcspy_run(lcd_type: str, event: Event) -> None:
    """
    Real starting point of DCSpy.

    :param lcd_type: LCD handling class as string
    :param event: stop event for main loop
    """
    parser = ProtocolParser()
    lcd = getattr(import_module('dcspy.logitech'), lcd_type)(parser)
    LOG.info(f'Loading: {str(lcd)}')
    LOG.debug(f'Loading: {repr(lcd)}')
    dcs_sock = _prepare_socket()
    _handle_connection(lcd, parser, dcs_sock, event)
    dcs_sock.close()
    LOG.info('DCSpy stopped.')
    lcd.display = ['Logitech LCD OK', 'DCSpy stopped', '', f'v{__version__}']
