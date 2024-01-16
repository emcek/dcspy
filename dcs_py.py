import sys
from traceback import format_exc

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass

try:
    from dcspy.run import run
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
    run()
