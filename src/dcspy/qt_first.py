from __future__ import annotations

from logging import getLogger

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QButtonGroup, QLabel, QRadioButton, QWidget, QWizard

from dcspy import qtgui_rc
from dcspy.qt_tools import UiLoader
from dcspy.utils import is_git_exec_present

_ = qtgui_rc  # prevent to remove import statement accidentally
LOG = getLogger(__name__)


class FirstRun(QWizard):
    """First run dialog for DCSpy."""
    def __init__(self, parent : QWidget | None = None) -> None:
        """
        First run dialog for DCSpy.

        :param parent: parent widget
        """
        super().__init__(parent)
        UiLoader().load_ui(':/ui/ui/firstrun.ui', self)
        self.rb_live: QRadioButton = self.findChild(QRadioButton, 'rb_live')  # type: ignore[assignment]
        self.rb_standard: QRadioButton = self.findChild(QRadioButton, 'rb_standard') # type: ignore[assignment]
        self.l_git_info: QLabel = self.findChild(QLabel, 'l_git_info') # type: ignore[assignment]
        self.bg_bios = QButtonGroup(self)
        self.bg_bios.addButton(self.rb_live)
        self.bg_bios.addButton(self.rb_standard)
        self.bg_bios.buttonClicked.connect(self._toggle_bg_bios)
        self.type = None

    def showEvent(self, arg__1: QShowEvent) -> None:
        """Prepare all information about setup of DCSpy application."""
        text = '\u2717 Git not found, download from https://git-scm.com/downloads'
        if is_git_exec_present():
            text = '\u2713 Git found, all is fine.'
        self.l_git_info.setText(text)

    def _toggle_bg_bios(self):
        for butt in self.bg_bios.buttons():
            if butt.isChecked():
                LOG.debug(f'Bios mode selected: {butt.text()}')
                self.type = butt.text()
                break
