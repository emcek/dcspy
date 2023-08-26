import signal
import sys
from logging import getLogger
from pathlib import Path

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from dcspy.qt_gui import DcsPyQtGui

LOG = getLogger(__name__)
__version__ = '2.3.1'


def run_gui() -> None:
    """Run DCSpy Qt6 GUI."""
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)

    try:
        tray = QSystemTrayIcon()
        tray.setIcon(QIcon(str(Path(__file__).resolve() / '..' / 'img' / 'dcspy.ico')))
        tray.setVisible(True)
        tray.setToolTip(f'DCSpy {__version__}')
        menu = QMenu()

        window = DcsPyQtGui()
        window.show()

        check_updates = QAction('Check updates')
        check_updates.triggered.connect(window.check_updates)
        menu.addAction(check_updates)
        action_quit = QAction('Quit')
        action_quit.triggered.connect(app.quit)
        menu.addAction(action_quit)

        tray.setContextMenu(menu)
        tray.activated.connect(window.activated)
        # app.aboutToQuit.connect(window.trigger_autosave)
    except Exception as exp:
        LOG.exception(f'Critical error: {exp}')
    finally:
        sys.exit(app.exec())


if __name__ == '__main__':
    run_gui()
