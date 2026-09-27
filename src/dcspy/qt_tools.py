from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFile, QIODevice, QMetaObject
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget


class UiLoader(QUiLoader):
    """UI file loader."""
    def __init__(self) -> None:
        """UI file loader."""
        super().__init__()
        self._base_instance = None

    def createWidget(self, className: str, parent: QWidget | None = None, name: str = '') -> QWidget:
        """
        Create a widget.

        :param className: Class name
        :param parent: Parent
        :param name: Name
        :return: QWidget
        """
        if parent is None and self._base_instance is not None:
            return self._base_instance
        widget = super().createWidget(className, parent, name)
        if self._base_instance is not None and name:
            setattr(self._base_instance, name, widget)
        return widget

    def load_ui(self, ui_path: str | bytes | Path, base_instance=None) -> QWidget:
        """
        Load a UI file.

        :param ui_path: Path to a UI file in format ':/../file.ui'
        :param base_instance:
        :return: QWidget
        """
        self._base_instance = base_instance
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise RuntimeError(f'Cannot open UI file: {ui_path!r}')
        try:
            widget = self.load(ui_file)
            if base_instance is not None:
                QMetaObject.connectSlotsByName(base_instance)
            return widget
        finally:
            ui_file.close()
            self._base_instance = None
