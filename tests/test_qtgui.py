from sys import platform
from unittest.mock import patch

from pytest import mark


@mark.slow
@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot, test_config_yaml, switch_dcs_bios_path_in_config, tmpdir):
    from time import sleep

    from PySide6 import QtCore
    from PySide6.QtCore import Qt
    from PySide6.QtQuick import QQuickWindow, QSGRendererInterface

    from dcspy import qt_gui

    QQuickWindow.setGraphicsApi(QSGRendererInterface.OpenGLRhi)
    QtCore.QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    with patch('dcspy.qt_gui.default_yaml', test_config_yaml):
        with patch.object(qt_gui.DcsPyQtGui, '_run_file_dialog', return_value=tmpdir):
            dcspy_gui = qt_gui.DcsPyQtGui()
            dcspy_gui.show()
            qtbot.addWidget(dcspy_gui)
            dcspy_gui.rb_g19.setChecked(True)
            dcspy_gui.sp_completer.setValue(10)
            dcspy_gui.combo_planes.setCurrentIndex(1)
            sleep(0.7)
            qtbot.mouseClick(dcspy_gui.pb_start, Qt.LeftButton)
            qtbot.mouseClick(dcspy_gui.pb_stop, Qt.LeftButton)
            qtbot.mouseClick(dcspy_gui.pb_collect_data, Qt.LeftButton)
            dcspy_gui.dw_gkeys.show()

            dcspy_gui.tw_gkeys.cellWidget(0, 0).setCurrentText('ADI_PITCH_TRIM')
            qtbot.mouseClick(dcspy_gui.tw_gkeys.cellWidget(0, 0), Qt.LeftButton)
            qtbot.mouseClick(dcspy_gui.rb_set_state, Qt.LeftButton)

            dcspy_gui.tw_gkeys.cellWidget(0, 1).setCurrentText('ARC210_CHN_KNB')

            dcspy_gui.tw_gkeys.cellWidget(1, 0).setCurrentIndex(5)
            qtbot.mouseClick(dcspy_gui.tw_gkeys.cellWidget(1, 0), Qt.LeftButton)
            qtbot.mouseClick(dcspy_gui.rb_fixed_step_dec, Qt.LeftButton)
            dcspy_gui.current_row = 1
            dcspy_gui.current_col = 0
            qtbot.mouseClick(dcspy_gui.pb_copy, Qt.LeftButton)
            qtbot.mouseClick(dcspy_gui.pb_save, Qt.LeftButton)

            qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
            sleep(0.7)
