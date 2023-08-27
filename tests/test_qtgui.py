from sys import platform

from PySide6.QtCore import Qt
from pytest import mark

from dcspy.qt_gui import DcsPyQtGui


@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot):
    dcspy_gui = DcsPyQtGui()
    dcspy_gui.show()
    qtbot.addWidget(dcspy_gui)
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
