import signal
import sys
import time
from argparse import Namespace
from functools import partial
from logging import getLogger
from os import environ, unlink
from pathlib import Path
from tempfile import gettempdir

from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QApplication, QProgressBar, QSplashScreen

from dcspy import get_config_yaml_item
from dcspy.qt_gui import DcsPyQtGui

LOG = getLogger(__name__)


def _update_progress(progbar: QProgressBar) -> None:
    """
    Update the progress bar, when loading application.

    :type progbar: Progress bar object
    """
    for i in range(1, 101):
        progbar.setValue(i)
        time.sleep(0.002)
    LOG.debug('Splash screen loading finished.')


def run(cli_args: Namespace = Namespace()) -> None:
    """Run DCSpy Qt6 GUI."""
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    app.setStyle('fusion')

    splash_pixmap = QPixmap((Path(__file__) / '..' / 'img' / 'splash.png').resolve())
    splash_screen = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash_screen.showMessage('Loading... Please wait.', Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, Qt.GlobalColor.black)
    progress_bar = QProgressBar(splash_screen)
    progress_bar.setGeometry(50, splash_pixmap.height() - 40, splash_pixmap.width() - 100, 20)
    progress_bar.setTextVisible(False)
    splash_screen.show()

    try:
        window = DcsPyQtGui(cli_args)
        QTimer.singleShot(5, partial(_update_progress, progress_bar))
        splash_screen.finish(window)
        if get_config_yaml_item('show_gui', True):
            window.show()
        app.aboutToQuit.connect(window.event_set)
        unlink(Path(gettempdir()) / f'onefile_{environ["NUITKA_ONEFILE_PARENT"]}_splash_feedback.tmp')
    except (KeyError, FileNotFoundError):
        pass
    except Exception as exp:
        LOG.exception(f'Critical error: {exp}', exc_info=True)
    finally:
        sys.exit(app.exec())
