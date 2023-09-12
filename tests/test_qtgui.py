from sys import platform

from pytest import mark


@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot, default_config):
    from PySide6.QtCore import Qt

    from dcspy.qt_gui import DcsPyQtGui

    default_config.update({'check_bios': False, 'check_ver': False})
    dcspy_gui = DcsPyQtGui(cfg_dict=default_config)
    dcspy_gui.show()
    qtbot.addWidget(dcspy_gui)
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
