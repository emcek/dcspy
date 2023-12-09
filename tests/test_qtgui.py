import os
from sys import platform
from unittest.mock import patch

from pytest import mark


@mark.slow
@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot, test_config_yaml, switch_dcs_bios_path_in_config, resources, tmpdir):
    from time import sleep

    from PySide6 import QtCore
    from PySide6.QtCore import Qt
    from PySide6.QtQuick import QQuickWindow, QSGRendererInterface

    from dcspy.models import ControlKeyData
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
            assert dcspy_gui.current_plane == 'A-10C'
            dcspy_gui.combo_planes.setCurrentIndex(1)
            assert dcspy_gui.current_plane == 'A-10C_2'
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
            os.remove(resources / 'A-10C_2.yaml')
            assert dcspy_gui.input_reqs['A-10C']['G1_M1'].request == 'AAP_CDUPWR TOGGLE'
            assert dcspy_gui.input_reqs['A-10C']['G1_M2'].request == 'ADI_PITCH_TRIM CYCLE 3200 65535'
            assert dcspy_gui.input_reqs['A-10C']['G1_M3'].request == 'AHCP_ALT_SCE INC'
            assert dcspy_gui.input_reqs['A-10C']['G2_M1'].request == 'AAP_CDUPWR INC'
            assert dcspy_gui.input_reqs['A-10C']['G2_M2'].request == 'ADI_PITCH_TRIM +3200'
            assert dcspy_gui.input_reqs['A-10C']['G2_M3'].request == 'AHCP_ALT_SCE DEC'
            assert dcspy_gui.input_reqs['A-10C']['G3_M1'].request == 'AAP_CDUPWR DEC'
            assert dcspy_gui.input_reqs['A-10C']['G3_M2'].request == 'ADI_PITCH_TRIM -3200'
            assert dcspy_gui.input_reqs['A-10C']['G3_M3'].request == 'AHCP_ALT_SCE CYCLE 1 2'
            assert dcspy_gui.input_reqs['A-10C']['G4_M1'].request == 'AAP_CDUPWR CYCLE 1 1'
            assert dcspy_gui.input_reqs['A-10C']['G5_M1'].request == 'AAP_STEERPT INC'
            assert dcspy_gui.input_reqs['A-10C']['G6_M1'].request == 'ADI_PITCH_TRIM +3200'
            assert dcspy_gui.input_reqs['A-10C_2']['G1_M1'].request == 'ADI_PITCH_TRIM CYCLE 3200 65535'
            assert dcspy_gui.input_reqs['A-10C_2']['G1_M2'].request == 'ARC210_CHN_KNB +3200'
            assert dcspy_gui.input_reqs['A-10C_2']['G2_M1'].request == 'AAP_STEERPT DEC'
            assert dcspy_gui.input_reqs['A-10C_2']['G2_M2'].request == 'AAP_STEERPT INC'
            assert dcspy_gui.input_reqs['A-10C_2']['G2_M3'].request == 'AAP_STEERPT INC'
            assert len(dcspy_gui.ctrl_input) == 47
            assert isinstance(dcspy_gui.ctrl_input['UFC']['UFC_1'], ControlKeyData)
            assert dcspy_gui.ctrl_input['UFC']['UFC_1'].has_fixed_step
            assert dcspy_gui.ctrl_input['UFC']['UFC_1'].has_set_state
            assert dcspy_gui.ctrl_input['UFC']['UFC_1'].has_action
            assert dcspy_gui.ctrl_input['UFC']['UFC_1'].input_len == 3
            assert len(dcspy_gui.ctrl_list) == 534
            assert len([ctrl for ctrl in dcspy_gui.ctrl_list if '--' in ctrl]) == 47
