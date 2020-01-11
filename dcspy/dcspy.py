import socket
import sys
from logging import info, debug, warning, error
from time import sleep, time

from packaging import version
from requests import get

from dcspy import __version__
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


def dcs_connected(sock: socket.socket) -> bool:
    """
    Attempt to connect to localhost.

    :param sock: socket
    :return: result as bool
    :rtype: bool
    """
    try:
        sock.connect(('127.0.0.1', 7778))
        info('DCS Connected')
        return True
    except socket.error:
        return False


def _handle_connection(g13: G13, parser: ProtocolParser, sock: socket.socket) -> None:
    """
    Main loop where all the magic is happened.

    :param g13:
    :type g13: G13
    :param parser:
    :type parser: ProtocolParser
    :param sock:
    :type sock: socket.socket
    """
    while True:
        try:
            dcs_bios_resp = sock.recv(1)
            parser.process_byte(dcs_bios_resp)
            if g13.should_activate_new_ac:
                g13.activate_new_ac()
            g13.button_handle(sock)
        except socket.error as exp:
            debug(f'Main loop socket error: {exp}')
            info('Waiting for DCS connection...')
        except KeyboardInterrupt:
            info('Exit due to Ctrl-C')
            sys.exit(0)
        except TypeError as exp:
            if exp.args[0] != 'ord() expected a character, but string of length 0 found':
                error(f'Unexpected error: resetting... {exp.__class__.__name__}', exc_info=True)
            info('DCS disconnected')
            info('Waiting for DCS connection...')
            break
        except Exception as exp:
            error(f'Unexpected error: resetting... {exp.__class__.__name__}', exc_info=True)
            info('Waiting for DCS connection...')
            break


def run() -> None:
    """Main of running function."""
    info(f'dcspy {__version__} https://github.com/emcek/dcspy')
    check_current_version()
    start = time()
    info('Waiting for DCS connection...')
    while True:
        parser = ProtocolParser()
        g13 = G13(parser)
        time_progress = time() - start
        g13.display = ['G13 initialised OK', 'Waiting for DCS:', f'{time_progress :.2f} s', f'dcspy: {__version__}']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(None)
        if dcs_connected(sock):
            _handle_connection(g13, parser, sock)
            start = time()
        else:
            time_progress = time() - start
            g13.display = ['G13 initialised OK', 'Waiting for DCS:', f'{time_progress :.2f} s', f'dcspy: {__version__}']
        sleep(0.5)
        del sock
        del g13
        del parser


if __name__ == '__main__':
    run()
