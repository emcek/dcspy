import signal
import sys
from argparse import Namespace
from logging import getLogger
from os import environ, unlink
from pathlib import Path
from tempfile import gettempdir

from PySide6.QtWidgets import QApplication

from dcspy import get_config_yaml_item
from dcspy.qt_gui import DcsPyQtGui

LOG = getLogger(__name__)
__version__ = '3.4.1'


def run(cli_args: Namespace = Namespace()) -> None:
    """Run DCSpy Qt6 GUI."""
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    app.setStyle('fusion')

    try:
        window = DcsPyQtGui(cli_args)
        if get_config_yaml_item('show_gui', True):
            window.show()
        unlink(Path(gettempdir()) / f'onefile_{environ["NUITKA_ONEFILE_PARENT"]}_splash_feedback.tmp')
        app.aboutToQuit.connect(window.event_set)
    except (KeyError, FileNotFoundError):
        pass
    except Exception as exp:
        LOG.exception(f'Critical error: {exp}')
    finally:
        sys.exit(app.exec())
