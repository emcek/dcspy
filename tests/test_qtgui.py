from sys import platform

from pytest import mark


@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot):
    from PySide6.QtCore import Qt

    from dcspy.qt_gui import DcsPyQtGui
    print('DUPA')
    dcspy_gui = DcsPyQtGui()
    dcspy_gui.show()
    print(dcspy_gui.config)
    qtbot.addWidget(dcspy_gui)
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
