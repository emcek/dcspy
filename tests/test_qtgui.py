from sys import platform

from pytest import mark


@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot):
    from PySide6.QtCore import Qt

    from dcspy.qt_gui import DcsPyQtGui
    dcspy_gui = DcsPyQtGui()
    print(dcspy_gui.cfg_file)
    with open(dcspy_gui.cfg_file) as f:
        d = f.read()
    print(d)
    print(dcspy_gui.cb_autoupdate_bios.isChecked())
    print(dcspy_gui.config)
    dcspy_gui.show()
    qtbot.addWidget(dcspy_gui)
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
