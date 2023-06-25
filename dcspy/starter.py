import socket
import struct
from collections import deque
from importlib import import_module
from logging import getLogger
from threading import Event
from time import gmtime, time
from typing import Iterator

from dcspy import MULTICAST_IP, RECV_ADDR, config
from dcspy.dcsbios import ProtocolParser
from dcspy.logitech import LogitechKeyboard
from dcspy.utils import check_bios_ver, get_version_string

LOG = getLogger(__name__)
LOOP_FLAG = True
__version__ = '2.1.2'


def _handle_connection(logi_keyboard: LogitechKeyboard, parser: ProtocolParser, sock: socket.socket, ver_string: str, event: Event) -> None:
    """
    Handle main loop where all the magic is happened.

    :param logi_keyboard: type of Logitech keyboard with LCD
    :param parser: DCS protocol parser
    :param sock: multi-cast UDP socket
    :param ver_string: current version to show
    :param event: stop event for main loop
    """
    start_time = time()
    LOG.info('Waiting for DCS connection...')
    support_banner = _supporters(text='Huge thanks to: Alexander Leschanz, Sireyn, Nick Thain, BrotherBloat and others! For support and help! ', width=26)
    while not event.is_set():
        try:
            dcs_bios_resp = sock.recv(2048)
            for int_byte in dcs_bios_resp:
                parser.process_byte(int_byte)
            start_time = time()
            _load_new_plane_if_detected(logi_keyboard)
            logi_keyboard.button_handle(sock)
        except OSError as exp:
            _sock_err_handler(logi_keyboard, start_time, ver_string, support_banner, exp)


def _load_new_plane_if_detected(logi_keyboard: LogitechKeyboard) -> None:
    """
    Load instance when new plane detected.

    :param logi_keyboard: type of Logitech keyboard with LCD
    """
    global LOOP_FLAG
    if logi_keyboard.plane_detected:
        logi_keyboard.load_new_plane()
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


def _sock_err_handler(logi_keyboard: LogitechKeyboard, start_time: float, ver_string: str, support_iter: Iterator[str], exp: Exception) -> None:
    """
    Show basic data when DCS is disconnected.

    :param logi_keyboard: type of Logitech keyboard with LCD
    :param start_time: time when connection to DCS was lost
    :param ver_string: current version to show
    :param support_iter: iterator for banner supporters
    :param exp: caught exception instance
    """
    global LOOP_FLAG
    if LOOP_FLAG:
        LOG.debug(f'Main loop socket error: {exp}')
        LOOP_FLAG = False
    wait_time = gmtime(time() - start_time)
    logi_keyboard.display = ['Logitech LCD OK',
                             f'No data from DCS:   {wait_time.tm_min:02d}:{wait_time.tm_sec:02d}',
                             f'{next(support_iter)}',
                             ver_string]


def _prepare_socket() -> socket.socket:
    """
    Prepare multi-cast UDP socket for DCS-BIOS communication.

    :return: socket object
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(RECV_ADDR)
    mreq = struct.pack('=4sl', socket.inet_aton(MULTICAST_IP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(0.5)
    return sock


def dcspy_run(lcd_type: str, event: Event) -> None:
    """
    Real starting point of DCSpy.

    :param lcd_type: LCD handling class as string
    :param event: stop event for main loop
    """
    parser = ProtocolParser()
    logi_keyboard = getattr(import_module('dcspy.logitech'), lcd_type)(parser)
    LOG.info(f'Loading: {str(logi_keyboard)}')
    LOG.debug(f'Loading: {repr(logi_keyboard)}')
    dcs_sock = _prepare_socket()
    dcspy_ver = get_version_string(repo='emcek/dcspy', current_ver=__version__, check=config['check_ver'])
    _handle_connection(logi_keyboard, parser, dcs_sock, dcspy_ver, event)
    dcs_sock.close()
    LOG.info('DCSpy stopped.')
    logi_keyboard.display = ['DCSpy stopped', '', f'DCSpy: {dcspy_ver}', f'DCS-BIOS: {check_bios_ver(bios_path=config["dcsbios"]).ver}']
