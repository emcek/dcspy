import socket
import struct
from collections import deque
from collections.abc import Iterator
from logging import getLogger
from threading import Event
from time import gmtime, time

from dcspy import get_config_yaml_item
from dcspy.dcsbios import ProtocolParser
from dcspy.logitech import LogitechDevice
from dcspy.models import DCSPY_REPO_NAME, MULTICAST_IP, RECV_ADDR, Color, LogitechDeviceModel, __version__
from dcspy.utils import check_bios_ver, get_version_string

LOG = getLogger(__name__)
SUPPORTERS = ['Jon Wardell', 'Simon Leigh', 'Alexander Leschanz', 'Sireyn', 'Nick Thain', 'BrotherBloat']


class DCSpyStarter:
    """Wrapper object to handle starting and showing welcome screen."""

    def __init__(self, model: LogitechDeviceModel, event: Event) -> None:
        """
        Initialize an object with a global state.

        :param model: Logitech device model
        :param event: stop event for the main loop
        """
        self.model = model
        self.event = event
        self.parser = ProtocolParser()
        self.CLEAN_BEFORE_LOAD_PLANE = False
        self.CLEAN_WHILE_WAIT_FOR_DATA = False

    def _handle_connection(self, logi_device: LogitechDevice, sock: socket.socket, ver_string: str) -> None:
        """
        Handle the main loop where all the magic is happened.

        :param logi_device: Type of Logitech keyboard with LCD
        :param sock: Multicast UDP socket
        :param ver_string: Current version to show
        """
        start_time = time()
        LOG.info('Waiting for DCS connection...')
        support_banner = DCSpyStarter._supporters(text=f'Huge thanks to: {", ".join(SUPPORTERS)} and others! For support and help! ', width=37)
        while not self.event.is_set():
            try:
                dcs_bios_resp = sock.recv(2048)
                if self.CLEAN_BEFORE_LOAD_PLANE:
                    logi_device.clear(true_clear=True)
                    self.CLEAN_BEFORE_LOAD_PLANE = False
                    self.CLEAN_WHILE_WAIT_FOR_DATA = True
                for int_byte in dcs_bios_resp:
                    self.parser.process_byte(int_byte)
                start_time = time()
                self._load_new_plane_if_detected(logi_device)
                logi_device.button_handle()
            except OSError as exp:
                self._sock_err_handler(logi_device, start_time, ver_string, support_banner, exp)

    def _load_new_plane_if_detected(self, logi_device: LogitechDevice) -> None:
        """
        Load instance when new plane detected.

        :param logi_device: Type of Logitech keyboard with LCD
        """
        if logi_device.plane_detected:
            logi_device.unload_old_plane()
            logi_device.load_new_plane()
            self.CLEAN_WHILE_WAIT_FOR_DATA = True

    @staticmethod
    def _supporters(text: str, width: int) -> Iterator[str]:
        """
        Scroll text with widow width.

        :param text: Text to scroll
        :param width: Width of a window
        """
        queue = deque(text)
        while True:
            yield ''.join(queue)[:width]
            queue.rotate(-1)

    def _sock_err_handler(self, logi_device: LogitechDevice, start_time: float, ver_string: str, support_iter: Iterator[str], exp: Exception) -> None:
        """
        Show basic data when DCS is disconnected.

        :param logi_device: Type of Logitech keyboard with LCD
        :param start_time: Time when connection to DCS was lost
        :param ver_string: Current version to show
        :param support_iter: Iterator for banner supporters
        :param exp: Caught exception instance
        """
        if self.CLEAN_WHILE_WAIT_FOR_DATA:
            LOG.debug(f'Main loop socket error: {exp}')
            logi_device.clear(true_clear=True)
            self.CLEAN_BEFORE_LOAD_PLANE = True
            self.CLEAN_WHILE_WAIT_FOR_DATA = False
        wait_time = gmtime(time() - start_time)
        logi_device.text = [('     DCSpy       ', Color.orange),
                            ('Logitech LCD OK', Color.lightgreen),
                            (f'No data from DCS:      {wait_time.tm_min:02d}:{wait_time.tm_sec:02d}', Color.red),
                            (f'{next(support_iter)}', Color.yellow),
                            (ver_string, Color.white)]

    @staticmethod
    def _prepare_socket() -> socket.socket:
        """
        Prepare a multicast UDP socket for DCS-BIOS communication.

        :return: Socket object
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(RECV_ADDR)
        mreq = struct.pack('=4sl', socket.inet_aton(MULTICAST_IP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.settimeout(0.5)
        return sock

    def __call__(self, *args, **kwargs) -> None:
        """Real starting point of DCSpy."""
        with DCSpyStarter._prepare_socket() as dcs_sock:
            logi_dev = LogitechDevice(parser=self.parser, sock=dcs_sock, model=self.model)
            LOG.info(f'Loading: {str(logi_dev)}')
            LOG.debug(f'Loading: {repr(logi_dev)}')
            dcspy_ver = get_version_string(repo=DCSPY_REPO_NAME, current_ver=__version__, check=bool(get_config_yaml_item('check_ver')))
            self._handle_connection(logi_device=logi_dev, sock=dcs_sock, ver_string=dcspy_ver)
        LOG.info('DCSpy stopped.')
        logi_dev.text = [('     DCSpy       ', Color.orange),
                         ('DCSpy stopped', Color.red),
                         ('', Color.black),
                         (f'DCSpy:    {dcspy_ver}', Color.white),
                         (f'DCS-BIOS:  {check_bios_ver(bios_path=get_config_yaml_item("dcsbios"))}', Color.white)]
