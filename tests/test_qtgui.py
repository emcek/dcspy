from pathlib import Path
from sys import platform

from pytest import mark

resources = Path(__file__).resolve().with_name('resources')


@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot, default_config):
    from PySide6.QtCore import Qt

    from dcspy.qt_gui import DcsPyQtGui

    default_config.update({
        'check_bios': False,
        'check_ver': False,
        'dcsbios': str(resources / 'dcs_bios'),
        'current_plane': 'A-10C',
    })
    import os
    print(f'----------------- {os.getcwd()} -----------------------')
    dcspy_gui = DcsPyQtGui(cfg_dict=default_config)
    dcspy_gui.show()
    qtbot.addWidget(dcspy_gui)
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
