from pathlib import Path
from sys import platform

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface
from pytest import mark

resources = Path(__file__).resolve().with_name('resources')
QtCore.QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
QQuickWindow.setGraphicsApi(QSGRendererInterface.OpenGLRhi)


@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot, default_config):
    from dcspy.qt_gui import DcsPyQtGui

    default_config.update({
        'check_bios': False,
        'check_ver': False,
        'dcsbios': str(resources / 'dcs_bios'),
        'current_plane': 'A-10C',
    })
    dcspy_gui = DcsPyQtGui(cfg_dict=default_config)
    dcspy_gui.show()
    qtbot.addWidget(dcspy_gui)
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
