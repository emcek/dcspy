from sys import platform
from unittest.mock import patch

from pytest import mark


@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot, resources, switch_dcs_bios_path_in_config):
    from time import sleep

    from PySide6 import QtCore
    from PySide6.QtCore import Qt
    from PySide6.QtQuick import QQuickWindow, QSGRendererInterface

    from dcspy import qt_gui

    QQuickWindow.setGraphicsApi(QSGRendererInterface.OpenGLRhi)
    QtCore.QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    with patch.object(qt_gui, 'get_default_yaml', return_value=resources / 'c.yml'):
        dcspy_gui = qt_gui.DcsPyQtGui()
    dcspy_gui.show()
    qtbot.addWidget(dcspy_gui)
    dcspy_gui.rb_g19.setChecked(True)
    dcspy_gui.sp_completer.setValue(10)
    dcspy_gui.combo_planes.setCurrentIndex(1)
    sleep(0.7)
    qtbot.mouseClick(dcspy_gui.pb_save, Qt.LeftButton)
    qtbot.mouseClick(dcspy_gui.pb_start, Qt.LeftButton)
    qtbot.mouseClick(dcspy_gui.pb_stop, Qt.LeftButton)
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
    sleep(0.7)
