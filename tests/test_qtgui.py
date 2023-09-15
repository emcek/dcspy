from sys import platform
from unittest.mock import patch

from pytest import mark


@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot, resources, switch_dcs_bios_path_in_config):
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
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
