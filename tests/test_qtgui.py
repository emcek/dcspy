from PySide6.QtCore import Qt

from dcspy.qt_gui import DcsPyQtGui


def test_qt(qtbot):
    dcspy_gui = DcsPyQtGui()
    dcspy_gui.show()
    qtbot.addWidget(dcspy_gui)
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
