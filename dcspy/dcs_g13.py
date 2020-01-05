import socket
from logging import basicConfig, DEBUG, info, debug, warning, error
from time import sleep

from packaging import version
from requests import get

from dcspy.dcsbios import ProtocolParser
from dcspy.logitech import G13

__version__ = '0.9.0'
basicConfig(format='%(asctime)s | %(levelname)-7s | %(message)s / %(filename)s:%(lineno)d', level=DEBUG)


def attempt_connect(sock: socket.socket) -> None:
    """
    Attempt to connect to localhost.

    :param sock: socket
    """
    connected = False
    info('Waiting for DCS connection...')
    while not connected:
        try:
            sock.connect(('127.0.0.1', 7778))
            info('Connected')
            connected = True
        except socket.error:
            sleep(2)


def check_current_version() -> None:
    """Check if version is current."""
    try:
        url = 'https://api.github.com/repos/emcek/dcspy/releases'
        response = get(url)
        if response.status_code == 200:
            json_response = response.json()
            online_version = json_response['tag_name']
            if version.parse(online_version) > version.parse(__version__):
                info(f'There is new version of dcspy: {online_version}')
            elif version.parse(online_version) == version.parse(__version__):
                info('This is up-to-date version')
            else:
                debug(f'Something goes wrong: local version: {__version__} a online_version: {online_version}')
        else:
            warning(f'Unable to check version online. Try again later. Status={response.status_code}')
    except Exception as exc:
        warning(f'Unable to check version online: {exc}')


def run() -> None:
    """Main of running function."""
    info(f'dcspy {__version__} https://github.com/emcek/dcspy')
    check_current_version()
    while True:
        parser = ProtocolParser()
        g13 = G13(parser)
        g13.info_display(('G13 initialised OK', 'Waiting for DCS', '', f'dcspy: {__version__}'))

        sock = socket.socket()
        sock.settimeout(None)

        attempt_connect(sock)
        while True:
            try:
                dcs_bios_resp = sock.recv(1)
                parser.process_byte(dcs_bios_resp)
                if g13.shouldActivateNewAC:
                    g13.activate_new_ac()
                g13.button_handle(sock)
            except socket.error as exp:
                debug(f'Main loop socket error: {exp}')
                sleep(2)
            except KeyboardInterrupt:
                info('Exit due to Ctrl-C')
                exit(0)
            except Exception as exp:
                error(f'Unexpected error: resetting... {exp.__class__.__name__}', exc_info=True)
                sleep(2)
                break
        del sock
        del g13
        del parser


if __name__ == '__main__':
    run()
