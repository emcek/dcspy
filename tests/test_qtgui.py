from sys import platform

from pytest import mark


@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot):
    from PySide6.QtCore import Qt

    from dcspy.qt_gui import DcsPyQtGui
    dcspy_gui = DcsPyQtGui()
    print(dcspy_gui.config)
    print(dcspy_gui.cb_autoupdate_bios.isChecked())
    dcspy_gui.show()
    qtbot.addWidget(dcspy_gui)
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
