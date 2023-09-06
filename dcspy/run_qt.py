import signal
import sys
from logging import getLogger
from pathlib import Path

from PySide6 import QtGui, QtWidgets

from dcspy.qt_gui import DcsPyQtGui

LOG = getLogger(__name__)
__version__ = '2.4.0'


def run_gui() -> None:
    """Run DCSpy Qt6 GUI."""
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')

    try:
        tray = QtWidgets.QSystemTrayIcon()
        tray.setIcon(QtGui.QIcon(str(Path(__file__).resolve() / '..' / 'img' / 'dcspy.ico')))
        tray.setVisible(True)
        tray.setToolTip(f'DCSpy {__version__}')
        menu = QtWidgets.QMenu()

        window = DcsPyQtGui()
        window.show()

        check_updates = QtGui.QAction('Check updates')
        check_updates.triggered.connect(window.check_updates)
        menu.addAction(check_updates)
        action_quit = QtGui.QAction('Quit')
        action_quit.triggered.connect(app.quit)
        menu.addAction(action_quit)

        tray.setContextMenu(menu)
        tray.activated.connect(window.activated)
        app.aboutToQuit.connect(window.event_set)
    except Exception as exp:
        LOG.exception(f'Critical error: {exp}')
    finally:
        sys.exit(app.exec())


if __name__ == '__main__':
    run_gui()
