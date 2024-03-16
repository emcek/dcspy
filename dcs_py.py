import sys
from argparse import ArgumentParser, Namespace
from traceback import format_exc

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass

__version__ = '3.3.0'


def start_dcspy(cli_args: Namespace) -> None:
    """
    Start the DCSpy application with the provided command line arguments.

    :param cli_args: Namespace object containing command line arguments
    """
    try:
        from dcspy.run import run
        run(cli_args)
    except NameError as exc:
        _ = QApplication([])
        msg = QMessageBox()
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText('Git is not installed!'
                    '<br><br>Download from: <a href="https://git-scm.com/download/win">https://git-scm.com/download/win</a> 64-bit version.'
                    '<br><br>Install with default settings.')
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle('Error')
        msg.setInformativeText(f'Error text: {exc}')
        msg.setDetailedText(format_exc())
        msg.exec()
        sys.exit(1)


if __name__ == '__main__':
    parser = ArgumentParser(description='DCSpy is able to pull information from DCS aircraft and display on Logitech G-series keyboards LCD.')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s version: ' + __version__)
    parser.add_argument('-n', '--no-lcd',  action='store_true', help='Make LCD optional, not loading Logitech LCD SKD')
    args = parser.parse_args()
    start_dcspy(args)
