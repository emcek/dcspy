import sys
import traceback
from functools import partial
from importlib import import_module
from logging import getLogger
from os import environ
from pathlib import Path
from platform import architecture, python_implementation, python_version, uname
from pprint import pformat
from shutil import copy, copytree, rmtree, unpack_archive
from tempfile import gettempdir
from threading import Event, Thread
from time import sleep
from typing import Callable, Dict, List, Optional, Union
from webbrowser import open_new_tab

from packaging import version
from pydantic_core import ValidationError
from PySide6 import __version__ as pyside6_ver
from PySide6.QtCore import QFile, QIODevice, QMetaObject, QObject, QRunnable, Qt, QThreadPool, Signal, SignalInstance, Slot
from PySide6.QtCore import __version__ as qt6_ver
from PySide6.QtGui import QAction, QActionGroup, QIcon, QPixmap, QShowEvent, QStandardItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QCompleter, QDialog, QDockWidget, QFileDialog, QLabel, QLineEdit, QMainWindow, QMenu,
                               QMessageBox, QProgressBar, QPushButton, QRadioButton, QSlider, QSpinBox, QStatusBar, QSystemTrayIcon, QTableWidget, QTabWidget,
                               QToolBar, QWidget)

from dcspy import default_yaml, qtgui_rc
from dcspy.models import (CTRL_LIST_SEPARATOR, DCS_BIOS_REPO_DIR, DCS_BIOS_VER_FILE, DCSPY_REPO_NAME, KEYBOARD_TYPES, ControlKeyData, DcspyConfigYaml,
                          FontsConfig, Gkey, GuiPlaneInputRequest, KeyboardModel, LcdButton, MsgBoxTypes, ReleaseInfo, SystemData)
from dcspy.starter import dcspy_run
from dcspy.utils import (CloneProgress, check_bios_ver, check_dcs_bios_entry, check_dcs_ver, check_github_repo, check_ver_at_github, collect_debug_data,
                         defaults_cfg, download_file, get_all_git_refs, get_inputs_for_plane, get_list_of_ctrls, get_plane_aliases, get_planes_list,
                         get_sha_for_current_git_ref, get_version_string, is_git_exec_present, is_git_object, load_yaml, proc_is_running, run_pip_command,
                         save_yaml)

_ = qtgui_rc  # prevent to remove import statement accidentally
__version__ = '3.0.0'
LOG = getLogger(__name__)


class DcsPyQtGui(QMainWindow):
    """PySide6 GUI for DCSpy."""

    def __init__(self, cfg_dict: Optional[DcspyConfigYaml] = None) -> None:
        """
        PySide6 GUI for DCSpy.

        :param cfg_dict: dict with configuration
        """
        super().__init__()
        UiLoader().loadUi(':/ui/ui/qtdcs.ui', self)
        self._find_children()
        self.threadpool = QThreadPool.globalInstance()
        LOG.debug(f'QThreadPool with {self.threadpool.maxThreadCount()} thread(s)')
        self.event = Event()
        self._done_event = Event()
        self.keyboard = KeyboardModel(name='', klass='', modes=0, gkeys=0, lcdkeys=(LcdButton.NONE,), lcd='mono')
        self.mono_font = {'large': 0, 'medium': 0, 'small': 0}
        self.color_font = {'large': 0, 'medium': 0, 'small': 0}
        self.current_row = -1
        self.current_col = -1
        self._completer_items = 0
        self._git_refs_count = 0
        self.plane_aliases = ['']
        self.ctrl_input: Dict[str, Dict[str, ControlKeyData]] = {}
        self.ctrl_list = ['']
        self.input_reqs: Dict[str, Dict[str, GuiPlaneInputRequest]] = {}
        self.git_exec = is_git_exec_present()
        self.l_bios = version.Version('0.0.0')
        self.r_bios = version.Version('0.0.0')
        self.systray = QSystemTrayIcon()
        self.traymenu = QMenu()
        self.config = cfg_dict
        if not cfg_dict:
            self.config = load_yaml(full_path=default_yaml)
        self.dw_gkeys.hide()
        self.dw_keyboard.hide()
        self.dw_keyboard.setFloating(True)
        self.bg_rb_input_iface = QButtonGroup(self)
        self._init_tray()
        self._init_combo_plane()
        self._init_menu_bar()
        self.apply_configuration(cfg=self.config)
        self._init_settings()
        self._init_keyboards()
        self._init_autosave()
        self._trigger_refresh_data()

        if self.cb_autoupdate_bios.isChecked():
            self._bios_check_clicked(silence=True)
        if self.cb_check_ver.isChecked():  # todo: clarify checking bios and dcspy in same way...
            data = self.fetch_system_data(silence=False)  # todo: maybe add silence
            status_ver = ''
            status_ver += f'Dcspy: {data.dcspy_ver} ' if self.config['check_ver'] else ''
            status_ver += f'BIOS: {data.bios_ver}' if self.config['check_bios'] else ''
            self.statusbar.showMessage(status_ver)
        if self.config.get('autostart', False):
            self._start_clicked()
        self.statusbar.showMessage(f'ver. {__version__}')

    def _init_tray(self) -> None:
        """Initialize of system tray icon."""
        self.systray.setIcon(QIcon(':/icons/img/dcspy_white.svg'))
        self.systray.setVisible(True)
        self.systray.setToolTip(f'DCSpy {__version__}')
        self.traymenu.addAction(self.a_dcspy_updates)
        self.traymenu.addAction(self.a_quit)
        self.systray.setContextMenu(self.traymenu)
        self.systray.activated.connect(self.activated)

    def _init_combo_plane(self) -> None:
        """Initialize of combo box for plane selector with completer."""
        try:
            plane_list = get_planes_list(bios_dir=Path(self.config['dcsbios']))
            completer = QCompleter(plane_list)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setMaxVisibleItems(self.config['completer_items'])
            completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
            self.combo_planes.addItems(plane_list)
            self.combo_planes.setEditable(True)
            self.combo_planes.setCompleter(completer)
            self.input_reqs = {plane: {} for plane in plane_list}
        except FileNotFoundError as exc:
            message = f'Folder not exists: \n{self.config["dcsbios"]}\n\nCheck DCS-BIOS path.\n\n{exc}'
            self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Get Planes List', message=message)

    def _init_settings(self) -> None:
        """Initialize of settings."""
        self.pb_dcsdir.clicked.connect(partial(self._run_file_dialog, for_load=True, for_dir=True, last_dir=lambda: 'C:\\', widget_name='le_dcsdir'))
        self.le_dcsdir.textChanged.connect(partial(self._is_dir_exists, widget_name='le_dcsdir'))
        self.pb_biosdir.clicked.connect(partial(self._run_file_dialog, for_load=True, for_dir=True, last_dir=lambda: 'C:\\', widget_name='le_biosdir'))
        self.le_biosdir.textChanged.connect(partial(self._is_dir_dcs_bios, widget_name='le_biosdir'))
        self.pb_collect_data.clicked.connect(self._collect_data_clicked)
        self.pb_start.clicked.connect(self._start_clicked)
        self.a_start.triggered.connect(self._start_clicked)
        self.pb_stop.clicked.connect(self._stop_clicked)
        self.a_stop.triggered.connect(self._stop_clicked)
        self.dw_gkeys.visibilityChanged.connect(partial(self._close_dock_widget, widget='gkeys'))
        self.dw_keyboard.visibilityChanged.connect(partial(self._close_dock_widget, widget='keyboard'))
        self.pb_dcspy_check.clicked.connect(self._dcspy_check_clicked)
        self.pb_bios_check.clicked.connect(self._bios_check_clicked)
        self.le_bios_live.textEdited.connect(self._is_git_object_exists)
        self.le_bios_live.returnPressed.connect(partial(self._bios_check_clicked, silence=False))
        self.cb_bios_live.toggled.connect(self._cb_bios_live_toggled)
        self.sp_completer.valueChanged.connect(self._set_find_value)
        self.tw_gkeys.currentCellChanged.connect(self._save_current_cell)
        self.pb_copy.clicked.connect(self._copy_cell_to_row)
        self.pb_save.clicked.connect(self._save_gkeys_cfg)
        self.combo_planes.currentIndexChanged.connect(self._load_table_gkeys)
        self.bg_rb_input_iface.addButton(self.rb_action)
        self.bg_rb_input_iface.addButton(self.rb_set_state)
        self.bg_rb_input_iface.addButton(self.rb_fixed_step_inc)
        self.bg_rb_input_iface.addButton(self.rb_fixed_step_dec)
        self.bg_rb_input_iface.addButton(self.rb_variable_step_plus)
        self.bg_rb_input_iface.addButton(self.rb_variable_step_minus)
        self.bg_rb_input_iface.addButton(self.rb_custom)
        self.bg_rb_input_iface.buttonClicked.connect(self._input_iface_changed)
        self.le_custom.editingFinished.connect(self._le_custom_text_edited)
        self.le_custom.returnPressed.connect(self._le_custom_text_edited)

    def _init_keyboards(self) -> None:
        """Initialize of keyboards."""
        for keyboard_type in KEYBOARD_TYPES:
            getattr(self, f'rb_{keyboard_type.lower()}').toggled.connect(partial(self._select_keyboard, keyboard_type))

    def _init_menu_bar(self) -> None:
        """Initialize of menubar."""
        self.a_reset_defaults.triggered.connect(self._reset_defaults_cfg)
        self.a_quit.triggered.connect(self.close)
        self.a_save_plane.triggered.connect(self._save_gkeys_cfg)
        self.a_show_toolbar.triggered.connect(self._show_toolbar)
        self.a_show_gkeys.triggered.connect(self._show_gkeys_dock)
        self.a_show_keyboard.triggered.connect(self._show_keyboard_dock)
        self.a_report_issue.triggered.connect(partial(open_new_tab, url='https://github.com/emcek/dcspy/issues'))
        self.a_discord.triggered.connect(partial(open_new_tab, url='https://discord.gg/SP5Yjx3'))
        self.a_about_dcspy.triggered.connect(AboutDialog(self).open)
        self.a_about_qt.triggered.connect(partial(self._show_message_box, kind_of=MsgBoxTypes.ABOUT_QT, title='About Qt'))
        self.a_dcspy_updates.triggered.connect(self._dcspy_check_clicked)
        self.a_bios_updates.triggered.connect(self._bios_check_clicked)

        toolbar_style = QActionGroup(self)
        toolbar_style.addAction(self.a_icons_only)
        toolbar_style.addAction(self.a_text_only)
        toolbar_style.addAction(self.a_text_beside)
        toolbar_style.addAction(self.a_text_under)

        self.a_icons_only.toggled.connect(lambda _: self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly))
        self.a_text_only.toggled.connect(lambda _: self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly))
        self.a_text_beside.toggled.connect(lambda _: self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon))
        self.a_text_under.toggled.connect(lambda _: self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon))

    def _init_autosave(self) -> None:
        """Initialize of autosave."""
        widget_dict = {
            'le_dcsdir': 'textChanged', 'le_biosdir': 'textChanged', 'le_font_name': 'textEdited', 'le_bios_live': 'textEdited',
            'hs_large_font': 'valueChanged', 'hs_medium_font': 'valueChanged', 'hs_small_font': 'valueChanged', 'sp_completer': 'valueChanged',
            'combo_planes': 'currentIndexChanged', 'toolbar': 'visibilityChanged', 'dw_gkeys': 'visibilityChanged',
            'a_icons_only': 'triggered', 'a_text_only': 'triggered', 'a_text_beside': 'triggered', 'a_text_under': 'triggered',
            'cb_autostart': 'toggled', 'cb_show_gui': 'toggled', 'cb_check_ver': 'toggled', 'cb_ded_font': 'toggled', 'cb_lcd_screenshot': 'toggled',
            'cb_verbose': 'toggled', 'cb_autoupdate_bios': 'toggled', 'cb_bios_live': 'toggled',
            'rb_g19': 'toggled', 'rb_g13': 'toggled', 'rb_g15v1': 'toggled', 'rb_g15v2': 'toggled', 'rb_g510': 'toggled',
        }
        for widget_name, trigger_method in widget_dict.items():
            getattr(getattr(self, widget_name), trigger_method).connect(self.save_configuration)

    def _trigger_refresh_data(self):
        """Refresh widgets states and regenerates data."""
        self._is_dir_exists(text=self.le_dcsdir.text(), widget_name='le_dcsdir')
        self._is_dir_dcs_bios(text=self.bios_path, widget_name='le_biosdir')
        if self.cb_bios_live.isChecked():
            self.le_bios_live.setEnabled(True)
            self._is_git_object_exists(text=self.le_bios_live.text())
        for keyboard_type in KEYBOARD_TYPES:
            keyboard = getattr(self, f'rb_{keyboard_type.lower()}')
            if keyboard.isChecked():
                self._select_keyboard(keyboard=keyboard_type, state=True)
                break

    def _set_find_value(self, value) -> None:
        """
        Refresh configuration of table and completer when visible items value changed.

        :param value: number of items visible
        """
        self._completer_items = value
        LOG.debug(f'Set number of results: {value}')
        self._load_table_gkeys()

    def _select_keyboard(self, keyboard: str, state: bool) -> None:
        """
        Triggered when new keyboard is selected.

        Based of current selected keyboard:
        * Add correct numbers of rows and columns
        * enable DED font checkbox
        * updates font sliders (range and values)
        * update dock with image of keyboard

        :param keyboard: name
        :param state: of radio button
        """
        if state:
            for mode_col in range(self.keyboard.modes):
                self.tw_gkeys.removeColumn(mode_col)
            for gkey_row in range(self.keyboard.gkeys + len(self.keyboard.lcdkeys)):
                self.tw_gkeys.removeRow(gkey_row)
            self.keyboard = getattr(import_module('dcspy.models'), f'Model{keyboard}')
            LOG.debug(f'Select: {self.keyboard}')
            self._set_ded_font_and_font_sliders()
            self._update_dock()
            self._load_table_gkeys()

    def _set_ded_font_and_font_sliders(self) -> None:
        """Enable DED font checkbox and updates font sliders."""
        if self.keyboard.lcd == 'color':
            self.cb_ded_font.setEnabled(True)
            minimum = 15
            maximum = 40
        else:
            self.cb_ded_font.setEnabled(False)
            minimum = 7
            maximum = 20

        for name in ['large', 'medium', 'small']:
            hs: QSlider = getattr(self, f'hs_{name}_font')
            try:
                hs.valueChanged.disconnect()
            except RuntimeError:
                pass
            hs.setMinimum(minimum)
            hs.setMaximum(maximum)
            hs.valueChanged.connect(partial(self._set_label_and_hs_value, name=name))
            hs.valueChanged.connect(self.save_configuration)
            hs.setValue(getattr(self, f'{self.keyboard.lcd}_font')[name])

    def _set_label_and_hs_value(self, value, name) -> None:
        """
        Set internal field for current value of slider and update label.

        :param value: of slider
        :param name: of slider
        """
        getattr(self, f'{self.keyboard.lcd}_font')[name] = value
        getattr(self, f'l_{name}').setText(str(value))

    def _update_dock(self) -> None:
        """Update dock with image of keyboard."""
        self.l_keyboard.setPixmap(QPixmap(f':/img/img/{self.keyboard.klass}device.png'))

    def _collect_data_clicked(self) -> None:
        """Collect data for troubleshooting and ask user where to save."""
        zip_file = collect_debug_data()
        try:
            dst_dir = str(Path(environ['USERPROFILE']) / 'Desktop')
        except KeyError:
            dst_dir = 'C:\\'
        directory = self._run_file_dialog(for_load=True, for_dir=True, last_dir=lambda: dst_dir)
        try:
            destination = Path(directory) / zip_file.name
            copy(zip_file, destination)
            LOG.debug(f'Save debug file: {destination}')
        except PermissionError as err:
            LOG.debug(f'Error: {err}, Collected data: {zip_file}')
            self._show_message_box(kind_of=MsgBoxTypes.WARNING, title=err.args[1], message=f'Can not save file:\n{err.filename}')

    def _is_dir_exists(self, text: str, widget_name: str) -> bool:
        """
        Check if directory exists.

        :param text: contents of text field
        :param widget_name: widget name
        :return: True if directory exists, False otherwise.
        """
        dir_exists = Path(text).is_dir()
        LOG.debug(f'Path: {text} for {widget_name} exists: {dir_exists}')
        if dir_exists:
            getattr(self, widget_name).setStyleSheet('')
            return True
        getattr(self, widget_name).setStyleSheet('color: red;')
        return False

    def _is_dir_dcs_bios(self, text: Union[Path, str], widget_name: str) -> bool:
        """
        Check if directory is valid DCS-BIOS installation.

        :param text: contents of text field
        :param widget_name: widget name
        :return: True if valid BIOS directory, False otherwise.
        """
        text = Path(text)
        bios_lua = text / 'BIOS.lua'
        metadata_json = text / 'doc' / 'json' / 'MetadataStart.json'
        if all([text.is_dir(), bios_lua.is_file(), metadata_json.is_file()]):
            getattr(self, widget_name).setStyleSheet('')
            return True
        getattr(self, widget_name).setStyleSheet('color: red;')
        return False

    # <=><=><=><=><=><=><=><=><=><=><=> g-keys tab <=><=><=><=><=><=><=><=><=><=><=>
    def _load_table_gkeys(self) -> None:
        """Initialize table with cockpit data."""
        if self._rebuild_ctrl_input_table_not_needed(plane_name=self.current_plane):
            return
        self.tw_gkeys.setColumnCount(self.keyboard.modes)
        for mode_col in range(self.keyboard.modes):
            self.tw_gkeys.setColumnWidth(mode_col, 200)
        no_lcd_keys = len(self.keyboard.lcdkeys)
        no_g_keys = self.keyboard.gkeys
        self.tw_gkeys.setRowCount(no_g_keys + no_lcd_keys)
        labels_g_key = [f'G{i}' for i in range(1, no_g_keys + 1)]
        labels_lcd_key = [lcd_key.name for lcd_key in self.keyboard.lcdkeys]
        self.tw_gkeys.setVerticalHeaderLabels(labels_g_key + labels_lcd_key)
        self.tw_gkeys.setHorizontalHeaderLabels([f'M{i}' for i in range(1, self.keyboard.modes + 1)])
        plane_keys = load_yaml(full_path=default_yaml.parent / f'{self.current_plane}.yaml')
        LOG.debug(f'Load {self.current_plane}:\n{pformat(plane_keys)}')
        self.input_reqs[self.current_plane] = GuiPlaneInputRequest.from_plane_gkeys(plane_gkeys=plane_keys)

        ctrl_list_without_sep = [item for item in self.ctrl_list if item and CTRL_LIST_SEPARATOR not in item]
        for row in range(0, no_g_keys + no_lcd_keys):
            for col in range(0, self.keyboard.modes):
                self._make_combo_with_completer_at(row, col, ctrl_list_without_sep)

    def _make_combo_with_completer_at(self, row: int, col: int, ctrl_list_no_sep: List[str]) -> None:
        """
        Make QComboBox widget with completer with list of strings in cell in row and column.

        :param row: current row
        :param col: current column
        :param ctrl_list_no_sep: list of control inputs without separator
        """
        key_name = self._get_key_name_from_row_col(row, col)
        if col == 0 or row < self.keyboard.gkeys:
            completer = QCompleter(ctrl_list_no_sep)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setMaxVisibleItems(self._completer_items)
            completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)

            combo = QComboBox()
            combo.setEditable(True)
            combo.addItems(self.ctrl_list)
            combo.setCompleter(completer)
            self._disable_items_with(text=CTRL_LIST_SEPARATOR, widget=combo)
            self.tw_gkeys.setCellWidget(row, col, combo)
            try:
                identifier = self.input_reqs[self.current_plane][key_name].identifier
            except KeyError:
                identifier = ''
            combo.setCurrentText(identifier)
            combo.editTextChanged.connect(partial(self._cell_ctrl_content_changed, widget=combo, row=row, col=col))
        else:
            combo = QComboBox()
            combo.setDisabled(True)
            self.tw_gkeys.setCellWidget(row, col, combo)
        combo.setStyleSheet(self._get_style_for_combobox(key_name, 'black'))

    def _rebuild_ctrl_input_table_not_needed(self, plane_name: str) -> bool:
        """
        Detect when new plane is selected.

        Compare old and new plane's aliases and reload when needed:
         - regenerate control inputs for new plane
         - construct list of controls for every cell in table
         - update aliases

         In case of problems:
          - pop-up with details
          - back to previous plane or first in list

        :param plane_name: BIOS plane name
        :return:
        """
        try:
            plane_aliases = get_plane_aliases(plane=plane_name, bios_dir=self.bios_path)
        except FileNotFoundError as exc:
            message = f'Folder not exists:\n{self.bios_path}\n\nCheck DCS-BIOS path.\n\n{exc}'
            self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Get Plane Aliases', message=message)
            return False

        if self.plane_aliases != plane_aliases[plane_name]:
            try:
                self.ctrl_input = get_inputs_for_plane(plane=plane_name, bios_dir=self.bios_path)
                self.plane_aliases = plane_aliases[plane_name]
                LOG.debug(f'Get input list: {plane_name} {plane_aliases}, old: {self.plane_aliases}')
                self.ctrl_list = get_list_of_ctrls(inputs=self.ctrl_input)
                return False
            except ValidationError as exc:
                LOG.debug(f'{plane_name}: {plane_aliases}\nValidation errors: {exc}')
                self._show_custom_msg_box(
                    kind_of=QMessageBox.Icon.Warning,
                    title=f'Warning with {plane_name}',
                    text=f'Can not read info-model of {plane_name}. Regenerate\ninfo-model might help. Please follow instruction: ',
                    info_txt=f'1. Stop DCSpy client (if running)\n2. Start any Instant Action for {plane_name}\n3. Click Fly\n4. Try again',
                    detail_txt=f'{exc.errors()}'
                )
                if len(self.plane_aliases) > 1:
                    self.combo_planes.setCurrentText(self.plane_aliases[1])
                else:
                    self.combo_planes.setCurrentIndex(0)
                return True

    def _cell_ctrl_content_changed(self, text: str, widget: QComboBox, row: int, col: int) -> None:
        """
        Check if control input exists in current plane control list.

        * set details for current control input
        * set styling
        * add description tooltip
        * save control request for current plane

        :param text: current text
        :param widget: combo instance
        :param row: current row
        :param col: current column
        """
        self.l_category.setText('')
        self.l_description.setText('')
        self.l_identifier.setText('')
        self.l_range.setText('')
        widget.setToolTip('')
        key_name = self._get_key_name_from_row_col(row, col)
        widget.setStyleSheet(self._get_style_for_combobox(key_name, 'red'))
        if text in self.ctrl_list and CTRL_LIST_SEPARATOR not in text:
            section = self._find_section_name(ctrl_name=text)
            ctrl_key = self.ctrl_input[section][text]
            widget.setToolTip(ctrl_key.description)
            widget.setStyleSheet(self._get_style_for_combobox(key_name, 'black'))
            self.l_category.setText(f'Category: {section}')
            self.l_description.setText(f'Description: {ctrl_key.description}')
            self.l_identifier.setText(f'Identifier: {text}')
            self.l_range.setText(f'Range: 0 - {ctrl_key.max_value}')
            self._enable_checked_iface_radio_button(ctrl_key=ctrl_key)
            self._checked_iface_rb_for_identifier(key_name=key_name)
            input_iface_name = self.bg_rb_input_iface.checkedButton().objectName()
            self.input_reqs[self.current_plane][key_name] = GuiPlaneInputRequest.from_control_key(ctrl_key=ctrl_key, rb_iface=input_iface_name,
                                                                                                  custom_value=self.le_custom.text())
        elif text == '':
            widget.setStyleSheet(self._get_style_for_combobox(key_name, 'black'))
            self.input_reqs[self.current_plane][key_name] = GuiPlaneInputRequest.make_empty()  # maybe del
            for rb_widget in self.bg_rb_input_iface.buttons():
                rb_widget.setEnabled(False)
                rb_widget.setChecked(False)

    def _get_key_name_from_row_col(self, row: int, col: int) -> str:
        """
        Get key name from row and column.

        It depends of location in table:
        * G-Key at the tom and LCD Keys at the bottom.
        * type of Keyboard number of G-Keys and LCD Keys are different

        :param row: current row
        :param row: current column
        :return: string name of key
        """
        if row <= self.keyboard.gkeys - 1:
            key = Gkey.name(row, col)
        else:
            key = self.keyboard.lcdkeys[row - self.keyboard.gkeys].name
        return key

    def _find_section_name(self, ctrl_name: str) -> str:
        """
        Find section name of control input name.

        :param ctrl_name: input name of controller.
        :return: section name as string
        """
        idx = self.ctrl_list.index(ctrl_name)
        for element in reversed(self.ctrl_list[:idx]):
            if element.startswith(CTRL_LIST_SEPARATOR):
                return element.strip(f' {CTRL_LIST_SEPARATOR}')
        return ''

    def _enable_checked_iface_radio_button(self, ctrl_key: ControlKeyData) -> None:
        """
        Enable and checked default input interface radio buttons for current identifier.

        :param ctrl_key: ControlKeyData instance
        """
        for widget in self.bg_rb_input_iface.buttons():
            widget.setEnabled(False)
        if ctrl_key.has_variable_step:
            self.rb_variable_step_plus.setEnabled(True)
            self.rb_variable_step_minus.setEnabled(True)
            self.rb_variable_step_plus.setChecked(True)
        if ctrl_key.has_set_state:
            self.rb_set_state.setEnabled(True)
            self.rb_set_state.setChecked(True)
        if ctrl_key.input_len == 2 and ctrl_key.has_variable_step and ctrl_key.has_set_state:
            self.rb_variable_step_plus.setChecked(True)
        if ctrl_key.has_fixed_step:
            self.rb_fixed_step_inc.setEnabled(True)
            self.rb_fixed_step_dec.setEnabled(True)
            self.rb_fixed_step_inc.setChecked(True)
        if ctrl_key.has_action:
            self.rb_action.setEnabled(True)
            self.rb_action.setChecked(True)
        self.rb_custom.setEnabled(True)

    def _checked_iface_rb_for_identifier(self, key_name: str) -> None:
        """
        Enable input interfaces for current control input identifier.

        :param key_name: G-Key or LCD Key as string
        """
        try:
            widget_iface = self.input_reqs[self.current_plane][key_name].widget_iface
            self.le_custom.setText('')
            if widget_iface == 'rb_custom':
                self.le_custom.setText(' '.join(self.input_reqs[self.current_plane][key_name].request.split(' ')[2:]))
            getattr(self, widget_iface).setChecked(True)
        except (KeyError, AttributeError):
            pass

    @staticmethod
    def _disable_items_with(text: str, widget: QComboBox) -> None:
        """
        Disable items in ComboBox, which shouldn't be selected.

        :param widget: QComboBox instance
        """
        model = widget.model()
        for i in range(0, widget.count()):
            item: QStandardItem = model.item(i)
            if text in item.text():
                item.setFlags(Qt.ItemFlag.NoItemFlags)

    def _save_gkeys_cfg(self) -> None:
        """Save G-Keys configuration for current plane."""
        plane_cfg_yaml = {g_key: value.request for g_key, value in self.input_reqs[self.current_plane].items() if value.request}
        LOG.debug(f'Save {self.current_plane}:\n{pformat(plane_cfg_yaml)}')
        save_yaml(data=plane_cfg_yaml, full_path=default_yaml.parent / f'{self.current_plane}.yaml')

    def _save_current_cell(self, currentRow: int, currentColumn: int, previousRow: int, previousColumn: int) -> None:
        """
        Save current cell of TableWidget.

        :param currentRow:
        :param currentColumn:
        :param previousRow:
        :param previousColumn:
        """
        self.current_row = currentRow
        self.current_col = currentColumn
        cell_combo = self.tw_gkeys.cellWidget(currentRow, currentColumn)
        self._cell_ctrl_content_changed(text=cell_combo.currentText(), widget=cell_combo, row=currentRow, col=currentColumn)

    def _input_iface_changed(self, button: QRadioButton) -> None:
        """
        Triggered when new input interface is selected.

        :param button: currently checked input interface radio button
        """
        row = self.current_row
        col = self.current_col
        current_text = self.tw_gkeys.cellWidget(row, col).currentText()
        if current_text in self.ctrl_list and CTRL_LIST_SEPARATOR not in current_text:
            section = self._find_section_name(ctrl_name=current_text)
            ctrl_key = self.ctrl_input[section][current_text]
            key_name = self._get_key_name_from_row_col(row, col)
            self.input_reqs[self.current_plane][key_name] = GuiPlaneInputRequest.from_control_key(ctrl_key=ctrl_key, rb_iface=button.objectName())

    def _le_custom_text_edited(self) -> None:
        """Triggered when text is changed and user press enter or widget lose focus."""
        input_iface_name = self.bg_rb_input_iface.checkedButton().objectName()
        current_cell_text = self.tw_gkeys.cellWidget(self.current_row, self.current_col).currentText()
        section = self._find_section_name(ctrl_name=current_cell_text)
        key_name = self._get_key_name_from_row_col(self.current_row, self.current_col)
        ctrl_key = self.ctrl_input[section][current_cell_text]
        self.input_reqs[self.current_plane][key_name] = GuiPlaneInputRequest.from_control_key(ctrl_key=ctrl_key, rb_iface=input_iface_name,
                                                                                              custom_value=self.le_custom.text())

    def _copy_cell_to_row(self) -> None:
        """Copy content of current cell to whole row."""
        current_index = self.tw_gkeys.cellWidget(self.current_row, self.current_col).currentIndex()
        for col in set(range(self.keyboard.modes)) - {self.current_col}:
            self.tw_gkeys.cellWidget(self.current_row, col).setCurrentIndex(current_index)

    # <=><=><=><=><=><=><=><=><=><=><=> dcs-bios tab <=><=><=><=><=><=><=><=><=><=><=>
    def _is_git_object_exists(self, text: str) -> bool:
        """
        Check if entered git object exists.

        :param text: Git reference
        :return: True if git object exists, False otherwise.
        """
        if self.cb_bios_live.isChecked():
            git_ref = is_git_object(repo_dir=DCS_BIOS_REPO_DIR, git_obj=text)
            LOG.debug(f'Git reference: {text} in {DCS_BIOS_REPO_DIR} exists: {git_ref}')
            if git_ref:
                self.le_bios_live.setStyleSheet('')
                self._set_completer_for_git_ref()
                return True
            self.le_bios_live.setStyleSheet('color: red;')
            return False

    def _get_bios_full_version(self, silence=True) -> str:
        """
        Get full SHA and git details DCS-BIOS version as string.

        :param silence: perform action with silence
        :return: full BIOS version
        """
        sha_commit = ''
        if self.git_exec and self.cb_bios_live.isChecked():
            try:
                sha_commit = check_github_repo(git_ref=self.le_bios_live.text(), update=False)
            except Exception as exc:
                LOG.debug(f'{exc}')
                if not silence:
                    self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Error', message=f'\n\n{exc}\n\nTry remove directory and restart DCSpy.')
        return sha_commit

    def _cb_bios_live_toggled(self, state: bool) -> None:
        """When Live BIOS checkbox is toggled."""
        if state:
            self.le_bios_live.setEnabled(True)
            self._is_git_object_exists(text=self.le_bios_live.text())
        else:
            self.le_bios_live.setEnabled(False)
            self.le_bios_live.setStyleSheet('')
        self._bios_check_clicked(silence=False)

    def _set_completer_for_git_ref(self) -> None:
        """Setups completer for Git references of DCS-BIOS git repo."""
        if not self._git_refs_count:
            git_refs = get_all_git_refs(repo_dir=DCS_BIOS_REPO_DIR)
            self._git_refs_count = len(git_refs)
            completer = QCompleter(git_refs)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
            self.le_bios_live.setCompleter(completer)

    # <=><=><=><=><=><=><=><=><=><=><=> check dcspy updates <=><=><=><=><=><=><=><=><=><=><=>
    def _dcspy_check_clicked(self) -> None:
        """Check version of DCSpy and show message box."""
        ver_string = get_version_string(repo=DCSPY_REPO_NAME, current_ver=__version__, check=True)
        self.statusbar.showMessage(ver_string)
        if 'update!' in ver_string:
            self.systray.showMessage('DCSpy', f'New version: {__version__}', QIcon(':/icons/img/edit-download.svg'))
            self._download_new_release()
        elif 'latest' in ver_string:
            self._show_message_box(kind_of=MsgBoxTypes.INFO, title='No updates', message='You are running latest version')
        elif 'failed' in ver_string:
            self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Warning', message='Unable to check DCSpy version online')

    def _download_new_release(self) -> None:
        """Download new release if running PyInstaller version or show instruction when running Pip version."""
        if getattr(sys, 'frozen', False):
            rel_info = check_ver_at_github(repo='emcek/dcspy', current_ver=__version__, extension='.exe')
            directory = self._run_file_dialog(for_load=True, for_dir=True, last_dir=lambda: str(Path.cwd()))
            try:
                destination = Path(directory) / rel_info.asset_file
                download_file(url=rel_info.dl_url, save_path=destination)
                LOG.debug(f'Save new release: {destination}')
            except PermissionError as exc:
                self._show_message_box(kind_of=MsgBoxTypes.WARNING, title=exc.args[1], message=f'Can not save file:\n{exc.filename}')
        else:
            rc, err, out = run_pip_command('install --upgrade dcspy')
            if not rc:
                self._show_message_box(kind_of=MsgBoxTypes.INFO, title='Pip Install', message=out.split('\r\n')[-2])
            else:
                self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Pip Install', message=err)

    # <=><=><=><=><=><=><=><=><=><=><=> check bios updates <=><=><=><=><=><=><=><=><=><=><=>
    def _bios_check_clicked(self, silence=False) -> None:
        """
        Do real update Git or stable DCS-BIOS version.

        :param silence: perform action with silence
        """
        if not self._check_dcs_bios_path():
            return

        if self.cb_bios_live.isChecked():
            clone_worker = GitCloneWorker(git_ref=self.le_bios_live.text(), bios_path=self.bios_path, to_path=DCS_BIOS_REPO_DIR, silence=silence)
            signal_handlers = {
                'progress': self._progress_by_abs_value,
                'stage': self.statusbar.showMessage,
                'error': self._error_during_bios_update,
                'result': self._clone_bios_completed,
            }
            for signal, handler in signal_handlers.items():
                getattr(clone_worker.signals, signal).connect(handler)
            self.threadpool.start(clone_worker)
        else:
            self._check_bios_release(silence=silence)

    def _check_dcs_bios_path(self) -> bool:
        """
        Check if DCS-BIOS path fulfill two conditions.

        - path is not empty
        - drive letter exists in system

        If those two are met return True, False otherwise.

        :return: True if path to DCS-BIOS is correct
        """
        result = True
        if self._is_dir_dcs_bios(text=self.bios_path, widget_name='le_biosdir'):
            drive_letter = self.bios_path.parts[0]
            if not Path(drive_letter).exists():
                self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Warning', message=f'Wrong drive: {drive_letter}\n\nCheck DCS-BIOS path.')
                result = False
        else:
            reply = QMessageBox.question(self, 'Install DCS-BIOS', f'There is no DCS-BIOS installed at:\n{self.bios_path}\n\nDo you want install?',
                                         defaultButton=QMessageBox.StandardButton.Yes)
            result = bool(reply == QMessageBox.StandardButton.Yes)
        return result

    def _error_during_bios_update(self, exc_tuple) -> None:
        """
        Show message box with error details.

        :param exc_tuple: Exception tuple
        """
        exc_type, exc_val, exc_tb = exc_tuple
        LOG.debug(exc_tb)
        self._show_custom_msg_box(kind_of=QMessageBox.Icon.Critical, title='Error', text=str(exc_type), detail_txt=str(exc_val),
                                  info_txt=f'Try remove directory:\n{DCS_BIOS_REPO_DIR}\nand restart DCSpy.')
        LOG.debug(f'Can not update BIOS: {exc_type}')

    def _clone_bios_completed(self, result) -> None:
        """
        Show message box with installation details.

        :param result:
        """
        sha, silence = result
        local_bios = self._check_local_bios()
        LOG.info(f'Git DCS-BIOS: {sha} ver: {local_bios}')
        install_result = self._handling_export_lua(temp_dir=DCS_BIOS_REPO_DIR / 'Scripts')
        install_result = f'{install_result}\n\nUsing Git/Live version.'
        self.statusbar.showMessage(sha)
        self._is_git_object_exists(text=self.le_bios_live.text())
        self._is_dir_dcs_bios(text=self.bios_path, widget_name='le_biosdir')
        self._update_bios_ver_file()
        if not silence:
            self._show_message_box(kind_of=MsgBoxTypes.INFO, title=f'Updated {self.l_bios}', message=install_result)
        self.progressbar.setValue(0)

    def _update_bios_ver_file(self):
        """Update DCS-BIOS version file with current SHA."""
        hex_sha = get_sha_for_current_git_ref(git_ref=self.le_bios_live.text(), repo_dir=DCS_BIOS_REPO_DIR)
        with open(file=self.bios_path / DCS_BIOS_VER_FILE, mode='w+') as bios_live_ver_file:
            bios_live_ver_file.write(hex_sha)

    def _check_bios_release(self, silence=False) -> None:
        """
        Check release version and configuration of DCS-BIOS.

        :param silence: perform action with silence
        """
        self._check_local_bios()
        remote_bios_info = self._check_remote_bios()
        self.statusbar.showMessage(f'Local BIOS: {self.l_bios} | Remote BIOS: {self.r_bios}')
        correct_local_bios_ver = all([isinstance(self.l_bios, version.Version), any([self.l_bios.major, self.l_bios.minor, self.l_bios.micro])])
        correct_remote_bios_ver = all([isinstance(self.r_bios, version.Version), remote_bios_info.dl_url, remote_bios_info.asset_file])
        dcs_runs = proc_is_running(name='DCS.exe')

        if silence and correct_remote_bios_ver and not remote_bios_info.latest:
            self._update_release_bios(rel_info=remote_bios_info)
        elif not silence and correct_remote_bios_ver:
            self._ask_to_update(rel_info=remote_bios_info)
        elif not all([silence, correct_remote_bios_ver]):
            msg = self._get_problem_desc(correct_local_bios_ver, correct_remote_bios_ver, bool(dcs_runs))
            msg = f'{msg}\n\nUsing stable release version.'
            self._show_message_box(kind_of=MsgBoxTypes.INFO, title='Update', message=msg)

    def _get_problem_desc(self, local_bios: bool, remote_bios: bool, dcs: bool) -> str:
        """
        Describe issues with DCS-BIOS update.

        :param local_bios: local BIOS version
        :param remote_bios: remote BIOS version
        :param dcs: DCS is running
        :return: description as string
        """
        dcs_chk = '\u2716 DCS' if dcs else '\u2714 DCS'
        dcs_sta = 'running' if dcs else 'not running'
        dcs_note = '\n     Be sure stay on Main menu.' if dcs else ''
        lbios_chk = '\u2714 Local' if local_bios else '\u2716 Local'
        lbios_note = '' if local_bios else '\n     Check "dcsbios" path in config'
        rbios_chk = '\u2714 Remote' if remote_bios else '\u2716 Remote'
        rbios_note = '' if remote_bios else '\n     Check internet connection.'

        return f'{dcs_chk}: {dcs_sta}{dcs_note}\n' \
               f'{lbios_chk} Bios ver: {self.l_bios}{lbios_note}\n' \
               f'{rbios_chk} Bios ver: {self.r_bios}{rbios_note}'

    def _check_local_bios(self) -> ReleaseInfo:
        """
        Check version of local BIOS.

        :return: release description info
        """
        result = check_bios_ver(bios_path=self.bios_path)
        self.l_bios = result.ver
        return result

    def _check_remote_bios(self) -> ReleaseInfo:
        """
        Check version of remote BIOS.

        :return: release description info
        """
        release_info = check_ver_at_github(repo='DCS-Skunkworks/dcs-bios', current_ver=str(self.l_bios), extension='.zip')
        self.r_bios = release_info.ver
        return release_info

    def _ask_to_update(self, rel_info: ReleaseInfo) -> None:
        """
        Ask user if update BIOS or not.

        :param rel_info: remote release information
        """
        msg_txt = f'You are running {self.l_bios} version.\n\n' \
                  f'Would you like to download\n' \
                  f'stable release:\n\n{rel_info.asset_file}\n\n' \
                  f'and overwrite update?'
        if not rel_info.latest:
            msg_txt = f'You are running {self.l_bios} version.\n' \
                      f'New version {rel_info.ver} available.\n' \
                      f'Released: {rel_info.published}\n\n' \
                      f'Would you like to update?'
        reply = QMessageBox.question(self, 'Update DCS-BIOS', msg_txt, defaultButton=QMessageBox.StandardButton.Yes)
        if reply == QMessageBox.StandardButton.Yes:
            self._update_release_bios(rel_info=rel_info)

    def _update_release_bios(self, rel_info: ReleaseInfo) -> None:
        """
        Perform update of release version of BIOS and check configuration.

        :param rel_info: remote release information
        """
        tmp_dir = Path(gettempdir())
        local_zip = tmp_dir / rel_info.asset_file
        download_file(url=rel_info.dl_url, save_path=local_zip)
        LOG.debug(f'Remove DCS-BIOS from: {tmp_dir} ')
        rmtree(path=tmp_dir / 'DCS-BIOS', ignore_errors=True)
        LOG.debug(f'Unpack file: {local_zip} ')
        unpack_archive(filename=local_zip, extract_dir=tmp_dir)
        LOG.debug(f'Remove: {self.bios_path} ')
        rmtree(path=self.bios_path, ignore_errors=True)
        LOG.debug(f'Copy DCS-BIOS to: {self.bios_path} ')
        copytree(src=tmp_dir / 'DCS-BIOS', dst=self.bios_path)
        install_result = self._handling_export_lua(tmp_dir)
        if 'github' in install_result:
            reply = QMessageBox.question(self, 'Open browser', install_result, defaultButton=QMessageBox.StandardButton.Yes)
            if reply == QMessageBox.StandardButton.Yes:
                open_new_tab(r'https://github.com/DCS-Skunkworks/DCSFlightpanels/wiki/Installation')
        else:
            local_bios = self._check_local_bios()
            self.statusbar.showMessage(f'Local BIOS: {local_bios.ver} | Remote BIOS: {self.r_bios}')
            install_result = f'{install_result}\n\nUsing stable release version.'
            self._is_dir_dcs_bios(text=self.bios_path, widget_name='le_biosdir')
            self._show_message_box(kind_of=MsgBoxTypes.INFO, title=f'Updated {local_bios.ver}', message=install_result)

    def _handling_export_lua(self, temp_dir: Path) -> str:
        """
        Check if Export.lua file exist and its content.

        If not copy Export.lua from DCS-BIOS installation archive.

        :param temp_dir: directory with DCS-BIOS archive
        :return: result of checks
        """
        result = 'Installation Success. Done.'
        lua_dst_path = self.bios_path.parent
        lua = 'Export.lua'
        try:
            with open(file=lua_dst_path / lua, encoding='utf-8') as lua_dst:
                lua_dst_data = lua_dst.read()
        except FileNotFoundError as err:
            LOG.debug(f'{type(err).__name__}: {err.filename}')
            copy(src=temp_dir / lua, dst=lua_dst_path)
            LOG.debug(f'Copy Export.lua from: {temp_dir} to {lua_dst_path} ')
        else:
            result += check_dcs_bios_entry(lua_dst_data, lua_dst_path, temp_dir)
        return result

    # <=><=><=><=><=><=><=><=><=><=><=> start/stop <=><=><=><=><=><=><=><=><=><=><=>
    def _stop_clicked(self) -> None:
        """Set event to stop DCSpy."""
        self.run_in_background(job=partial(self._fake_progress, total_time=0.3),
                               signal_handlers={'progress': self._progress_by_abs_value})
        for rb_key in [self.rb_g13, self.rb_g15v1, self.rb_g15v2, self.rb_g19, self.rb_g510]:
            if not rb_key.isChecked():
                rb_key.setEnabled(True)
        self.statusbar.showMessage('Start again or close DCSpy')
        self.pb_start.setEnabled(True)
        self.a_start.setEnabled(True)
        self.pb_stop.setEnabled(False)
        self.a_stop.setEnabled(False)
        self.le_dcsdir.setEnabled(True)
        self.le_biosdir.setEnabled(True)
        self.hs_small_font.setEnabled(True)
        self.hs_medium_font.setEnabled(True)
        self.hs_large_font.setEnabled(True)
        self.le_font_name.setEnabled(True)
        if self.rb_g19.isChecked():
            self.cb_ded_font.setEnabled(True)
        self.l_large.setEnabled(True)
        self.l_medium.setEnabled(True)
        self.l_small.setEnabled(True)
        self.event_set()

    def _start_clicked(self) -> None:
        """Run real application in thread."""
        LOG.debug(f'Local DCS-BIOS version: {self._check_local_bios().ver}')
        self.run_in_background(job=partial(self._fake_progress, total_time=0.5),
                               signal_handlers={'progress': self._progress_by_abs_value})
        for rb_key in [self.rb_g13, self.rb_g15v1, self.rb_g15v2, self.rb_g19, self.rb_g510]:
            if not rb_key.isChecked():
                rb_key.setEnabled(False)
        fonts_cfg = FontsConfig(name=self.le_font_name.text(), **getattr(self, f'{self.keyboard.lcd}_font'))
        app_params = {'lcd_type': self.keyboard.klass, 'event': self.event, 'fonts_cfg': fonts_cfg}
        app_thread = Thread(target=dcspy_run, kwargs=app_params)
        app_thread.name = 'dcspy-app'
        LOG.debug(f'Starting thread {app_thread} for: {app_params}')
        self.pb_start.setEnabled(False)
        self.a_start.setEnabled(False)
        self.pb_stop.setEnabled(True)
        self.a_stop.setEnabled(True)
        self.le_dcsdir.setEnabled(False)
        self.le_biosdir.setEnabled(False)
        self.hs_small_font.setEnabled(False)
        self.hs_medium_font.setEnabled(False)
        self.hs_large_font.setEnabled(False)
        self.le_font_name.setEnabled(False)
        self.cb_ded_font.setEnabled(False)
        self.l_large.setEnabled(False)
        self.l_medium.setEnabled(False)
        self.l_small.setEnabled(False)
        app_thread.start()
        alive = 'working' if app_thread.is_alive() else 'not working'
        self.statusbar.showMessage(f'DCSpy client: {alive}')

    # <=><=><=><=><=><=><=><=><=><=><=> configuration <=><=><=><=><=><=><=><=><=><=><=>
    def apply_configuration(self, cfg: dict) -> None:
        """
        Apply configuration to GUI widgets.

        :param cfg: dictionary with configuration
        """
        icon_map = {0: 'a_icons_only', 1: 'a_text_only', 2: 'a_text_beside', 3: 'a_text_under'}

        self.cb_autostart.setChecked(cfg['autostart'])
        self.cb_show_gui.setChecked(cfg['show_gui'])
        self.cb_lcd_screenshot.setChecked(cfg['save_lcd'])
        self.cb_check_ver.setChecked(cfg['check_ver'])
        self.cb_verbose.setChecked(cfg['verbose'])
        self.cb_ded_font.setChecked(cfg['f16_ded_font'])
        self.cb_autoupdate_bios.setChecked(cfg['check_bios'])
        self.le_font_name.setText(cfg['font_name'])
        self.sp_completer.setValue(cfg['completer_items'])
        self._completer_items = cfg['completer_items']
        self.combo_planes.setCurrentText(cfg['current_plane'])
        self.mono_font = {'large': cfg['font_mono_l'], 'medium': cfg['font_mono_m'], 'small': cfg['font_mono_s']}
        self.color_font = {'large': cfg['font_color_l'], 'medium': cfg['font_color_m'], 'small': cfg['font_color_s']}
        getattr(self, f'rb_{cfg["keyboard"].lower().replace(" ", "")}').toggle()
        self.le_dcsdir.setText(cfg['dcs'])
        self.le_biosdir.setText(cfg['dcsbios'])
        self.le_bios_live.setText(cfg['git_bios_ref'])
        self.cb_bios_live.setChecked(cfg['git_bios'])
        self.addDockWidget(Qt.DockWidgetArea(int(cfg['gkeys_area'])), self.dw_gkeys)
        self.dw_gkeys.setFloating(bool(cfg['gkeys_float']))
        self.addToolBar(Qt.ToolBarArea(int(cfg['toolbar_area'])), self.toolbar)
        getattr(self, icon_map[cfg['toolbar_style']]).setChecked(True)

    def save_configuration(self) -> None:
        """Save configuration from GUI."""
        cfg = {
            'api_ver': __version__,
            'keyboard': self.keyboard.name,
            'autostart': self.cb_autostart.isChecked(),
            'show_gui': self.cb_show_gui.isChecked(),
            'save_lcd': self.cb_lcd_screenshot.isChecked(),
            'check_ver': self.cb_check_ver.isChecked(),
            'check_bios': self.cb_autoupdate_bios.isChecked(),
            'verbose': self.cb_verbose.isChecked(),
            'f16_ded_font': self.cb_ded_font.isChecked(),
            'dcs': self.le_dcsdir.text(),
            'dcsbios': self.le_biosdir.text(),
            'font_name': self.le_font_name.text(),
            'git_bios': self.cb_bios_live.isChecked(),
            'git_bios_ref': self.le_bios_live.text(),
            'font_mono_l': self.mono_font['large'],
            'font_mono_m': self.mono_font['medium'],
            'font_mono_s': self.mono_font['small'],
            'font_color_l': self.color_font['large'],
            'font_color_m': self.color_font['medium'],
            'font_color_s': self.color_font['small'],
            'completer_items': self.sp_completer.value(),
            'current_plane': self.current_plane,
            'gkeys_area': self.dockWidgetArea(self.dw_gkeys).value,
            'gkeys_float': self.dw_gkeys.isFloating(),
            'toolbar_area': self.toolBarArea(self.toolbar).value,
            'toolbar_style': self.toolbar.toolButtonStyle().value,
        }
        if self.keyboard.lcd == 'color':
            font_cfg = {'font_color_l': self.hs_large_font.value(),
                        'font_color_m': self.hs_medium_font.value(),
                        'font_color_s': self.hs_small_font.value()}
        else:
            font_cfg = {'font_mono_l': self.hs_large_font.value(),
                        'font_mono_m': self.hs_medium_font.value(),
                        'font_mono_s': self.hs_small_font.value()}
        cfg.update(font_cfg)
        save_yaml(data=cfg, full_path=default_yaml)

    def _reset_defaults_cfg(self) -> None:
        """Set defaults and stop application."""
        save_yaml(data=defaults_cfg, full_path=default_yaml)
        self.config = load_yaml(full_path=default_yaml)
        self.apply_configuration(self.config)
        for name in ['large', 'medium', 'small']:
            getattr(self, f'hs_{name}_font').setValue(getattr(self, f'{self.keyboard.lcd}_font')[name])
        self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Restart', message='DCSpy needs to be close.\nPlease start again manually!')
        self.close()

    # <=><=><=><=><=><=><=><=><=><=><=> others <=><=><=><=><=><=><=><=><=><=><=>
    @property
    def current_plane(self) -> str:
        """
        Get current plane from combo box.

        :return: plane name as string
        """
        return self.combo_planes.currentText()

    @property
    def bios_path(self) -> Path:
        """
        Get path to DCS-BIOS.

        :return: full path as Path
        """
        return Path(self.le_biosdir.text())

    # <=><=><=><=><=><=><=><=><=><=><=> helpers <=><=><=><=><=><=><=><=><=><=><=>
    def run_in_background(self, job: Union[partial, Callable], signal_handlers: Dict[str, Callable]) -> None:
        """
        Worker with signals callback to schedule GUI job in background.

        signal_handlers parameter is a dict with signals from  WorkerSignals,
        possibles signals are: finished, error, result, progress. Values in dict
        are methods/callables as handlers/callbacks for particular signal.

        :param job: GUI method or function to run in background
        :param signal_handlers: signals as keys: finished, error, result, progress and values as callable
        """
        progress = True if 'progress' in signal_handlers.keys() else False
        worker = Worker(func=job, with_progress=progress)
        for signal, handler in signal_handlers.items():
            getattr(worker.signals, signal).connect(handler)
        if isinstance(job, partial):
            job_name = job.func.__name__
            args = job.args
            kwargs = job.keywords
        else:
            job_name = job.__name__
            args = tuple()
            kwargs = dict()
        signals = {signal: handler.__name__ for signal, handler in signal_handlers.items()}
        LOG.debug(f'bg job for: {job_name} args: {args} kwargs: {kwargs} signals {signals}')
        self.threadpool.start(worker)

    @staticmethod
    def _fake_progress(progress_callback: SignalInstance, total_time: int, steps: int = 100,
                       clean_after: bool = True, **kwargs) -> None:
        """
        Make fake progress for progressbar.

        :param progress_callback: signal to update progress bar
        :param total_time: time for fill-up whole bar (in seconds)
        :param steps: number of steps (default 100)
        :param clean_after: clean progress bar when finish
        """
        done_event = kwargs.get('done_event', Event())
        for progress_step in range(1, steps + 1):
            sleep(total_time / steps)
            progress_callback.emit(progress_step)
            if done_event.is_set():
                progress_callback.emit(100)
                break
        if clean_after:
            sleep(0.5)
            progress_callback.emit(0)

    def _progress_by_abs_value(self, value: int) -> None:
        """
        Update progress bar by absolute value.

        :param value: absolute value of progress bar
        """
        self.progressbar.setValue(value)

    def fetch_system_data(self, silence: bool = False) -> SystemData:
        """
        Fetch various system related data.

        :param silence: perform action with silence
        :return: SystemData named tuple with all data
        """
        system, _, release, ver, _, proc = uname()
        dcs_type, dcs_ver = check_dcs_ver(Path(self.config['dcs']))
        dcspy_ver = get_version_string(repo='emcek/dcspy', current_ver=__version__, check=self.config['check_ver'])
        bios_ver = str(self._check_local_bios().ver)
        dcs_bios_ver = self._get_bios_full_version(silence=silence)
        git_ver = 'Not installed'
        if self.git_exec:
            from git import cmd
            git_ver = '.'.join([str(i) for i in cmd.Git().version_info])
        return SystemData(system=system, release=release, ver=ver, proc=proc, dcs_type=dcs_type, dcs_ver=dcs_ver,
                          dcspy_ver=dcspy_ver, bios_ver=bios_ver, dcs_bios_ver=dcs_bios_ver, git_ver=git_ver)

    def _run_file_dialog(self, for_load: bool, for_dir: bool, last_dir: Callable[..., str],
                         widget_name: Optional[str] = None, file_filter: str = 'All Files [*.*](*.*)') -> str:
        """
        Open/save dialog to select file or folder.

        :param for_load: if True show window for load, for save otherwise
        :param for_dir: if True show window for selecting directory only, if False selecting file only
        :param last_dir: function return last selected dir
        :param widget_name: update text for widget
        :param file_filter: list of types of files ;;-seperated: Text [*.txt](*.txt)
        :return: full path to file or directory
        """
        result_path = ''
        if file_filter != 'All Files [*.*](*.*)':
            file_filter = f'{file_filter};;All Files [*.*](*.*)'
        if for_load and for_dir:
            result_path = QFileDialog.getExistingDirectory(self, caption='Open Directory', dir=last_dir(), options=QFileDialog.Option.ShowDirsOnly)
        if for_load and not for_dir:
            result_path = QFileDialog.getOpenFileName(self, caption='Open File', dir=last_dir(), filter=file_filter, options=QFileDialog.Option.ReadOnly)[0]
        if not for_load and not for_dir:
            result_path = QFileDialog.getSaveFileName(self, caption='Save File', dir=last_dir(), filter=file_filter, options=QFileDialog.Option.ReadOnly)[0]
        if widget_name is not None and result_path:
            getattr(self, widget_name).setText(result_path)
        return result_path

    @staticmethod
    def _get_style_for_combobox(key_name: str, fg: str) -> str:
        """
        Get style for QComboBox with foreground color.

        :param key_name: G-Key or LCD Key as string
        :param fg: color as string
        :return: style sheet string
        """
        bg = 'lightblue'
        if '_' in key_name:
            bg = 'lightgreen'
        return f'QComboBox{{color: {fg};background-color: {bg};}} QComboBox QAbstractItemView {{background-color: {bg};}}'

    def _show_message_box(self, kind_of: MsgBoxTypes, title: str, message: str = '') -> None:
        """
        Show any QMessageBox delivered with Qt.

        :param kind_of: any of MsgBoxTypes - information, question, warning, critical, about or aboutQt
        :param title: Title of modal window
        :param message: text of message, default is empty
        """
        message_box = getattr(QMessageBox, kind_of.value)
        if kind_of == MsgBoxTypes.ABOUT_QT:
            message_box(self, title)
        else:
            message_box(self, title, message)

    def _show_custom_msg_box(self, kind_of: QMessageBox.Icon, title: str, text: str, info_txt: str, detail_txt: Optional[str] = None,
                             buttons: Optional[QMessageBox.StandardButton] = None) -> int:
        """
        Show custom message box with hidden text.

        :param title: title
        :param text: first section
        :param info_txt: second section
        :param detail_txt: hidden text
        :param buttons: tuple of buttons
        :return: code of pushed button as integer code
        """
        msg = QMessageBox(text=text, parent=self)
        msg.setIcon(kind_of)
        msg.setWindowTitle(title)
        msg.setInformativeText(info_txt)
        if detail_txt:
            msg.setDetailedText(detail_txt)
        if buttons:
            msg.setStandardButtons(buttons)
        return msg.exec()

    def event_set(self) -> None:
        """Set event to close running thread."""
        self.event.set()

    def activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Signal of activation.

        :param reason: reason of activation
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def _show_toolbar(self) -> None:
        """Toggle show and hide toolbar."""
        if self.a_show_toolbar.isChecked():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    def _show_gkeys_dock(self) -> None:
        """Toggle show and hide G-Keys dock."""
        if self.a_show_gkeys.isChecked():
            self.dw_gkeys.show()
        else:
            self.dw_gkeys.hide()

    def _show_keyboard_dock(self) -> None:
        """Toggle show and hide keyboard dock."""
        if self.a_show_keyboard.isChecked():
            self.dw_keyboard.show()
        else:
            self.dw_keyboard.hide()

    @Slot(bool)
    def _close_dock_widget(self, visible: bool, widget: str) -> None:
        """
        Close dock widget and check menu/toolbar item.

        :param visible: is dock visible
        :param widget: widget name
        """
        action = getattr(self, f'a_show_{widget}')
        if not visible:
            action.setChecked(False)
        else:
            action.setChecked(True)

    def _find_children(self) -> None:
        """Find all widgets of main window."""
        self.statusbar: Union[object, QStatusBar] = self.findChild(QStatusBar, 'statusbar')
        self.systray: Union[object, QSystemTrayIcon] = self.findChild(QSystemTrayIcon, 'systray')
        self.traymenu: Union[object, QMenu] = self.findChild(QMenu, 'traymenu')
        self.progressbar: Union[object, QProgressBar] = self.findChild(QProgressBar, 'progressbar')
        self.toolbar: Union[object, QToolBar] = self.findChild(QToolBar, 'toolbar')
        self.tw_gkeys: Union[object, QTableWidget] = self.findChild(QTableWidget, 'tw_gkeys')
        self.sp_completer: Union[object, QSpinBox] = self.findChild(QSpinBox, 'sp_completer')
        self.combo_planes: Union[object, QComboBox] = self.findChild(QComboBox, 'combo_planes')
        self.tw_main: Union[object, QTabWidget] = self.findChild(QTabWidget, 'tw_main')

        self.dw_gkeys: Union[object, QDockWidget] = self.findChild(QDockWidget, 'dw_gkeys')
        self.dw_keyboard: Union[object, QDockWidget] = self.findChild(QDockWidget, 'dw_keyboard')

        self.l_keyboard: Union[object, QLabel] = self.findChild(QLabel, 'l_keyboard')
        self.l_large: Union[object, QLabel] = self.findChild(QLabel, 'l_large')
        self.l_medium: Union[object, QLabel] = self.findChild(QLabel, 'l_medium')
        self.l_small: Union[object, QLabel] = self.findChild(QLabel, 'l_small')
        self.l_category: Union[object, QLabel] = self.findChild(QLabel, 'l_category')
        self.l_description: Union[object, QLabel] = self.findChild(QLabel, 'l_description')
        self.l_identifier: Union[object, QLabel] = self.findChild(QLabel, 'l_identifier')
        self.l_range: Union[object, QLabel] = self.findChild(QLabel, 'l_range')

        self.a_start: Union[object, QAction] = self.findChild(QAction, 'a_start')
        self.a_stop: Union[object, QAction] = self.findChild(QAction, 'a_stop')
        self.a_quit: Union[object, QAction] = self.findChild(QAction, 'a_quit')
        self.a_save_plane: Union[object, QAction] = self.findChild(QAction, 'a_save_plane')
        self.a_reset_defaults: Union[object, QAction] = self.findChild(QAction, 'a_reset_defaults')
        self.a_show_toolbar: Union[object, QAction] = self.findChild(QAction, 'a_show_toolbar')
        self.a_show_gkeys: Union[object, QAction] = self.findChild(QAction, 'a_show_gkeys')
        self.a_show_keyboard: Union[object, QAction] = self.findChild(QAction, 'a_show_keyboard')
        self.a_about_dcspy: Union[object, QAction] = self.findChild(QAction, 'a_about_dcspy')
        self.a_about_qt: Union[object, QAction] = self.findChild(QAction, 'a_about_qt')
        self.a_report_issue: Union[object, QAction] = self.findChild(QAction, 'a_report_issue')
        self.a_dcspy_updates: Union[object, QAction] = self.findChild(QAction, 'a_dcspy_updates')
        self.a_bios_updates: Union[object, QAction] = self.findChild(QAction, 'a_bios_updates')
        self.a_donate: Union[object, QAction] = self.findChild(QAction, 'a_donate')
        self.a_discord: Union[object, QAction] = self.findChild(QAction, 'a_discord')
        self.a_icons_only: Union[object, QAction] = self.findChild(QAction, 'a_icons_only')
        self.a_text_only: Union[object, QAction] = self.findChild(QAction, 'a_text_only')
        self.a_text_beside: Union[object, QAction] = self.findChild(QAction, 'a_text_beside')
        self.a_text_under: Union[object, QAction] = self.findChild(QAction, 'a_text_under')

        self.pb_start: Union[object, QPushButton] = self.findChild(QPushButton, 'pb_start')
        self.pb_stop: Union[object, QPushButton] = self.findChild(QPushButton, 'pb_stop')
        self.pb_close: Union[object, QPushButton] = self.findChild(QPushButton, 'pb_close')
        self.pb_dcsdir: Union[object, QPushButton] = self.findChild(QPushButton, 'pb_dcsdir')
        self.pb_biosdir: Union[object, QPushButton] = self.findChild(QPushButton, 'pb_biosdir')
        self.pb_collect_data: Union[object, QPushButton] = self.findChild(QPushButton, 'pb_collect_data')
        self.pb_copy: Union[object, QPushButton] = self.findChild(QPushButton, 'pb_copy')
        self.pb_save: Union[object, QPushButton] = self.findChild(QPushButton, 'pb_save')
        self.pb_dcspy_check: Union[object, QPushButton] = self.findChild(QPushButton, 'pb_dcspy_check')
        self.pb_bios_check: Union[object, QPushButton] = self.findChild(QPushButton, 'pb_bios_check')

        self.cb_autostart: Union[object, QCheckBox] = self.findChild(QCheckBox, 'cb_autostart')
        self.cb_show_gui: Union[object, QCheckBox] = self.findChild(QCheckBox, 'cb_show_gui')
        self.cb_check_ver: Union[object, QCheckBox] = self.findChild(QCheckBox, 'cb_check_ver')
        self.cb_ded_font: Union[object, QCheckBox] = self.findChild(QCheckBox, 'cb_ded_font')
        self.cb_lcd_screenshot: Union[object, QCheckBox] = self.findChild(QCheckBox, 'cb_lcd_screenshot')
        self.cb_verbose: Union[object, QCheckBox] = self.findChild(QCheckBox, 'cb_verbose')
        self.cb_autoupdate_bios: Union[object, QCheckBox] = self.findChild(QCheckBox, 'cb_autoupdate_bios')
        self.cb_bios_live: Union[object, QCheckBox] = self.findChild(QCheckBox, 'cb_bios_live')

        self.le_dcsdir: Union[object, QLineEdit] = self.findChild(QLineEdit, 'le_dcsdir')
        self.le_biosdir: Union[object, QLineEdit] = self.findChild(QLineEdit, 'le_biosdir')
        self.le_font_name: Union[object, QLineEdit] = self.findChild(QLineEdit, 'le_font_name')
        self.le_bios_live: Union[object, QLineEdit] = self.findChild(QLineEdit, 'le_bios_live')
        self.le_custom: Union[object, QLineEdit] = self.findChild(QLineEdit, 'le_custom')

        self.rb_g19: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_g19')
        self.rb_g13: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_g13')
        self.rb_g15v1: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_g15v1')
        self.rb_g15v2: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_g15v2')
        self.rb_g510: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_g510')
        self.rb_action: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_action')
        self.rb_fixed_step_inc: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_fixed_step_inc')
        self.rb_fixed_step_dec: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_fixed_step_dec')
        self.rb_set_state: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_set_state')
        self.rb_variable_step_plus: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_variable_step_plus')
        self.rb_variable_step_minus: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_variable_step_minus')
        self.rb_custom: Union[object, QRadioButton] = self.findChild(QRadioButton, 'rb_custom')

        self.hs_large_font: Union[object, QSlider] = self.findChild(QSlider, 'hs_large_font')
        self.hs_medium_font: Union[object, QSlider] = self.findChild(QSlider, 'hs_medium_font')
        self.hs_small_font: Union[object, QSlider] = self.findChild(QSlider, 'hs_small_font')


class AboutDialog(QDialog):
    """About dialog."""
    def __init__(self, parent) -> None:
        """Dcspy about dialog window."""
        super().__init__(parent)
        self.parent: Union[DcsPyQtGui, QWidget] = parent
        UiLoader().loadUi(':/ui/ui/about.ui', self)
        self.l_info: Union[object, QLabel] = self.findChild(QLabel, 'l_info')

    def showEvent(self, event: QShowEvent):
        """Prepare text information about DCSpy application."""
        super().showEvent(event)
        d = self.parent.fetch_system_data(silence=False)
        text = '<html><head/><body><p>'
        text += '<b>Author</b>: <a href="https://github.com/emcek">Michal Plichta</a>'
        text += '<br><b>Project</b>: <a href="https://github.com/emcek/dcspy/">emcek/dcspy</a>'
        text += '<br><b>Wiki</b>: <a href="https://github.com/emcek/dcspy/wiki">docs</a>'
        text += '<br><b>Discord</b>: <a href="https://discord.gg/SP5Yjx3">discord.gg/SP5Yjx3</a>'
        text += '<br><b>Issues</b>: <a href="https://github.com/emcek/dcspy/issues">report issue</a>'
        text += f'<br><b>System</b>: {d.system}{d.release} ver. {d.ver} ({architecture()[0]})'
        text += f'<br><b>Processor</b>: {d.proc}'
        text += f'<br><b>Python</b>: {python_implementation()}-{python_version()}'
        text += f'<br><b>Config</b>: <a href="file:///{default_yaml.parent}">{default_yaml.name}</a>'
        text += f'<br><b>Git</b>: {d.git_ver}'
        text += f'<br><b>PySide6</b>: {pyside6_ver} / <b>Qt</b>: {qt6_ver}'
        text += f'<br><b>DCSpy</b>: {d.dcspy_ver}'
        text += f'<br><b>DCS-BIOS</b>: <a href="https://github.com/DCS-Skunkworks/dcs-bios/releases">{d.bios_ver}</a> '
        text += f'<b>SHA:</b> <a href="https://github.com/DCS-Skunkworks/dcs-bios/commit/{d.sha}">{d.dcs_bios_ver}</a>'
        text += f'<br><b>DCS World</b>: <a href="https://www.digitalcombatsimulator.com/en/news/changelog/openbeta/{d.dcs_ver}/">{d.dcs_ver}</a> ({d.dcs_type})'
        text += '</p></body></html>'
        self.l_info.setText(text)


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:
    * finished - no data
    * error - tuple with exctype, value, traceback.format_exc()
    * result - object/any type - data returned from processing
    * progress - float between 0 and 1 as indication of progress
    * stage - string with current stage
    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)
    stage = Signal(str)


class Worker(QRunnable):
    """Runnable worker."""

    def __init__(self, func: partial, with_progress: bool) -> None:
        """
        Worker thread.

        Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
        :param func: The function callback to run on worker thread
        """
        super().__init__()
        self.func = func
        self.signals = WorkerSignals()
        if with_progress:
            self.func.keywords['progress_callback'] = self.signals.progress

    @Slot()
    def run(self) -> None:
        """Initialise the runner function with passed additional kwargs."""
        try:
            result = self.func()
        except Exception:
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class GitCloneWorker(QRunnable):
    """Worker for git clone with reporting progress."""

    def __init__(self, git_ref: str, bios_path: Path, repo: str = 'DCS-Skunkworks/dcs-bios', to_path: Path = DCS_BIOS_REPO_DIR, silence: bool = False) -> None:
        """
        Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

        :param git_ref: git reference
        :param repo: valid git repository user/name
        :param bios_path: Path to DCS-BIOS
        :param to_path: Path to which the repository should be cloned to
        :param silence: perform action with silence
        """
        super().__init__()
        self.git_ref = git_ref
        self.repo = repo
        self.to_path = to_path
        self.bios_path = bios_path
        self.silence = silence
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        """Clone repository and report progress using special object CloneProgress."""
        try:
            sha = check_github_repo(git_ref=self.git_ref, update=True, repo=self.repo, repo_dir=self.to_path,
                                    progress=CloneProgress(self.signals.progress, self.signals.stage))
            LOG.debug(f'Remove: {self.bios_path} {sha}')
            rmtree(path=self.bios_path, ignore_errors=True)
            LOG.debug(f'Copy Git DCS-BIOS to: {self.bios_path} ')
            copytree(src=DCS_BIOS_REPO_DIR / 'Scripts' / 'DCS-BIOS', dst=self.bios_path)
        except Exception:
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit((sha, self.silence))
        finally:
            self.signals.finished.emit()


class UiLoader(QUiLoader):
    """UI file loader."""
    _baseinstance = None

    def createWidget(self, classname: str, parent: Optional[QWidget] = None, name='') -> QWidget:
        """
        Create widget.

        :param classname: class name
        :param parent: parent
        :param name: name
        :return: QWidget
        """
        if parent is None and self._baseinstance is not None:
            widget = self._baseinstance
        else:
            widget = super().createWidget(classname, parent, name)
            if self._baseinstance is not None:
                setattr(self._baseinstance, name, widget)
        return widget

    def loadUi(self, ui_path: Union[str, bytes, Path], baseinstance=None) -> QWidget:
        """
        Load UI file.

        :param ui_path: path to UI file
        :param baseinstance:
        :return: QWidget
        """
        self._baseinstance = baseinstance
        ui_file = QFile(ui_path)
        ui_file.open(QIODevice.OpenModeFlag.ReadOnly)
        try:
            widget = self.load(ui_file)
            QMetaObject.connectSlotsByName(widget)
            return widget
        finally:
            ui_file.close()
