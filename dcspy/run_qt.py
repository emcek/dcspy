import signal
import sys
from logging import getLogger

from PySide6.QtWidgets import QApplication

from dcspy.qt_gui import DcsPyQtGui

LOG = getLogger(__name__)
__version__ = '2.4.0'


def run_gui() -> None:
    """Run DCSpy Qt6 GUI."""
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    app.setStyle('fusion')

    try:
        window = DcsPyQtGui()
        window.show()
        app.aboutToQuit.connect(window.event_set)
    except Exception as exp:
        LOG.exception(f'Critical error: {exp}')
    finally:
        sys.exit(app.exec())


if __name__ == '__main__':
    run_gui()
