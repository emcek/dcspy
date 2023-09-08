from os import environ
from sys import platform

from pytest import mark


@mark.qt6
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_qt(qtbot):
    from PySide6.QtCore import Qt

    from dcspy.qt_gui import DcsPyQtGui

    cfg_dict = {'dcsbios': f'D:\\Users\\{environ.get("USERNAME", "UNKNOWN")}\\Saved Games\\DCS.openbeta\\Scripts\\DCS-BIOS',
                'dcs': 'C:\\Program Files\\Eagle Dynamics\\DCS World OpenBeta', 'keyboard': 'G13', 'save_lcd': False, 'show_gui': True, 'autostart': False,
                'verbose': False, 'check_bios': False, 'check_ver': False, 'font_name': 'consola.ttf', 'font_mono_s': 11, 'font_mono_xs': 9, 'font_mono_l': 16,
                'font_color_s': 22, 'font_color_xs': 18, 'font_color_l': 32, 'f16_ded_font': True, 'git_bios': False, 'git_bios_ref': 'master',
                'theme_mode': 'system', 'theme_color': 'dark-blue'}
    dcspy_gui = DcsPyQtGui(cfg_dict=cfg_dict)
    dcspy_gui.show()
    qtbot.addWidget(dcspy_gui)
    qtbot.mouseClick(dcspy_gui.pb_close, Qt.LeftButton)
