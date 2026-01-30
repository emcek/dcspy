from __future__ import annotations

import os
import sys
import traceback
from argparse import Namespace
from collections.abc import Callable
from contextlib import suppress
from functools import partial
from importlib import import_module
from logging import DEBUG, INFO, Formatter, Handler, LogRecord, getLogger
from pathlib import Path
from platform import architecture, python_implementation, python_version, uname
from pprint import pformat
from shutil import copy, copytree, rmtree, unpack_archive
from tempfile import gettempdir
from threading import Event, Thread
from time import sleep
from typing import Any, ClassVar
from webbrowser import open_new_tab

from packaging import version
from pydantic import ValidationError
from PySide6 import __version__ as pyside6_ver
from PySide6.QtCore import QAbstractItemModel, QFile, QIODevice, QMetaObject, QObject, QRunnable, Qt, QThreadPool, Signal, SignalInstance, Slot
from PySide6.QtCore import __version__ as qt6_ver
from PySide6.QtGui import (QAction, QActionGroup, QColor, QColorConstants, QFont, QGuiApplication, QIcon, QPixmap, QShowEvent, QStandardItemModel, QStyleHints,
                           QTextCharFormat)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox, QCompleter, QDialog, QDockWidget, QFileDialog, QGroupBox, QLabel, QLineEdit,
                               QListView, QMainWindow, QMenu, QMessageBox, QProgressBar, QPushButton, QRadioButton, QSlider, QSpinBox, QStatusBar,
                               QSystemTrayIcon, QTableWidget, QTabWidget, QTextBrowser, QTextEdit, QToolBar, QToolBox, QWidget)

from dcspy import default_yaml, qtgui_rc
from dcspy.models import (ALL_DEV, BIOS_REPO_NAME, CTRL_LIST_SEPARATOR, DCSPY_REPO_NAME, AnyButton, ControlDepiction, ControlKeyData, DcspyConfigYaml,
                          FontsConfig, Gkey, GuiPlaneInputRequest, GuiTab, LcdButton, LcdMono, LcdType, LogitechDeviceModel, MouseButton, MsgBoxTypes, Release,
                          RequestType, SystemData, __version__)
from dcspy.starter import DCSpyStarter
from dcspy.utils import (CloneProgress, check_bios_ver, check_dcs_bios_entry, check_dcs_ver, check_github_repo, check_ver_at_github, collect_debug_data,
                         count_files, defaults_cfg, detect_system_color_mode, download_file, generate_bios_jsons_with_lupa, get_all_git_refs,
                         get_depiction_of_ctrls, get_inputs_for_plane, get_list_of_ctrls, get_plane_aliases, get_planes_list, get_version_string,
                         is_git_exec_present, is_git_object, load_yaml, run_command, save_yaml)

_ = qtgui_rc  # prevent to remove import statement accidentally
LOG = getLogger(__name__)
NO_MSG_BOX = int(os.environ.get('DCSPY_NO_MSG_BOXES', 0))
LOGI_DEV_RADIO_BUTTON = {'rb_g19': 0, 'rb_g13': 0, 'rb_g15v1': 0, 'rb_g15v2': 0, 'rb_g510': 0,
                         'rb_g910': 1, 'rb_g710': 1, 'rb_g110': 1, 'rb_g103': 1, 'rb_g105': 1, 'rb_g11': 1,
                         'rb_g633': 2, 'rb_g35': 2, 'rb_g930': 2, 'rb_g933': 2,
                         'rb_g600': 3, 'rb_g300': 3, 'rb_g400': 3, 'rb_g700': 3, 'rb_g9': 3, 'rb_mx518': 3, 'rb_g402': 3, 'rb_g502': 3, 'rb_g602': 3}


class DcsPyQtGui(QMainWindow):
    """PySide6 GUI for DCSpy."""

    def __init__(self, cli_args=Namespace(), cfg_dict: DcspyConfigYaml | None = None) -> None:
        """
        PySide6 GUI for DCSpy.

        :param cli_args: Namespace of CLI arguments
        :param cfg_dict: dict with configuration
        """
        super().__init__()
        UiLoader().load_ui(':/ui/ui/qtdcs.ui', self)
        self._find_children()
        self.config = cfg_dict
        if not cfg_dict:
            self.config = load_yaml(full_path=default_yaml)
        self._init_gui_logger()
        self.threadpool = QThreadPool.globalInstance()
        LOG.debug(f'QThreadPool with {self.threadpool.maxThreadCount()} thread(s)')
        self.cli_args = cli_args
        self.event: Event = Event()
        self.device = LogitechDeviceModel(klass='', lcd_info=LcdMono)
        self.mono_font = {'large': 0, 'medium': 0, 'small': 0}
        self.color_font = {'large': 0, 'medium': 0, 'small': 0}
        self.current_row = -1
        self.current_col = -1
        self._completer_items = 0
        self._git_refs_count = 0
        self.plane_aliases = ['']
        self.ctrl_input: dict[str, dict[str, ControlKeyData]] = {}
        self.ctrl_list = ['']
        self.ctrl_depiction: dict[str, ControlDepiction] = {}
        self.input_reqs: dict[str, dict[str, GuiPlaneInputRequest]] = {}
        self.git_exec = is_git_exec_present()
        self.bios_git_addr = self.config['git_bios_repo']
        self.l_bios = version.Version('0.0.0')
        self.r_bios = version.Version('0.0.0')
        self.systray = QSystemTrayIcon()
        self.traymenu = QMenu()
        self.dw_gkeys.hide()
        self.dw_device.hide()
        self.dw_device.setFloating(True)
        self.bg_rb_input_iface = QButtonGroup(self)
        self.bg_rb_device = QButtonGroup(self)
        self._init_tray()
        self._init_combo_plane()
        self._init_menu_bar()
        self.apply_configuration(cfg=self.config)
        self._init_settings()
        self._init_devices()
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

    def _init_gui_logger(self) -> None:
        """Initialize GUI log handler."""
        self.gui_log = QTextEditLogHandler(text_widget=self.te_debug)
        formatter = Formatter(fmt='%(asctime)s | %(levelname)-7s | %(threadName)-10s | %(message)s / %(funcName)s:%(lineno)d', datefmt='%H:%M:%S')
        self.gui_log.setFormatter(formatter)
        self.gui_log.setLevel(INFO)
        if self.config.get('verbose', False):
            self.gui_log.setLevel(DEBUG)
        LOG.parent.addHandler(self.gui_log)
        self.hs_debug_font_size.valueChanged.connect(self._hs_debug_font_size_changed)

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
            message = f'Folder not exists: \n{self.config["dcsbios"]}\n\nCheck DCS-BIOS path.\n\n{exc}'  # generate json/bios
            self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Get Planes List', message=message)
        except TypeError as exc:
            LOG.warning(exc, exc_info=True)

    def _init_settings(self) -> None:
        """Initialize of settings."""
        self.pb_dcsdir.clicked.connect(partial(self._run_file_dialog, last_dir=lambda: 'C:\\', widget_name='le_dcsdir'))
        self.le_dcsdir.textChanged.connect(partial(self._is_dir_exists, widget_name='le_dcsdir'))
        self.pb_biosdir.clicked.connect(partial(self._run_file_dialog, last_dir=lambda: 'C:\\', widget_name='le_biosdir'))
        self.le_biosdir.textChanged.connect(partial(self._is_dir_dcs_bios, widget_name='le_biosdir'))
        self.pb_collect_data.clicked.connect(self._collect_data_clicked)
        self.pb_start.clicked.connect(self._start_clicked)
        self.a_start.triggered.connect(self._start_clicked)
        self.pb_stop.clicked.connect(self._stop_clicked)
        self.a_stop.triggered.connect(self._stop_clicked)
        self.dw_gkeys.visibilityChanged.connect(partial(self._close_dock_widget, widget='gkeys'))
        self.dw_device.visibilityChanged.connect(partial(self._close_dock_widget, widget='device'))
        self.pb_dcspy_check.clicked.connect(self._dcspy_check_clicked)
        self.pb_bios_check.clicked.connect(self._bios_check_clicked)
        self.pb_bios_repair.clicked.connect(self._bios_repair_clicked)
        self.le_bios_ref.textEdited.connect(self._is_git_object_exists)
        self.le_bios_ref.returnPressed.connect(partial(self._bios_check_clicked, silence=False))
        self.le_bios_repo.textEdited.connect(self._bios_git_repo_chnaged)
        self.cb_bios_live.toggled.connect(self._cb_bios_live_toggled)
        self.sp_completer.valueChanged.connect(self._set_find_value)  # generate json/bios
        self.tw_gkeys.currentCellChanged.connect(self._save_current_cell)
        self.pb_copy.clicked.connect(self._copy_cell_to_row)
        self.pb_save.clicked.connect(self._save_gkeys_cfg)
        self.combo_planes.currentIndexChanged.connect(self._load_table_gkeys)  # generate json/bios
        self.bg_rb_input_iface.addButton(self.rb_action)
        self.bg_rb_input_iface.addButton(self.rb_cycle)
        self.bg_rb_input_iface.addButton(self.rb_set_state)
        self.bg_rb_input_iface.addButton(self.rb_fixed_step_inc)
        self.bg_rb_input_iface.addButton(self.rb_fixed_step_dec)
        self.bg_rb_input_iface.addButton(self.rb_variable_step_plus)
        self.bg_rb_input_iface.addButton(self.rb_variable_step_minus)
        self.bg_rb_input_iface.addButton(self.rb_custom)
        self.bg_rb_input_iface.addButton(self.rb_push_button)
        self.bg_rb_input_iface.buttonClicked.connect(self._input_iface_changed_or_custom_text_changed)
        self.le_custom.editingFinished.connect(self._input_iface_changed_or_custom_text_changed)
        self.le_custom.returnPressed.connect(self._input_iface_changed_or_custom_text_changed)
        self.hs_set_state.valueChanged.connect(self._input_iface_changed_or_custom_text_changed)
        self.hs_set_state.valueChanged.connect(self._hs_set_state_moved)
        for rb_dev_widget in ['rb_g19', 'rb_g13', 'rb_g15v1', 'rb_g15v2', 'rb_g510', 'rb_g910', 'rb_g710', 'rb_g110', 'rb_g103', 'rb_g105', 'rb_g11', 'rb_g633',
                              'rb_g35', 'rb_g930', 'rb_g933', 'rb_g600', 'rb_g300', 'rb_g400', 'rb_g700', 'rb_g9', 'rb_mx518', 'rb_g402', 'rb_g502', 'rb_g602']:
            self.bg_rb_device.addButton(getattr(self, rb_dev_widget))
        self.cb_debug_enable.toggled.connect(self._toggle_gui_logging)

    def _init_devices(self) -> None:
        """Initialize of a Logitech device."""
        for logitech_dev in ALL_DEV:
            rb_device: QRadioButton = getattr(self, f'rb_{logitech_dev.klass.lower()}')
            rb_device.clicked.connect(partial(self._select_logi_dev, logitech_dev))
            rb_device.setToolTip(str(logitech_dev))

    def _init_menu_bar(self) -> None:
        """Initialize of menubar."""
        self.a_reset_defaults.triggered.connect(self._reset_defaults_cfg)
        self.a_quit.triggered.connect(self.close)
        self.a_save_plane.triggered.connect(self._save_gkeys_cfg)
        self.a_show_toolbar.triggered.connect(self._show_toolbar)
        self.a_show_gkeys.triggered.connect(self._show_gkeys_dock)
        self.a_show_device.triggered.connect(self._show_device_dock)
        self.a_report_issue.triggered.connect(partial(open_new_tab, url=f'https://github.com/{DCSPY_REPO_NAME}/issues'))
        self.a_discord.triggered.connect(partial(open_new_tab, url='https://discord.gg/SP5Yjx3'))
        self.a_donate.triggered.connect(partial(open_new_tab, url='https://paypal.me/emcek137'))
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

        color_mode = QActionGroup(self)
        color_mode.addAction(self.a_mode_light)
        color_mode.addAction(self.a_mode_dark)
        color_mode.addAction(self.a_mode_system)
        color_mode.triggered.connect(self._switch_color_mode)

    def _init_autosave(self) -> None:
        """Initialize of autosave."""
        widget_dict = {
            'le_dcsdir': 'textChanged', 'le_biosdir': 'textChanged', 'le_font_name': 'textEdited', 'le_bios_ref': 'returnPressed',
            'le_bios_repo': 'returnPressed', 'hs_large_font': 'valueChanged', 'hs_medium_font': 'valueChanged', 'hs_small_font': 'valueChanged',
            'hs_debug_font_size': 'valueChanged', 'sp_completer': 'valueChanged', 'combo_planes': 'currentIndexChanged',
            'toolbar': 'visibilityChanged', 'dw_gkeys': 'visibilityChanged', 'a_icons_only': 'triggered', 'a_text_only': 'triggered',
            'a_text_beside': 'triggered', 'a_text_under': 'triggered', 'a_mode_light': 'triggered', 'a_mode_dark': 'triggered',
            'a_mode_system': 'triggered', 'cb_autostart': 'toggled', 'cb_show_gui': 'toggled', 'cb_check_ver': 'toggled',
            'cb_ded_font': 'toggled', 'cb_lcd_screenshot': 'toggled', 'cb_verbose': 'toggled', 'cb_autoupdate_bios': 'toggled',
            'cb_bios_live': 'toggled', 'cb_debug_enable': 'toggled', 'rb_g19': 'toggled', 'rb_g13': 'toggled', 'rb_g15v1': 'toggled',
            'rb_g15v2': 'toggled', 'rb_g510': 'toggled', 'rb_g910': 'toggled', 'rb_g710': 'toggled', 'rb_g110': 'toggled', 'rb_g103': 'toggled',
            'rb_g105': 'toggled', 'rb_g11': 'toggled', 'rb_g35': 'toggled', 'rb_g633': 'toggled', 'rb_g930': 'toggled', 'rb_g933': 'toggled',
            'rb_g600': 'toggled', 'rb_g300': 'toggled', 'rb_g400': 'toggled', 'rb_g700': 'toggled', 'rb_g9': 'toggled', 'rb_mx518': 'toggled',
            'rb_g402': 'toggled', 'rb_g502': 'toggled', 'rb_g602': 'toggled',
        }
        for widget_name, trigger_method in widget_dict.items():
            getattr(getattr(self, widget_name), trigger_method).connect(self.save_configuration)

    def _trigger_refresh_data(self) -> None:
        """Refresh widgets states and regenerates data."""
        try:
            self._is_dir_exists(text=self.le_dcsdir.text(), widget_name='le_dcsdir')
            self._is_dir_dcs_bios(text=self.bios_path, widget_name='le_biosdir')
            if self.cb_bios_live.isChecked():
                self.le_bios_ref.setEnabled(True)
                self.le_bios_repo.setEnabled(True)
                self._is_git_object_exists(text=self.le_bios_ref.text())
            for logitech_dev in ALL_DEV:
                logi_dev_rb_name = f'rb_{logitech_dev.klass.lower()}'
                dev = getattr(self, logi_dev_rb_name)
                if dev.isChecked():
                    self._select_logi_dev(logi_dev=logitech_dev)  # generate json/bios
                    self.toolBox.setCurrentIndex(LOGI_DEV_RADIO_BUTTON.get(logi_dev_rb_name, 0))
                    break
        except KeyError as err:
            exc, value, tb = sys.exc_info()
            traceback_data = traceback.format_exception(exc, value=value, tb=tb)
            self._show_custom_msg_box(
                kind_of=QMessageBox.Icon.Warning,
                title='Warning',
                text=f'Can not find key: {err}. Please report error with detail below. You can use menu Help / Report issue option.',
                info_txt=f'Problem: {type(err).__name__}.',
                detail_txt='\n'.join(traceback_data)
            )

    def _set_find_value(self, value) -> None:
        """
        Refresh a configuration of table and completer when visible items value changed.

        :param value: Number of items visible
        """
        self._completer_items = value
        LOG.debug(f'Set number of results: {value}')
        self._load_table_gkeys()

    def _select_logi_dev(self, logi_dev: LogitechDeviceModel) -> None:
        """
        Triggered when a new device is selected.

        Based on a currently selected device:
            * Add correct numbers of rows and columns
            * enable DED font checkbox
            * updates font sliders (range and values)
            * update dock with an image of a device

        :param logi_dev: Logitech device model object
        """
        for mode_col in range(self.device.cols):
            self.tw_gkeys.removeColumn(mode_col)
        for gkey_row in range(self.device.rows.total):
            self.tw_gkeys.removeRow(gkey_row)
        self.device = getattr(import_module('dcspy.models'), logi_dev.klass)
        LOG.debug(f'Select: {repr(self.device)}')
        if self.device.lcd_info.type != LcdType.NONE:
            self._set_ded_font_and_font_sliders()
        self._update_dock()
        self.current_row = -1
        self.current_col = -1
        self._load_table_gkeys()  # generate json/bios
        self.current_row = 0
        self.current_col = 0
        cell_combo: QComboBox | QWidget = self.tw_gkeys.cellWidget(self.current_row, self.current_col)
        self._cell_ctrl_content_changed(text=cell_combo.currentText(), widget=cell_combo, row=self.current_row, col=self.current_col)

    def _set_ded_font_and_font_sliders(self) -> None:
        """Enable the DED font checkbox and updates font sliders."""
        if self.device.lcd_info.type == LcdType.COLOR:
            self.cb_ded_font.setEnabled(True)
            minimum = 15
            maximum = 40
        else:
            self.cb_ded_font.setEnabled(False)
            minimum = 7
            maximum = 20

        for name in ['large', 'medium', 'small']:
            hs: QSlider = getattr(self, f'hs_{name}_font')
            with suppress(RuntimeError):
                hs.valueChanged.disconnect()
            hs.setMinimum(minimum)
            hs.setMaximum(maximum)
            hs.valueChanged.connect(partial(self._set_label_and_hs_value, name=name))
            hs.valueChanged.connect(self.save_configuration)
            hs.setValue(getattr(self, f'{self.device.lcd_name}_font')[name])

    def _set_label_and_hs_value(self, value, name) -> None:
        """
        Set internal field for current value of slider and update label.

        :param value: Slider's value
        :param name: Slider's name
        """
        getattr(self, f'{self.device.lcd_name}_font')[name] = value
        getattr(self, f'l_{name}').setText(str(value))

    def _update_dock(self) -> None:
        """Update dock with an image of a device."""
        self.l_keyboard.setPixmap(QPixmap(f':/img/img/{self.device.klass}device.png'))

    def _collect_data_clicked(self) -> None:
        """Collect data for troubleshooting and ask a user where to save."""
        zip_file = collect_debug_data()
        try:
            dst_dir = str(Path(os.environ['USERPROFILE']) / 'Desktop')
        except KeyError:
            dst_dir = 'C:\\'
        directory = self._run_file_dialog(last_dir=lambda: dst_dir)
        destination = Path(directory) / zip_file.name
        try:
            copy(zip_file, destination)
            self.statusbar.showMessage(f'Save: {destination}')
            LOG.debug(f'Save debug file: {destination}')
        except PermissionError as err:
            LOG.debug(f'Error: {err}, Collected data: {zip_file}')
            self._show_message_box(kind_of=MsgBoxTypes.WARNING, title=err.args[1], message=f'Can not save file:\n{err.filename}')

    def _is_dir_exists(self, text: str, widget_name: str) -> bool:
        """
        Check if the directory exists.

        :param text: Contents of a text field
        :param widget_name: Widget name
        :return: True if a directory exists, False otherwise.
        """
        dir_exists = Path(text).is_dir()
        LOG.debug(f'Path: {text} for {widget_name} exists: {dir_exists}')
        if dir_exists:
            getattr(self, widget_name).setStyleSheet('')
            return True
        getattr(self, widget_name).setStyleSheet('color: red;')
        return False

    def _is_dir_dcs_bios(self, text: Path | str, widget_name: str) -> bool:
        """
        Check if the directory is a valid DCS-BIOS installation.

        :param text: Contents of a text field
        :param widget_name: Widget name
        :return: True if valid BIOS directory, False otherwise.
        """
        text = Path(text)
        bios_lua = text / 'BIOS.lua'
        number_of_jsons = count_files(directory=text / 'doc' / 'json', extension='json')
        widget = getattr(self, widget_name)
        if all([text.is_dir(), bios_lua.is_file(), number_of_jsons]):
            widget.setStyleSheet('')
            widget.setToolTip('Location of DCS-BIOS in Saved Games')
            return True
        LOG.debug(f'BIOS dir: {text}: {text.is_dir()=}, {bios_lua.is_file()=}, {number_of_jsons=}')
        widget.setStyleSheet('color: red;')
        widget.setToolTip('It is not valid DCS-BIOS directory or it not contains planes JSON files')
        return False

    def _generate_bios_jsons_with_dcs_lua(self) -> bool:
        """
        Regenerate DCS-BIOS JSON files.

        :return: True if a generation is successful, False otherwise.
        """
        lua_exec = self.dcs_path / 'bin' / 'luae.exe'
        LOG.info('Regenerating DCS-BIOS JSONs files...')
        return_code = -1
        try:
            return_code = run_command(cmd=[lua_exec, r'Scripts\DCS-BIOS\test\compile\LocalCompile.lua'], cwd=self.bios_repo_path)
        except (FileNotFoundError, NotADirectoryError) as err:
            exc, value, tb = sys.exc_info()
            traceback_data = traceback.format_exception(exc, value=value, tb=tb)
            self._show_custom_msg_box(
                kind_of=QMessageBox.Icon.Warning,
                title='Problem with command',
                text=f'Error during executing command:\n{lua_exec} Scripts\\DCS-BIOS\\test\\compile\\LocalCompile.lua',
                info_txt=f'Problem: {err}\n\nPlease report  error with detail below. You can use menu Help / Report issue option.',
                detail_txt='\n'.join(traceback_data)
            )
        LOG.debug(f'RC: {return_code} {lua_exec=}, cwd={self.bios_repo_path}')
        return True if return_code == 0 else False

    # <=><=><=><=><=><=><=><=><=><=><=> g-keys tab <=><=><=><=><=><=><=><=><=><=><=>
    def _load_table_gkeys(self) -> None:
        """Initialize table with cockpit data."""
        if self._check_and_rebuild_ctrl_input_table(plane_name=self.current_plane):
            return
        self.tw_gkeys.setColumnCount(self.device.cols)
        for mode_col in range(self.device.cols):
            self.tw_gkeys.setColumnWidth(mode_col, 200)
        self.tw_gkeys.setRowCount(self.device.rows.total)
        labels_g_key = [f'G{i}' for i in range(1, self.device.rows.g_key + 1)]
        labels_lcd_key = [lcd_key.name for lcd_key in self.device.lcd_keys]
        m_btn_start, m_btn_end = self.device.btn_m_range
        labels_m_key = [f'M{i}' for i in range(m_btn_start, m_btn_end + 1)]
        self.tw_gkeys.setVerticalHeaderLabels(labels_g_key + labels_lcd_key + labels_m_key)
        self.tw_gkeys.setHorizontalHeaderLabels([f'Mode {i}' for i in range(1, self.device.cols + 1)])
        plane_keys = load_yaml(full_path=default_yaml.parent / f'{self.current_plane}.yaml')
        LOG.debug(f'Load {self.current_plane}:\n{pformat(plane_keys)}')
        self.input_reqs[self.current_plane] = GuiPlaneInputRequest.from_plane_gkeys(plane_gkeys=plane_keys)
        self._generate_table()

    def _generate_table(self) -> None:
        """Generate a table of combo boxes with completer functionality."""
        ctrl_list_without_sep = [item for item in self.ctrl_list if item and CTRL_LIST_SEPARATOR not in item]
        for row in range(0, self.device.rows.total):
            for col in range(0, self.device.cols):
                self._make_combo_with_completer_at(row, col, ctrl_list_without_sep)
        if self.current_row != -1 and self.current_col != -1:
            cell_combo: QComboBox | QWidget = self.tw_gkeys.cellWidget(self.current_row, self.current_col)
            self._cell_ctrl_content_changed(text=cell_combo.currentText(), widget=cell_combo, row=self.current_row,
                                            col=self.current_col)

    def _make_combo_with_completer_at(self, row: int, col: int, ctrl_list_no_sep: list[str]) -> None:
        """
        Make QComboBox widget with completer with a list of strings in cell in row and column.

        :param row: Current row
        :param col: Current column
        :param ctrl_list_no_sep: List of control inputs without separator
        """
        key = self.device.get_key_at(row=row, col=col)
        if col == 0 or row < self.device.no_g_keys:
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
                identifier = self.input_reqs[self.current_plane][str(key)].identifier
            except KeyError:
                identifier = ''
            combo.setCurrentText(identifier)
            combo.editTextChanged.connect(partial(self._cell_ctrl_content_changed, widget=combo, row=row, col=col))
        else:
            combo = QComboBox()
            combo.setDisabled(True)
            self.tw_gkeys.setCellWidget(row, col, combo)
        combo.setStyleSheet(self._get_style_for_combobox(key=key, fg='black'))

    def _check_and_rebuild_ctrl_input_table(self, plane_name: str) -> bool:
        """
        Detect when a new plane is selected.

        Compare old and new plane aliases and reload when needed:
            * regenerate control inputs for a new plane
            * construct a list of controls for every cell in the table
            * update aliases

        In case of problems:
            * pop-up with details
            * back to a previous plane or first in a list

        :param plane_name: BIOS plane name
        :return: True when rebuild is not needed, False otherwise.
        """
        plane_aliases = self._get_plane_aliases(plane_name)

        if self.plane_aliases != plane_aliases[plane_name]:
            return self._rebuild_or_not_rebuild_planes_aliases(plane_aliases, plane_name)
        return False

    def _get_plane_aliases(self, plane_name: str) -> dict[str, list[str]]:
        """
        Try getting plane aliases.

        Show a warning message when fails DCS-BIOS path error.

        :param plane_name: BIOS plane name.
        :return: A dictionary of the plane aliases or empty dict.
        """
        try:
            if count_files(directory=self.bios_path / 'doc' / 'json', extension='json') < 1:
                generate_bios_jsons_with_lupa(dcs_save_games=Path(self.le_biosdir.text()).parents[1])
            if count_files(directory=self.bios_path / 'doc' / 'json', extension='json') < 1:
                self._generate_bios_jsons_with_dcs_lua()
            self._is_dir_dcs_bios(text=self.bios_path, widget_name='le_biosdir')
            return get_plane_aliases(plane=plane_name, bios_dir=self.bios_path)
        except FileNotFoundError as err:
            message = f'Folder not exists:\n{self.bios_path}\n\nCheck DCS-BIOS path.\n\n{err}'  # generate json/bios
            self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Get Plane Aliases', message=message)
            return {}

    def _rebuild_or_not_rebuild_planes_aliases(self, plane_aliases: dict[str, list[str]], plane_name: str) -> bool:
        """
        Check if rebuild is possible and return false or not possible and return true.

        :param plane_aliases: Dict with BIOS plane aliases
        :param plane_name: Plane name which should be validated
        :return: True when rebuild is not required, False otherwise
        """
        try:
            return self._rebuild_needed(plane_aliases, plane_name)
        except ValidationError as validation_err:
            return self._rebuild_not_needed(plane_aliases, plane_name, validation_err)

    def _rebuild_needed(self, plane_aliases: dict[str, list[str]], plane_name: str) -> bool:
        """
        Rebuild is required.

        :param plane_aliases: List of all YAML files for plane definition
        :param plane_name: BIOS plane name
        :return: False - the rebuild is required
        """
        self.ctrl_input = get_inputs_for_plane(plane=plane_name, bios_dir=self.bios_path)
        self.plane_aliases = plane_aliases[plane_name]
        LOG.debug(f'Get input list: {plane_name} {plane_aliases}, old: {self.plane_aliases}')
        self.ctrl_list = get_list_of_ctrls(inputs=self.ctrl_input)
        self.ctrl_depiction = get_depiction_of_ctrls(inputs=self.ctrl_input)
        self._update_combo_search()
        return False

    def _update_combo_search(self) -> None:
        """Update the combo search widget with new control depiction data."""
        max_name, max_desc = (max(len(i[1]) for i in depiction_val) for depiction_val in zip(*self.ctrl_depiction.values()))
        ctrl_desc_list = [f'{i.name:<{max_name}} | {i.description:<{max_desc}}' for i in self.ctrl_depiction.values()]
        completer = QCompleter(ctrl_desc_list)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setMaxVisibleItems(self._completer_items)
        completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
        completer.popup().setFont(QFont('Courier', 9))
        self.combo_search.clear()
        view = QListView(self.combo_search)
        self.combo_search.setView(view)
        view.setTextElideMode(Qt.TextElideMode.ElideRight)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.combo_search.addItems(ctrl_desc_list)
        self.combo_search.setCompleter(completer)
        self.combo_search.textActivated.connect(self._copy_text_to_clipboard)
        self.combo_search.clearEditText()

    def _copy_text_to_clipboard(self, text: str) -> None:
        """
        Copy the specified text to the clipboard.

        Selects only the first word before space and update the statusbar message.

        :param text: The text to be copied to the clipboard.
        """
        clipboard = QApplication.clipboard()
        try:
            key_name = text.split(' ')[0]
            clipboard.setText(key_name)
            self.statusbar.showMessage(f'{key_name} copied to clipboard')
        except IndexError:
            LOG.debug(f'Can not split: {text=}.')

    def _rebuild_not_needed(self, plane_aliases: dict[str, list[str]], plane_name: str, exc: ValidationError) -> bool:
        """
        Rebuild is not required.

        :param plane_aliases: List of all YAML files for plane definition
        :param plane_name: BIOS plane name
        :param exc: The ValidationError object containing the validation errors.
        :return: True - the rebuild is not required
        """
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
        Check if control input exists in a current plane's control list.

        * set details for a current control input
        * set styling
        * add description tooltip
        * save control request for a current plane

        :param text: Current text
        :param widget: Combo instance
        :param row: Current row
        :param col: Current column
        """
        self.l_category.setText('')
        self.l_description.setText('')
        self.l_identifier.setText('')
        self.l_range.setText('')
        widget.setToolTip('')
        key = self.device.get_key_at(row=row, col=col)
        widget.setStyleSheet(self._get_style_for_combobox(key=key, fg='red'))
        if text in self.ctrl_list and CTRL_LIST_SEPARATOR not in text:
            section = self._find_section_name(ctrl_name=text)
            ctrl_key = self.ctrl_input[section][text]
            widget.setToolTip(ctrl_key.description)
            widget.setStyleSheet(self._get_style_for_combobox(key=key, fg='black'))
            self.l_category.setText(f'Category: {section}')
            self.l_description.setText(f'Description: {ctrl_key.description}')
            self.l_identifier.setText(f'Identifier: {text}')
            self.l_range.setText(f'Range: 0 - {ctrl_key.max_value}')
            self._enable_checked_iface_radio_button(ctrl_key=ctrl_key)
            self._checked_iface_rb_for_identifier(key_name=str(key))
            input_iface_name = self.bg_rb_input_iface.checkedButton().objectName()
            custom_value = self._get_custom_value(input_iface_name)
            self.input_reqs[self.current_plane][str(key)] = GuiPlaneInputRequest.from_control_key(ctrl_key=ctrl_key, rb_iface=input_iface_name,
                                                                                                  custom_value=custom_value)
        elif text == '':
            widget.setStyleSheet(self._get_style_for_combobox(key=key, fg='black'))
            self.input_reqs[self.current_plane][str(key)] = GuiPlaneInputRequest.make_empty()  # maybe del
            for rb_widget in self.bg_rb_input_iface.buttons():
                rb_widget.setEnabled(False)
                rb_widget.setChecked(False)

    def _find_section_name(self, ctrl_name: str) -> str:
        """
        Find section name of control input name.

        :param ctrl_name: Input name of controller.
        :return: Section name as string
        """
        idx = self.ctrl_list.index(ctrl_name)
        for element in reversed(self.ctrl_list[:idx]):
            if element.startswith(CTRL_LIST_SEPARATOR):
                return element.strip(f' {CTRL_LIST_SEPARATOR}')
        return ''

    def _enable_checked_iface_radio_button(self, ctrl_key: ControlKeyData) -> None:
        """
        Enable and checked default input interface radio buttons for a current identifier.

        Order of execution is important.

        :param ctrl_key: ControlKeyData instance
        """
        self._disable_all_widgets()
        self._handle_variable_step(ctrl_key)
        self._handle_set_state(ctrl_key)
        self._handle_variable_step_and_set_state(ctrl_key)
        self._handle_fixed_step(ctrl_key)
        self._handle_action(ctrl_key)
        self._handle_push_button(ctrl_key)
        self.rb_custom.setEnabled(True)

    def _disable_all_widgets(self) -> None:
        """Disable all radio button widgets."""
        for widget in self.bg_rb_input_iface.buttons():
            widget.setEnabled(False)

    def _handle_variable_step(self, ctrl_key: ControlKeyData) -> None:
        """Handle the control key for VariableStep."""
        if ctrl_key.has_variable_step:
            self.rb_variable_step_plus.setEnabled(True)
            self.rb_variable_step_minus.setEnabled(True)
            self.rb_variable_step_plus.setChecked(True)

    def _handle_set_state(self, ctrl_key: ControlKeyData) -> None:
        """Handle the control key for SetState and cycle action."""
        if ctrl_key.has_set_state:
            self.rb_set_state.setEnabled(True)
            self.rb_set_state.setChecked(True)
            self.rb_cycle.setEnabled(True)
            self.rb_cycle.setChecked(True)
            self.hs_set_state.setMinimum(0)
            self.hs_set_state.setMaximum(ctrl_key.max_value)
            self.hs_set_state.setSingleStep(ctrl_key.suggested_step)
            self.hs_set_state.setPageStep(ctrl_key.suggested_step)
            self.hs_set_state.setTickInterval(ctrl_key.suggested_step)

    def _handle_variable_step_and_set_state(self, ctrl_key: ControlKeyData) -> None:
        """Handle the case where the control key has a VariableStep and SetState."""
        if ctrl_key.input_len == 2 and ctrl_key.has_variable_step and ctrl_key.has_set_state:
            self.rb_variable_step_plus.setChecked(True)

    def _handle_fixed_step(self, ctrl_key: ControlKeyData) -> None:
        """Handle the control key for FixedStep."""
        if ctrl_key.has_fixed_step:
            self.rb_fixed_step_inc.setEnabled(True)
            self.rb_fixed_step_dec.setEnabled(True)
            self.rb_fixed_step_inc.setChecked(True)

    def _handle_action(self, ctrl_key: ControlKeyData) -> None:
        """Handle the control key for Action."""
        if ctrl_key.has_action:
            self.rb_action.setEnabled(True)
            self.rb_action.setChecked(True)

    def _handle_push_button(self, ctrl_key: ControlKeyData) -> None:
        """Handle the control key for Button action."""
        if ctrl_key.is_push_button:
            self.rb_push_button.setEnabled(True)

    def _checked_iface_rb_for_identifier(self, key_name: str) -> None:
        """
        Enable input interfaces for a current control input identifier.

        :param key_name: G-Key, LCD or Mouse button as string
        """
        with suppress(KeyError, AttributeError):
            widget_iface = self.input_reqs[self.current_plane][key_name].widget_iface
            if widget_iface == 'rb_custom':
                self.le_custom.setText(self.input_reqs[self.current_plane][key_name].request.split(f'{RequestType.CUSTOM.value} ')[1])
            elif widget_iface == 'rb_set_state':
                self.hs_set_state.setValue(int(self.input_reqs[self.current_plane][key_name].request.split(' ')[1]))
            else:
                self.le_custom.setText('')
                self.hs_set_state.setValue(0)
            getattr(self, widget_iface).setChecked(True)

    def _hs_set_state_moved(self, value: int) -> None:
        """
        Set tooltip with current value of slider.

        :param value: The new value to set.
        """
        self.hs_set_state.setToolTip(str(value))

    @staticmethod
    def _disable_items_with(text: str, widget: QComboBox) -> None:
        """
        Disable items in ComboBox, which shouldn't be selected.

        :param widget: QComboBox instance
        """
        model: QStandardItemModel | QAbstractItemModel = widget.model()
        for i in range(0, widget.count()):
            if text in model.item(i).text():
                model.item(i).setFlags(Qt.ItemFlag.NoItemFlags)

    def _save_gkeys_cfg(self) -> None:
        """Save G-Keys configuration for a current plane."""
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
        cell_combo: QComboBox | QWidget = self.tw_gkeys.cellWidget(currentRow, currentColumn)
        self._cell_ctrl_content_changed(text=cell_combo.currentText(), widget=cell_combo, row=currentRow, col=currentColumn)

    def _input_iface_changed_or_custom_text_changed(self) -> None:
        """
        Triggered for a radio button group and custom text.

        When:
            * New input interface is selected
            * A text is changed and a user pressed enter
            * The widget lost focus
        """
        current_cell: QComboBox | QWidget = self.tw_gkeys.cellWidget(self.current_row, self.current_col)
        current_cell_text = current_cell.currentText()
        if current_cell_text in self.ctrl_list and CTRL_LIST_SEPARATOR not in current_cell_text:
            section = self._find_section_name(ctrl_name=current_cell_text)
            key_name = str(self.device.get_key_at(row=self.current_row, col=self.current_col))
            ctrl_key = self.ctrl_input[section][current_cell_text]
            input_iface_name = self.bg_rb_input_iface.checkedButton().objectName()
            custom_value = self._get_custom_value(input_iface_name)
            self.input_reqs[self.current_plane][key_name] = GuiPlaneInputRequest.from_control_key(ctrl_key=ctrl_key, rb_iface=input_iface_name,
                                                                                                  custom_value=custom_value)

    def _copy_cell_to_row(self) -> None:
        """Copy content of current cell to whole row."""
        current_cell: QComboBox | QWidget = self.tw_gkeys.cellWidget(self.current_row, self.current_col)
        for col in set(range(self.device.cols)) - {self.current_col}:
            cell_at_column: QComboBox | QWidget = self.tw_gkeys.cellWidget(self.current_row, col)
            cell_at_column.setCurrentIndex(current_cell.currentIndex())

    def _reload_table_gkeys(self) -> None:
        """
        Reload the table with G-Keys.

        * Disconnects the currentIndexChanged signal of the combo_planes widget
        * _load_table_gkeys method to load the table with gkeys,
        * reconnects the currentIndexChanged signal of the combo_planes widget
        """
        self.plane_aliases = ['']
        self.combo_planes.currentIndexChanged.disconnect()
        self._load_table_gkeys()
        self.combo_planes.currentIndexChanged.connect(self._load_table_gkeys)

    def _get_custom_value(self, selected_rb_name: str) -> str:
        """
        Get custom value for a request depending on a currently selected action radio button.

        :param selected_rb_name: Name of radio button widget
        :return: Custom value as string
        """
        custom_value = ''
        if selected_rb_name == 'rb_custom' and self.le_custom.text():
            custom_value = self.le_custom.text() if self.le_custom.text()[-1] == '|' else f'{self.le_custom.text()}|'
        elif selected_rb_name == 'rb_set_state':
            custom_value = str(self.hs_set_state.value())
        return custom_value

    def _toggle_gui_logging(self, state: bool) -> None:
        """
        Toggle GUI logging on and off.

        :param state: State to switch to.
        """
        if state:
            LOG.parent.addHandler(self.gui_log)
        else:
            LOG.parent.removeHandler(self.gui_log)
        self.tw_main.setTabEnabled(GuiTab.debug, state)
        self.gui_log.toggle_logging(state=state)

    def _hs_debug_font_size_changed(self) -> None:
        """Change font size for debug log text edit."""
        current_font = self.te_debug.font()
        current_font.setPointSize(self.hs_debug_font_size.value())
        self.te_debug.setFont(current_font)

    # <=><=><=><=><=><=><=><=><=><=><=> dcs-bios tab <=><=><=><=><=><=><=><=><=><=><=>
    def _is_git_object_exists(self, text: str) -> bool | None:
        """
        Check if an entered git object exists.

        :param text: Git reference
        :return: True if a git object exists, False otherwise.
        """
        if self.cb_bios_live.isChecked():
            self._set_completer_for_git_ref()
            git_ref = is_git_object(repo_dir=self.bios_repo_path, git_obj=text)
            LOG.debug(f'Git reference: {text} in {self.bios_repo_path} exists: {git_ref}')
            if git_ref:
                self.le_bios_ref.setStyleSheet('')
                return True
            self.le_bios_ref.setStyleSheet('color: red;')
            return False
        return None

    def _get_bios_full_version(self, silence=True) -> str:
        """
        Get full SHA and git details the DCS-BIOS version as string.

        :param silence: Perform action with a silence
        :return: Full BIOS version
        """
        sha_commit = 'N/A'
        if self.git_exec and self.cb_bios_live.isChecked():
            try:
                sha_commit = check_github_repo(git_ref=self.le_bios_ref.text(), repo_dir=self.bios_repo_path, repo=self.le_bios_repo.text(), update=False)
            except Exception as exc:
                LOG.debug(f'{exc}')
                if not silence:
                    self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Error', message=f'\n\n{exc}\n\nTry remove directory and restart DCSpy.')
        return sha_commit

    def _cb_bios_live_toggled(self, state: bool) -> None:
        """
        Toggle between Live DCS-BIOS and regular release one.

        :param state: True if checked, False if unchecked.
        """
        if state:
            self.le_bios_ref.setEnabled(True)
            self.le_bios_repo.setEnabled(True)
            self.l_bios_ref.setEnabled(True)
            self.l_bios_repo.setEnabled(True)
            self._is_git_object_exists(text=self.le_bios_ref.text())
        else:
            self.le_bios_ref.setEnabled(False)
            self.le_bios_repo.setEnabled(False)
            self.l_bios_ref.setEnabled(False)
            self.l_bios_repo.setEnabled(False)
            self.le_bios_ref.setStyleSheet('')
        self._clean_bios_files()
        self._bios_check_clicked(silence=False)

    def _set_completer_for_git_ref(self) -> None:
        """Set-ups completer for Git references of the DCS-BIOS git repository."""
        git_refs = get_all_git_refs(repo_dir=self.bios_repo_path)
        if self._git_refs_count != len(git_refs):
            self._git_refs_count = len(git_refs)
            completer = QCompleter(git_refs)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
            self.le_bios_ref.setCompleter(completer)

    def _bios_git_repo_chnaged(self, text: str) -> None:
        """
        Show info at statusbar when BIOS Git repostory changed.

        :param text: Git repository sddress
        """
        self.le_bios_repo.setStyleSheet('')
        if self.bios_git_addr != text:
            self.statusbar.showMessage('BIOS git address changes, please click Repair')
            self.le_bios_repo.setStyleSheet('color: red;')

    # <=><=><=><=><=><=><=><=><=><=><=> check dcspy updates <=><=><=><=><=><=><=><=><=><=><=>
    def _dcspy_check_clicked(self) -> None:
        """Check a version of DCSpy and show a message box."""
        ver_string = get_version_string(repo=DCSPY_REPO_NAME, current_ver=__version__, check=True)
        self.statusbar.showMessage(ver_string)
        if 'update!' in ver_string:
            self.systray.showMessage('DCSpy', f'New: {ver_string}', QIcon(':/icons/img/edit-download.svg'))
            self._download_new_release()
        elif 'latest' in ver_string:
            self._show_message_box(kind_of=MsgBoxTypes.INFO, title='No updates', message='You are running latest version')
        elif 'failed' in ver_string:
            self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Warning', message='Unable to check DCSpy version online')

    def _download_new_release(self) -> None:
        """Download the new release if running Nuitka version or Pip version."""
        if globals().get('__compiled__', False):
            self._restart_nuitka_ver()
        else:
            self._show_message_box(kind_of=MsgBoxTypes.INFO, title='uv/pip Install', message='Use uv in console:\n\nuv tool update dcspy')

    def _restart_nuitka_ver(self) -> None:
        """Download and restart a new version of DCSpy when using an executable/nuitka version."""
        LOG.debug(f'Nuitka unpacked: {globals().get("__builtins__", {}).get("__nuitka_binary_exe", "")}')
        rel_info = check_ver_at_github(repo=DCSPY_REPO_NAME)
        asset_file = rel_info.get_asset(extension='_setup.exe')
        reply = self._show_message_box(kind_of=MsgBoxTypes.QUESTION, title='Update DCSpy',
                                       message=f'Download new version {rel_info.version} ({asset_file.size / 1_048_576:.2f} MB) and shutdown DCSpy?',
                                       defaultButton=QMessageBox.StandardButton.Yes)
        if bool(reply == QMessageBox.StandardButton.Yes):
            try:
                dst_dir = str(Path(os.environ['USERPROFILE']) / 'Desktop')
            except KeyError:
                dst_dir = 'C:\\'
            directory = self._run_file_dialog(last_dir=lambda: dst_dir, caption='Where save DCSpy release')
            try:
                download_file(url=asset_file.browser_download_url, save_path=Path(directory) / asset_file.name, progress_fn=self._progress_by_abs_value)
                result = rel_info.verify(local_file=Path(directory) / asset_file.name)
                if result[0]:
                    self._show_message_box(kind_of=MsgBoxTypes.INFO, title='Verification',
                                           message=f'Checksum verification of:\n{asset_file.name} succeed.')
                else:
                    self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Verification',
                                           message=f'Checksum verification of:\n{asset_file.name} failed:\n\n{(pformat(result[1]))}')
                LOG.info(f'Stop DCSpy {__version__}')
                sys.exit(0)
            except PermissionError as exc:
                self._show_message_box(kind_of=MsgBoxTypes.WARNING, title=exc.args[1], message=f'Can not save file:\n{exc.filename}')

    # <=><=><=><=><=><=><=><=><=><=><=> check bios updates <=><=><=><=><=><=><=><=><=><=><=>
    def _bios_check_clicked(self, silence=False) -> None:
        """
        Check the DCS-BIOS directory and perform update.

        :param silence: Perform action with silence
        """
        if not self._check_dcs_bios_path():
            return

        self._start_bios_update(silence)

    def _start_bios_update(self, silence: bool) -> None:
        """
        Make a real update of git or stable DCS-BIOS version.

        :param silence: Perform action with silence
        """
        if self.cb_bios_live.isChecked():
            clone_worker: QRunnable | WorkerSignalsMixIn = GitCloneWorker(git_ref=self.le_bios_ref.text(), bios_path=self.bios_path,
                                                                          to_path=self.bios_repo_path, repo=self.le_bios_repo.text(), silence=silence)
            signal_handlers = {
                'progress': self._progress_by_abs_value,
                'stage': self.statusbar.showMessage,
                'error': self._error_during_bios_update,
                'result': self._clone_bios_completed,
            }
            clone_worker.setup_signal_handlers(signal_handlers=signal_handlers)
            self.threadpool.start(clone_worker)
        else:
            try:
                self._check_bios_release(silence=silence)
            except ValueError as exc:
                LOG.debug('Check BIOS version', exc_info=True)
                if not silence:
                    self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Problem', message=f'Error during checking version:\n{exc}')
            self._reload_table_gkeys()

    def _check_dcs_bios_path(self) -> bool:
        """
        Check if the DCS-BIOS path fulfills two conditions.

        - Path is not empty
        - A drive letter exists in a system

        If met return True, False otherwise.

        :return: True if the path to DCS-BIOS is correct
        """
        result = True
        if self._is_dir_dcs_bios(text=self.bios_path, widget_name='le_biosdir'):
            drive_letter = self.bios_path.parts[0]
            if not Path(drive_letter).exists():
                self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Warning', message=f'Wrong drive: {drive_letter}\n\nCheck DCS-BIOS path.')
                result = False
        else:
            reply = self._show_message_box(kind_of=MsgBoxTypes.QUESTION, title='Install DCS-BIOS',
                                           message=f'There is no DCS-BIOS installed at:\n{self.bios_path}\n\nDo you want install?',
                                           defaultButton=QMessageBox.StandardButton.Yes)
            result = bool(reply == QMessageBox.StandardButton.Yes)
        return result

    def _error_during_bios_update(self, exc_tuple) -> None:
        """
        Show a message box with error details.

        :param exc_tuple: Exception tuple
        """
        exc_type, exc_val, exc_tb = exc_tuple
        LOG.debug(exc_tb)
        self._show_custom_msg_box(kind_of=QMessageBox.Icon.Critical, title='Error', text=exc_type.__name__, detail_txt=str(exc_val),
                                  info_txt=f'Try remove directory:\n{self.bios_repo_path}\nand restart DCSpy.')
        LOG.debug(f'Can not update BIOS: {exc_type}')

    def _clone_bios_completed(self, result) -> None:
        """
        Show a message box with installation details.

        :param result:
        """
        sha, silence = result
        local_bios = self._check_local_bios()
        LOG.info(f'Git DCS-BIOS: {sha} ver: {local_bios}')
        install_result = self._handling_export_lua(temp_dir=self.bios_repo_path / 'Scripts')
        install_result = f'{install_result}\n\nUsing Git/Live version.'
        self.statusbar.showMessage(sha)
        self._is_git_object_exists(text=self.le_bios_ref.text())
        self._reload_table_gkeys()
        if not silence:
            self._show_message_box(kind_of=MsgBoxTypes.INFO, title=f'Updated {self.l_bios}', message=install_result)
        self.progressbar.setValue(0)

    def _check_bios_release(self, silence=False) -> None:
        """
        Check the release version and configuration of DCS-BIOS.

        :param silence: Perform action with silence
        """
        self._check_local_bios()
        remote_bios_info = self._check_remote_bios()
        download_url = remote_bios_info.download_url(extension='.zip', file_name='BIOS')
        self.statusbar.showMessage(f'Local BIOS: {self.l_bios} | Remote BIOS: {self.r_bios}')
        correct_local_bios_ver = all([isinstance(self.l_bios, version.Version), any([self.l_bios.major, self.l_bios.minor, self.l_bios.micro])])
        correct_remote_bios_ver = all([isinstance(self.r_bios, version.Version), download_url, download_url.split('/')[-1]])

        if silence and correct_remote_bios_ver and not remote_bios_info.is_latest(current_ver=self.l_bios):
            self._update_release_bios(rel_info=remote_bios_info)
        elif not silence and correct_remote_bios_ver:
            self._ask_to_update(rel_info=remote_bios_info)
        elif not all([silence, correct_remote_bios_ver]):
            msg = self._get_problem_desc(correct_local_bios_ver, correct_remote_bios_ver)
            msg = f'{msg}\n\nUsing stable release version.'
            self._show_message_box(kind_of=MsgBoxTypes.INFO, title='Update', message=msg)

    def _get_problem_desc(self, local_bios: bool, remote_bios: bool) -> str:
        """
        Describe issues with DCS-BIOS update.

        :param local_bios: Local BIOS version
        :param remote_bios: Remote BIOS version
        :return: Description as string
        """
        lbios_chk = '\u2714 Local' if local_bios else '\u2716 Local'
        lbios_note = '' if local_bios else '\n     Check "dcsbios" path in config'
        rbios_chk = '\u2714 Remote' if remote_bios else '\u2716 Remote'
        rbios_note = '' if remote_bios else '\n     Check internet connection.'

        return f'{lbios_chk} Bios ver: {self.l_bios}{lbios_note}\n' \
               f'{rbios_chk} Bios ver: {self.r_bios}{rbios_note}'

    def _check_local_bios(self) -> version.Version:
        """
        Check the version of local BIOS.

        :return: Version object
        """
        result = check_bios_ver(bios_path=self.bios_path)
        self.l_bios = result
        return result

    def _check_remote_bios(self) -> Release:
        """
        Check the version of remote BIOS.

        :return: Release description info
        """
        release_info = check_ver_at_github(repo=BIOS_REPO_NAME)
        self.r_bios = release_info.version
        return release_info

    def _ask_to_update(self, rel_info: Release) -> None:
        """
        Ask a user if update BIOS or not.

        :param rel_info: Remote release information
        """
        asset_file = rel_info.download_url(extension='.zip', file_name='BIOS').split('/')[-1]
        msg_txt = f'You are running {self.l_bios} version.\n\n' \
                  f'Would you like to download\n' \
                  f'stable release:\n\n{asset_file}\n\n' \
                  f'and overwrite update?'
        if not rel_info.is_latest(current_ver=self.l_bios):
            msg_txt = f'You are running {self.l_bios} version.\n' \
                      f'New version {rel_info.version} available.\n' \
                      f'Released: {rel_info.published}\n\n' \
                      f'Would you like to update?'
        reply = self._show_message_box(kind_of=MsgBoxTypes.QUESTION, title='Update DCS-BIOS', message=msg_txt,
                                       defaultButton=QMessageBox.StandardButton.Yes)
        if reply == QMessageBox.StandardButton.Yes:
            self._update_release_bios(rel_info=rel_info)

    def _update_release_bios(self, rel_info: Release) -> None:
        """
        Perform update of the release version BIOS and check configuration.

        :param rel_info: Remote release information
        """
        tmp_dir = Path(gettempdir())
        download_url = rel_info.download_url(extension='.zip', file_name='BIOS')
        local_zip = tmp_dir / download_url.split('/')[-1]
        download_file(url=download_url, save_path=local_zip, progress_fn=self._progress_by_abs_value)
        LOG.debug(f'Remove DCS-BIOS from: {tmp_dir} ')
        rmtree(path=tmp_dir / 'DCS-BIOS', ignore_errors=True)
        LOG.debug(f'Unpack file: {local_zip} ')
        unpack_archive(filename=local_zip, extract_dir=tmp_dir)
        LOG.debug(f'Try remove regular DCS-BIOS directory: {self.bios_path} ')
        rmtree(path=self.bios_path, ignore_errors=True)
        LOG.debug(f'Copy DCS-BIOS to: {self.bios_path} ')
        copytree(src=tmp_dir / 'DCS-BIOS', dst=self.bios_path)
        install_result = self._handling_export_lua(tmp_dir)
        if 'github' in install_result:
            reply = self._show_message_box(kind_of=MsgBoxTypes.QUESTION, title='Open browser', message=install_result,
                                           defaultButton=QMessageBox.StandardButton.Yes)
            if reply == QMessageBox.StandardButton.Yes:
                open_new_tab(r'https://github.com/DCS-Skunkworks/DCSFlightpanels/wiki/Installation')
        else:
            local_bios = self._check_local_bios()
            self.statusbar.showMessage(f'Local BIOS: {local_bios} | Remote BIOS: {self.r_bios}')
            install_result = f'{install_result}\n\nUsing stable release version.'
            self._is_dir_dcs_bios(text=self.bios_path, widget_name='le_biosdir')
            self._show_message_box(kind_of=MsgBoxTypes.INFO, title=f'Updated {local_bios}', message=install_result)
        self.progressbar.setValue(0)

    def _handling_export_lua(self, temp_dir: Path) -> str:
        """
        Check if the Export.lua file exists and check its content.

        If not, copy Export.lua from the DCS-BIOS installation archive.

        :param temp_dir: Directory with DCS-BIOS archive
        :return: Result of checks
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

    # <=><=><=><=><=><=><=><=><=><=><=> repair bios <=><=><=><=><=><=><=><=><=><=><=>
    def _bios_repair_clicked(self) -> None:
        """
        Repair DCS-BIOS installation.

        Procedure:
        * Show a message box with a warning
        * Remove Git repo from a temporary directory (optionally)
        * Remove DCS-BIOS from the Saved Games directory
        * Install DCS-BIOS
        """
        message = f'Are you sure to remove content of:\n\n{self.bios_path}'
        reply = self._show_message_box(kind_of=MsgBoxTypes.QUESTION, title='Repair DCS-BIOS',
                                       message=message, defaultButton=QMessageBox.StandardButton.No)
        if bool(reply == QMessageBox.StandardButton.Yes):
            self._clean_bios_files()
            self._remove_dcs_bios_repo_dir()
            self._start_bios_update(silence=False)
            self.le_bios_repo.setStyleSheet('')

    def _clean_bios_files(self) -> None:
        """Clean all DCS-BIOS directories and files."""
        if self.bios_path.is_symlink():
            rm_symlink = f"(Get-Item '{self.bios_path}').Delete()"
            ps_command = f'Start-Process powershell.exe -ArgumentList "-Command {rm_symlink}" -Verb RunAs'
            LOG.debug(f'Execute: {ps_command}')
            run_command(cmd=['powershell.exe', '-Command', ps_command])
        rmtree(path=self.bios_path, ignore_errors=True)

    def _remove_dcs_bios_repo_dir(self) -> None:
        """Remove the DCS-BIOS repository directory."""
        if self.cb_bios_live.isChecked():
            return_code = run_command(cmd=['attrib', '-R', '-H', '-S', fr'{self.bios_repo_path}\*.*', '/S', '/D'])
            try:
                rmtree(self.bios_repo_path, ignore_errors=False)
            except FileNotFoundError as err:
                LOG.debug(f'Try remove DCS-BIOS old repo\n{err}', exc_info=True)
            LOG.debug(f'Clean up old DCS-BIOS git repository, RC: {return_code}')

    # <=><=><=><=><=><=><=><=><=><=><=> start/stop <=><=><=><=><=><=><=><=><=><=><=>
    def _stop_clicked(self) -> None:
        """Set event to stop DCSpy."""
        self.run_in_background(job=partial(self._fake_progress, total_time=0.3),
                               signal_handlers={'progress': self._progress_by_abs_value})
        for rb_key in self.bg_rb_device.buttons():
            if not rb_key.isChecked():
                rb_key.setEnabled(True)
        self.statusbar.showMessage('Start again or close DCSpy')
        self.pb_start.setEnabled(True)
        self.a_start.setEnabled(True)
        self.pb_stop.setEnabled(False)
        self.a_stop.setEnabled(False)
        self.le_dcsdir.setEnabled(True)
        self.le_biosdir.setEnabled(True)
        self.gb_fonts.setEnabled(True)
        if self.rb_g19.isChecked():
            self.cb_ded_font.setEnabled(True)
        self.event_set()

    def _start_clicked(self) -> None:
        """Run real application in thread."""
        LOG.debug(f'Local DCS-BIOS version: {self._check_local_bios()}')
        self.run_in_background(job=partial(self._fake_progress, total_time=0.5),
                               signal_handlers={'progress': self._progress_by_abs_value})
        for rb_key in self.bg_rb_device.buttons():
            if not rb_key.isChecked():
                rb_key.setEnabled(False)
        if self.device.lcd_info.type != LcdType.NONE:
            ded_font = True if self.cb_ded_font.isChecked() and self.device.lcd_info.type == LcdType.COLOR else False
            fonts_cfg = FontsConfig(name=self.le_font_name.text(), ded_font=ded_font,
                                    **getattr(self, f'{self.device.lcd_name}_font'))
            self.device.lcd_info.set_fonts(fonts_cfg)
        self.event: Event = Event()
        app_params = {'model': self.device, 'event': self.event}
        app_thread = Thread(target=DCSpyStarter(**app_params))
        app_thread.name = 'dcspy-app'
        LOG.debug(f'Starting thread {app_thread} for: {app_params}')
        self.pb_start.setEnabled(False)
        self.a_start.setEnabled(False)
        self.pb_stop.setEnabled(True)
        self.a_stop.setEnabled(True)
        self.le_dcsdir.setEnabled(False)
        self.le_biosdir.setEnabled(False)
        self.gb_fonts.setEnabled(False)
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
        try:
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
            self.mono_font = {'large': int(cfg['font_mono_l']), 'medium': int(cfg['font_mono_m']), 'small': int(cfg['font_mono_s'])}
            self.color_font = {'large': int(cfg['font_color_l']), 'medium': int(cfg['font_color_m']), 'small': int(cfg['font_color_s'])}
            getattr(self, f'rb_{cfg["device"].lower()}').toggle()
            self.le_dcsdir.setText(cfg['dcs'])
            self.le_biosdir.setText(cfg['dcsbios'])
            self.le_bios_ref.setText(cfg['git_bios_ref'])
            self.le_bios_repo.setText(cfg['git_bios_repo'])
            self.cb_bios_live.setChecked(cfg['git_bios'])
            self.addDockWidget(Qt.DockWidgetArea(int(cfg['gkeys_area'])), self.dw_gkeys)
            self.dw_gkeys.setFloating(bool(cfg['gkeys_float']))
            self.addToolBar(Qt.ToolBarArea(int(cfg['toolbar_area'])), self.toolbar)
            getattr(self, icon_map.get(cfg['toolbar_style'], 'a_icons_only')).setChecked(True)
            color_mode: QAction = getattr(self, f'a_mode_{cfg["color_mode"]}')
            color_mode.setChecked(True)
            self._switch_color_mode(color_mode)
            self.tw_main.setTabEnabled(GuiTab.debug, cfg['gui_debug'])
            self.cb_debug_enable.setChecked(cfg['gui_debug'])
            self.hs_debug_font_size.setValue(cfg['debug_font_size'])
        except (TypeError, AttributeError, ValueError) as exc:
            LOG.warning(exc, exc_info=True)
            self._reset_defaults_cfg()

    def save_configuration(self) -> None:
        """Save configuration from GUI."""
        cfg = {
            'api_ver': __version__,
            'device': self.device.klass,
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
            'git_bios_ref': self.le_bios_ref.text(),
            'git_bios_repo': self.le_bios_repo.text(),
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
            'gui_debug': self.cb_debug_enable.isChecked(),
            'debug_font_size': self.hs_debug_font_size.value(),
        }
        if self.device.lcd_info.type == LcdType.COLOR:
            font_cfg = {'font_color_l': self.hs_large_font.value(),
                        'font_color_m': self.hs_medium_font.value(),
                        'font_color_s': self.hs_small_font.value()}
        else:
            font_cfg = {'font_mono_l': self.hs_large_font.value(),
                        'font_mono_m': self.hs_medium_font.value(),
                        'font_mono_s': self.hs_small_font.value()}

        for mode_menu in [self.a_mode_system, self.a_mode_dark, self.a_mode_light]:
            if mode_menu.isChecked():
                color_mode = mode_menu.text().lower()
                break
        else:
            color_mode = 'system'

        cfg.update(font_cfg)
        cfg.update({'color_mode': color_mode})
        save_yaml(data=cfg, full_path=default_yaml)

    def _reset_defaults_cfg(self) -> None:
        """Set defaults and stop the application."""
        save_yaml(data=defaults_cfg, full_path=default_yaml)
        self.config = load_yaml(full_path=default_yaml)
        self.apply_configuration(self.config)
        for name in ['large', 'medium', 'small']:
            getattr(self, f'hs_{name}_font').setValue(getattr(self, f'{self.device.lcd_name}_font')[name])
        self._show_message_box(kind_of=MsgBoxTypes.WARNING, title='Reset settings',
                               message='All settings will be reset to default values.\nDCSpy will to be close.\nIt could be necessary start DCSpy manually!')
        self.close()

    # <=><=><=><=><=><=><=><=><=><=><=> others <=><=><=><=><=><=><=><=><=><=><=>
    @property
    def current_plane(self) -> str:
        """
        Get current plane from combo box.

        :return: Plane name as string
        """
        return self.combo_planes.currentText()

    @property
    def bios_path(self) -> Path:
        """
        Get the path to the DCS-BIOS directory.

        :return: Full path as Path
        """
        return Path(self.le_biosdir.text())

    @property
    def bios_repo_path(self) -> Path:
        """
        Get the path to DCS-BIOS repository.

        :return: Full path as Path
        """
        return Path(self.le_biosdir.text()).parents[1] / 'dcs-bios'

    @property
    def dcs_path(self) -> Path:
        """
        Get a path to the DCS World directory.

        :return: Full path as Path
        """
        return Path(self.le_dcsdir.text())

    # <=><=><=><=><=><=><=><=><=><=><=> helpers <=><=><=><=><=><=><=><=><=><=><=>
    def run_in_background(self, job: partial | Callable, signal_handlers: dict[str, Callable]) -> None:
        """
        Worker with signals callback to schedule a GUI job in the background.

        Parameter `signal_handlers` is a dict with signals from WorkerSignals.
        Possible signals are: `finished`, `error`, `result`, `progress`.
        Values in dict are methods/callables as handlers/callbacks for a particular signal.

        :param job: GUI method or function to run in background
        :param signal_handlers: Signals as keys: finished, error, result, progress and values as callable
        """
        progress = True if 'progress' in signal_handlers.keys() else False
        worker: QRunnable | WorkerSignalsMixIn = Worker(func=job, with_progress=progress)
        worker.setup_signal_handlers(signal_handlers=signal_handlers)
        if isinstance(job, partial):
            job_name = job.func.__name__
            args = job.args
            kwargs = job.keywords
        else:
            job_name = job.__name__
            args = ()
            kwargs = {}
        signals = {signal: handler.__name__ for signal, handler in signal_handlers.items()}
        LOG.debug(f'bg job for: {job_name} args: {args} kwargs: {kwargs} signals {signals}')
        self.threadpool.start(worker)

    @staticmethod
    def _fake_progress(progress_callback: SignalInstance, total_time: float, steps: int = 100,
                       clean_after: bool = True, **kwargs) -> None:
        """
        Make fake progress for the progressbar.

        :param progress_callback: Signal to update progress bar
        :param total_time: Time for fill-up whole bar (in seconds)
        :param steps: Number of steps (default 100)
        :param clean_after: Clean progress bar when finish
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
        Fetch various system-related data.

        :param silence: Perform action with silence
        :return: SystemData named tuple with all data
        """
        system, _, release, ver, _, proc = uname()
        dcs_ver = check_dcs_ver(Path(self.config['dcs']))
        dcspy_ver = get_version_string(repo=DCSPY_REPO_NAME, current_ver=__version__, check=self.config['check_ver'])
        bios_ver = str(self._check_local_bios())
        dcs_bios_ver = self._get_bios_full_version(silence=silence)
        git_ver = 'Not installed'
        if self.git_exec:
            from git import cmd
            git_ver = '.'.join([str(i) for i in cmd.Git().version_info])
        return SystemData(system=system, release=release, ver=ver, proc=proc, dcs_ver=dcs_ver,
                          dcspy_ver=dcspy_ver, bios_ver=bios_ver, dcs_bios_ver=dcs_bios_ver, git_ver=git_ver)

    def _run_file_dialog(self, last_dir: Callable[..., str], widget_name: str | None = None, caption: str='Open Directory') -> str:
        """
        Open/save dialog to select a file or a folder.

        :param last_dir: Function which returns the last selected directory
        :param widget_name: widget name which should be updated
        :param caption: Tittle for the dialog
        :return: Full path to directory
        """
        result_path = QFileDialog.getExistingDirectory(self, caption=caption, dir=last_dir(), options=QFileDialog.Option.ShowDirsOnly)
        if widget_name is not None and result_path:
            getattr(self, widget_name).setText(result_path)
        return result_path

    @staticmethod
    def _get_style_for_combobox(key: AnyButton, fg: str) -> str:
        """
        Get style for QComboBox with foreground color.

        Colors:
        - light green - G-Keys
        - light yellow - Mouse buttons
        - light blue - LCD buttons

        :param key: LcdButton, Gkey or MouseButton
        :param fg: color as string
        :return: style sheet string
        """
        bg = ''
        if isinstance(key, Gkey):
            bg = 'lightgreen'
        elif isinstance(key, MouseButton):
            bg = 'lightyellow'
        elif isinstance(key, LcdButton):
            bg = 'lightblue'
        return f'QComboBox{{color: {fg};background-color: {bg};}} QComboBox QAbstractItemView {{background-color: {bg};}}'

    def _show_message_box(self, kind_of: MsgBoxTypes, title: str, message: str = '', **kwargs) -> QMessageBox.StandardButton:
        """
        Show any QMessageBox delivered with Qt.

        :param kind_of: One of MsgBoxTypes: `information`, `question`, `warning`, `critical`, `about` or `aboutQt`
        :param title: Title of modal window
        :param message: A text of a message, default is empty
        :param kwargs: Additional keyword arguments for customizing the message box
        :return: The standard button clicked by the user
        """
        result = QMessageBox.StandardButton.NoButton
        if not NO_MSG_BOX:
            message_box = getattr(QMessageBox, kind_of.value)
            if kind_of == MsgBoxTypes.ABOUT_QT:
                result = message_box(self, title, **kwargs)
            else:
                result = message_box(self, title, message, **kwargs)
        return result

    def _show_custom_msg_box(self, kind_of: QMessageBox.Icon, title: str, text: str, info_txt: str, detail_txt: str | None = None,
                             buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton) -> int | None:
        """
        Show a custom message box with hidden text.

        :param title: Title
        :param text: First section
        :param info_txt: Second section
        :param detail_txt: Hidden text
        :param buttons: Collection of standard buttons in the message box
        :return: Integer value of pushed buttons
        """
        if not NO_MSG_BOX:
            msg = QMessageBox(parent=self)
            msg.setText(text)
            msg.setIcon(kind_of)
            msg.setWindowTitle(title)
            msg.setInformativeText(info_txt)
            if detail_txt:
                msg.setDetailedText(detail_txt)
            if buttons:
                msg.setStandardButtons(buttons)
            return msg.exec()
        return None

    def event_set(self) -> None:
        """Set event to close the running thread."""
        self.event.set()

    def activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Signal of activation.

        :param reason: Reason of activation
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def _show_toolbar(self) -> None:
        """Toggles show and hide the toolbar."""
        if self.a_show_toolbar.isChecked():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    def _show_gkeys_dock(self) -> None:
        """Toggles show and hide G-Keys dock."""
        if self.a_show_gkeys.isChecked():
            self.dw_gkeys.show()
        else:
            self.dw_gkeys.hide()

    def _show_device_dock(self) -> None:
        """Toggles between show and hide a device dock."""
        if self.a_show_device.isChecked():
            self.dw_device.show()
        else:
            self.dw_device.hide()

    @Slot(bool)
    def _close_dock_widget(self, visible: bool, widget: str) -> None:
        """
        Close the dock widget and check menu/toolbar item.

        :param visible: Is dock visible
        :param widget: Widget name
        """
        action = getattr(self, f'a_show_{widget}')
        if not visible:
            action.setChecked(False)
        else:
            action.setChecked(True)

    @staticmethod
    def _switch_color_mode(action: QAction) -> None:
        """
        Switch between light and dark color mode.

        :param action: Action from the menu
        """
        mode = action.text()
        style_hints: QStyleHints = QGuiApplication.styleHints()
        if mode == 'System':
            mode = detect_system_color_mode()
        style_hints.setColorScheme(getattr(Qt.ColorScheme, mode))

    def _find_children(self) -> None:
        """Find all widgets in the main window."""
        self.statusbar: QStatusBar = self.findChild(QStatusBar, 'statusbar')
        self.progressbar: QProgressBar = self.findChild(QProgressBar, 'progressbar')
        self.toolbar: QToolBar = self.findChild(QToolBar, 'toolbar')
        self.tw_gkeys: QTableWidget = self.findChild(QTableWidget, 'tw_gkeys')
        self.sp_completer: QSpinBox = self.findChild(QSpinBox, 'sp_completer')
        self.tw_main: QTabWidget = self.findChild(QTabWidget, 'tw_main')
        self.gb_fonts: QGroupBox = self.findChild(QGroupBox, 'gb_fonts')
        self.toolBox: QToolBox = self.findChild(QToolBox, 'toolBox')
        self.te_debug: QTextEdit = self.findChild(QTextEdit, 'te_debug')

        self.combo_planes: QComboBox = self.findChild(QComboBox, 'combo_planes')
        self.combo_search: QComboBox = self.findChild(QComboBox, 'combo_search')

        self.dw_gkeys: QDockWidget = self.findChild(QDockWidget, 'dw_gkeys')
        self.dw_device: QDockWidget = self.findChild(QDockWidget, 'dw_device')

        self.l_keyboard: QLabel = self.findChild(QLabel, 'l_keyboard')
        self.l_large: QLabel = self.findChild(QLabel, 'l_large')
        self.l_medium: QLabel = self.findChild(QLabel, 'l_medium')
        self.l_small: QLabel = self.findChild(QLabel, 'l_small')
        self.l_category: QLabel = self.findChild(QLabel, 'l_category')
        self.l_description: QLabel = self.findChild(QLabel, 'l_description')
        self.l_identifier: QLabel = self.findChild(QLabel, 'l_identifier')
        self.l_range: QLabel = self.findChild(QLabel, 'l_range')
        self.l_bios_ref: QLabel = self.findChild(QLabel, 'l_bios_ref')
        self.l_bios_repo: QLabel = self.findChild(QLabel, 'l_bios_repo')

        self.a_start: QAction = self.findChild(QAction, 'a_start')
        self.a_stop: QAction = self.findChild(QAction, 'a_stop')
        self.a_quit: QAction = self.findChild(QAction, 'a_quit')
        self.a_save_plane: QAction = self.findChild(QAction, 'a_save_plane')
        self.a_reset_defaults: QAction = self.findChild(QAction, 'a_reset_defaults')
        self.a_show_toolbar: QAction = self.findChild(QAction, 'a_show_toolbar')
        self.a_show_gkeys: QAction = self.findChild(QAction, 'a_show_gkeys')
        self.a_show_device: QAction = self.findChild(QAction, 'a_show_device')
        self.a_about_dcspy: QAction = self.findChild(QAction, 'a_about_dcspy')
        self.a_about_qt: QAction = self.findChild(QAction, 'a_about_qt')
        self.a_report_issue: QAction = self.findChild(QAction, 'a_report_issue')
        self.a_dcspy_updates: QAction = self.findChild(QAction, 'a_dcspy_updates')
        self.a_bios_updates: QAction = self.findChild(QAction, 'a_bios_updates')
        self.a_donate: QAction = self.findChild(QAction, 'a_donate')
        self.a_discord: QAction = self.findChild(QAction, 'a_discord')
        self.a_icons_only: QAction = self.findChild(QAction, 'a_icons_only')
        self.a_text_only: QAction = self.findChild(QAction, 'a_text_only')
        self.a_text_beside: QAction = self.findChild(QAction, 'a_text_beside')
        self.a_text_under: QAction = self.findChild(QAction, 'a_text_under')
        self.a_mode_light: QAction = self.findChild(QAction, 'a_mode_light')
        self.a_mode_dark: QAction = self.findChild(QAction, 'a_mode_dark')
        self.a_mode_system: QAction = self.findChild(QAction, 'a_mode_system')

        self.pb_start: QPushButton = self.findChild(QPushButton, 'pb_start')
        self.pb_stop: QPushButton = self.findChild(QPushButton, 'pb_stop')
        self.pb_close: QPushButton = self.findChild(QPushButton, 'pb_close')
        self.pb_dcsdir: QPushButton = self.findChild(QPushButton, 'pb_dcsdir')
        self.pb_biosdir: QPushButton = self.findChild(QPushButton, 'pb_biosdir')
        self.pb_collect_data: QPushButton = self.findChild(QPushButton, 'pb_collect_data')
        self.pb_copy: QPushButton = self.findChild(QPushButton, 'pb_copy')
        self.pb_save: QPushButton = self.findChild(QPushButton, 'pb_save')
        self.pb_dcspy_check: QPushButton = self.findChild(QPushButton, 'pb_dcspy_check')
        self.pb_bios_check: QPushButton = self.findChild(QPushButton, 'pb_bios_check')
        self.pb_bios_repair: QPushButton = self.findChild(QPushButton, 'pb_bios_repair')

        self.cb_autostart: QCheckBox = self.findChild(QCheckBox, 'cb_autostart')
        self.cb_show_gui: QCheckBox = self.findChild(QCheckBox, 'cb_show_gui')
        self.cb_check_ver: QCheckBox = self.findChild(QCheckBox, 'cb_check_ver')
        self.cb_ded_font: QCheckBox = self.findChild(QCheckBox, 'cb_ded_font')
        self.cb_lcd_screenshot: QCheckBox = self.findChild(QCheckBox, 'cb_lcd_screenshot')
        self.cb_verbose: QCheckBox = self.findChild(QCheckBox, 'cb_verbose')
        self.cb_autoupdate_bios: QCheckBox = self.findChild(QCheckBox, 'cb_autoupdate_bios')
        self.cb_bios_live: QCheckBox = self.findChild(QCheckBox, 'cb_bios_live')
        self.cb_debug_enable: QCheckBox = self.findChild(QCheckBox, 'cb_debug_enable')

        self.le_dcsdir: QLineEdit = self.findChild(QLineEdit, 'le_dcsdir')
        self.le_biosdir: QLineEdit = self.findChild(QLineEdit, 'le_biosdir')
        self.le_font_name: QLineEdit = self.findChild(QLineEdit, 'le_font_name')
        self.le_bios_ref: QLineEdit = self.findChild(QLineEdit, 'le_bios_ref')
        self.le_bios_repo: QLineEdit = self.findChild(QLineEdit, 'le_bios_repo')
        self.le_custom: QLineEdit = self.findChild(QLineEdit, 'le_custom')

        self.rb_g19: QRadioButton = self.findChild(QRadioButton, 'rb_g19')
        self.rb_g13: QRadioButton = self.findChild(QRadioButton, 'rb_g13')
        self.rb_g15v1: QRadioButton = self.findChild(QRadioButton, 'rb_g15v1')
        self.rb_g15v2: QRadioButton = self.findChild(QRadioButton, 'rb_g15v2')
        self.rb_g510: QRadioButton = self.findChild(QRadioButton, 'rb_g510')
        self.rb_rb_g910: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g910')
        self.rb_rb_g710: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g710')
        self.rb_rb_g110: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g110')
        self.rb_rb_g103: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g103')
        self.rb_rb_g105: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g105')
        self.rb_rb_g11: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g11')
        self.rb_rb_g633: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g633')
        self.rb_rb_g35: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g35')
        self.rb_rb_g930: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g930')
        self.rb_rb_g933: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g933')
        self.rb_rb_g600: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g600')
        self.rb_rb_g300: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g300')
        self.rb_rb_g400: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g400')
        self.rb_rb_g700: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g700')
        self.rb_rb_g9: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g9')
        self.rb_rb_mx518: QRadioButton = self.findChild(QRadioButton, 'rb_rb_mx518')
        self.rb_rb_g402: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g402')
        self.rb_rb_g502: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g502')
        self.rb_rb_g602: QRadioButton = self.findChild(QRadioButton, 'rb_rb_g602')
        self.rb_action: QRadioButton = self.findChild(QRadioButton, 'rb_action')
        self.rb_fixed_step_inc: QRadioButton = self.findChild(QRadioButton, 'rb_fixed_step_inc')
        self.rb_fixed_step_dec: QRadioButton = self.findChild(QRadioButton, 'rb_fixed_step_dec')
        self.rb_set_state: QRadioButton = self.findChild(QRadioButton, 'rb_set_state')
        self.rb_cycle: QRadioButton = self.findChild(QRadioButton, 'rb_cycle')
        self.rb_variable_step_plus: QRadioButton = self.findChild(QRadioButton, 'rb_variable_step_plus')
        self.rb_variable_step_minus: QRadioButton = self.findChild(QRadioButton, 'rb_variable_step_minus')
        self.rb_push_button: QRadioButton = self.findChild(QRadioButton, 'rb_push_button')
        self.rb_custom: QRadioButton = self.findChild(QRadioButton, 'rb_custom')

        self.hs_large_font: QSlider = self.findChild(QSlider, 'hs_large_font')
        self.hs_medium_font: QSlider = self.findChild(QSlider, 'hs_medium_font')
        self.hs_small_font: QSlider = self.findChild(QSlider, 'hs_small_font')
        self.hs_set_state: QSlider = self.findChild(QSlider, 'hs_set_state')
        self.hs_debug_font_size: QSlider = self.findChild(QSlider, 'hs_debug_font_size')


class AboutDialog(QDialog):
    """About dialog."""
    def __init__(self, parent) -> None:
        """Dcspy about dialog window."""
        super().__init__(parent)
        self.parent: DcsPyQtGui | QWidget = parent
        UiLoader().load_ui(':/ui/ui/about.ui', self)
        self.l_info: QLabel = self.findChild(QLabel, 'l_info')
        self.tb_licenses: QTextBrowser = self.findChild(QTextBrowser, 'tb_licenses')

    def showEvent(self, event: QShowEvent) -> None:
        """Prepare all information about DCSpy application."""
        super().showEvent(event)
        self._prepare_about()
        self._prepare_licenses()

    def _prepare_about(self) -> None:
        """Prepare text information about DCSpy."""
        d = self.parent.fetch_system_data(silence=False)
        text = '<html><head/><body><p>'
        text += '<b>Author</b>: <a href="https://github.com/emcek">Michal Plichta</a>'
        text += f'<br><b>Project</b>: <a href="https://github.com/{DCSPY_REPO_NAME}/">{DCSPY_REPO_NAME}</a>'
        text += '<br><b>Docs</b>: <a href="https://dcspy.readthedocs.io/en/latest/">docs</a>'
        text += '<br><b>Discord</b>: <a href="https://discord.gg/SP5Yjx3">discord.gg/SP5Yjx3</a>'
        text += f'<br><b>Issues</b>: <a href="https://github.com/{DCSPY_REPO_NAME}/issues">report issue</a>'
        text += f'<br><b>System</b>: {d.system}{d.release} ver. {d.ver} ({architecture()[0]})'
        text += f'<br><b>Processor</b>: {d.proc}'
        text += f'<br><b>Python</b>: {python_implementation()}-{python_version()}'
        text += f'<br><b>Config</b>: <a href="file:///{default_yaml.parent}">{default_yaml.name}</a>'
        text += f'<br><b>Git</b>: {d.git_ver}'
        text += f'<br><b>PySide6</b>: {pyside6_ver} / <b>Qt</b>: {qt6_ver}'
        text += f'<br><b>DCSpy</b>: {d.dcspy_ver}'
        text += f'<br><b>DCS-BIOS</b>: <a href="https://github.com/DCS-Skunkworks/dcs-bios/releases">{d.bios_ver}</a> '
        if d.sha != 'N/A':
            text += f'<b>SHA:</b> <a href="https://github.com/DCS-Skunkworks/dcs-bios/commit/{d.sha}">{d.dcs_bios_ver}</a>'
        else:
            text += f'<b>SHA:</b> {d.dcs_bios_ver}</a>'
        text += f'<br><b>DCS World</b>: <a href="https://www.digitalcombatsimulator.com/en/news/changelog/stable/{d.dcs_ver}/">{d.dcs_ver}</a>'
        text += '</p></body></html>'
        self.l_info.setText(text)

    def _prepare_licenses(self) -> None:
        """Prepare licenses text."""
        packages = {
            'cffi': {'webpage': 'https://github.com/python-cffi/cffi', 'license': 'MIT'},
            'eval-type-backport': {'webpage': 'https://github.com/alexmojaki/eval_type_backport', 'license': 'MIT'},
            'GitPython': {'webpage': 'https://github.com/gitpython-developers/GitPython', 'license': 'BSD-3-Clause'},
            'Lupa': {'webpage': 'https://github.com/scoder/lupa', 'license': 'MIT style'},
            'packaging': {'webpage': 'https://github.com/pypa/packaging', 'license': 'Apache-2.0 OR BSD-2-Clause'},
            'Pillow': {'webpage': 'https://github.com/python-pillow/Pillow', 'license': 'MIT-CMU'},
            'Pydantic': {'webpage': 'https://github.com/pydantic/pydantic', 'license': 'MIT'},
            'PySide6': {'webpage': 'https://wiki.qt.io/Qt_for_Python', 'license': 'LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only'},
            'PyYAML': {'webpage': 'https://github.com/yaml/pyyaml', 'license': 'MIT'},
            'Requests': {'webpage': 'https://github.com/psf/requests', 'license': 'Apache-2.0'},
            'Typing Extensions': {'webpage': 'https://github.com/python/typing_extensions', 'license': 'PSF-2.0'},
            'FalconDED by "uri_ba"': {'webpage': 'https://fontstruct.com/fontstructions/show/1014500', 'license': 'CC BY-NC-SA 3.0'},
        }
        text = '<html><head/><body>'
        text += '<p>DCSpy heavily relies on other open source software listed below.</p>'
        for package, data in packages.items():
            text += f'<p><b>{package}</b>'
            text += f'<br>Web page: <a href="{data["webpage"]}">{data["webpage"]}</a>'
            text += f'<br>License: {data["license"]}</p>'
        text += '</body></html>'
        self.tb_licenses.setText(text)

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:
    * finished - no data
    * error - tuple with exctype, value, traceback.format_exc()
    * result - object/any type - data returned from processing
    * progress - float between zero (0) and one (1) as an indication of progress
    * stage - string with current stage
    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)
    stage = Signal(str)


class WorkerSignalsMixIn:
    """Worker signals Mixin."""

    def __init__(self) -> None:
        """Signal handler for WorkerSignals."""
        self.signals = WorkerSignals()

    def setup_signal_handlers(self, signal_handlers: dict[str, Callable[[Any], None]]) -> None:
        """
        Connect handlers to signals.

        :param signal_handlers: Dict with signals and handlers as value.
        """
        for signal, handler in signal_handlers.items():
            getattr(self.signals, signal).connect(handler)


class Worker(QRunnable, WorkerSignalsMixIn):
    """Runnable worker."""

    def __init__(self, func: partial, with_progress: bool) -> None:
        """
        Worker thread.

        Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
        :param func: The function callback to run on a worker thread
        """
        super().__init__()
        self.func = func
        if with_progress:
            self.func.keywords['progress_callback'] = self.signals.progress

    @Slot()
    def run(self) -> None:
        """Run the worker function."""
        try:
            result = self.func()
        except Exception:
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class GitCloneWorker(QRunnable, WorkerSignalsMixIn):
    """Worker for git clone with reporting progress."""

    def __init__(self, git_ref: str, bios_path: Path, to_path: Path, repo: str, silence: bool = False) -> None:
        """
        Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

        :param git_ref: Git reference
        :param repo: Valid git repository address
        :param bios_path: Path to DCS-BIOS
        :param to_path: Path to which the repository should be cloned to
        :param silence: Perform action with silence
        """
        super().__init__()
        self.git_ref = git_ref
        self.repo = repo
        self.to_path = to_path
        self.bios_path = bios_path
        self.silence = silence

    @Slot()
    def run(self) -> None:
        """Clone the repository and report progress using a special object CloneProgress."""
        try:
            sha = check_github_repo(git_ref=self.git_ref, update=True, repo=self.repo, repo_dir=self.to_path,
                                    progress=CloneProgress(self.signals.progress, self.signals.stage))
            if not self.bios_path.is_symlink():
                target = self.to_path / 'Scripts' / 'DCS-BIOS'
                cmd_symlink = f'"New-Item -ItemType SymbolicLink -Path \\"{self.bios_path}\\" -Target \\"{target}\\"'
                ps_command = f"Start-Process powershell.exe -ArgumentList '-Command {cmd_symlink}' -Verb RunAs"
                LOG.debug(f'Make symbolic link: {ps_command}')
                run_command(cmd=['powershell.exe', '-Command', ps_command])
                sleep(0.8)
            LOG.debug(f'Directory: {self.bios_path} is symbolic link: {self.bios_path.is_symlink()}')
        except Exception:
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit((sha, self.silence))
        finally:
            self.signals.finished.emit()


class UiLoader(QUiLoader):
    """UI file loader."""
    _base_instance = None

    def createWidget(self, classname: str, parent: QWidget | None = None, name='') -> QWidget:
        """
        Create a widget.

        :param classname: Class name
        :param parent: Parent
        :param name: Name
        :return: QWidget
        """
        if parent is None and self._base_instance is not None:
            widget = self._base_instance
        else:
            widget = super().createWidget(classname, parent, name)
            if self._base_instance is not None:
                setattr(self._base_instance, name, widget)
        return widget

    def load_ui(self, ui_path: str | bytes | Path, base_instance=None) -> QWidget:
        """
        Load a UI file.

        :param ui_path: Path to a UI file
        :param base_instance:
        :return: QWidget
        """
        self._base_instance = base_instance
        ui_file = QFile(ui_path)
        ui_file.open(QIODevice.OpenModeFlag.ReadOnly)
        try:
            widget = self.load(ui_file)
            QMetaObject.connectSlotsByName(widget)
            return widget
        finally:
            ui_file.close()


class QTextEditLogHandler(Handler):
    """GUI log handler."""
    colors: ClassVar[dict[str, QColor]] = {
        'DEBUG': QColorConstants.Svg.black,
        'INFO': QColorConstants.Svg.green,
        'WARNING': QColorConstants.Svg.darkorange,
        'ERROR': QColorConstants.Svg.red,
        'CRITICAL': QColorConstants.Svg.blue
    }

    def __init__(self, text_widget: QTextEdit) -> None:
        """
        Log handler for GUI application.

        :param text_widget: widget to emit logs to.
        """
        super().__init__()
        self.text_widget = text_widget
        self.paused = False

    def emit(self, record: LogRecord) -> None:
        """
        Emit a log record.

        :param record: LogRecord instance.
        """
        if self.paused:
            return
        cursor = self.text_widget.textCursor()
        text_format = QTextCharFormat()
        text_format.setForeground(self.colors.get(record.levelname, QColorConstants.Svg.black))
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(f'{self.format(record)}\n', text_format)
        self.text_widget.setTextCursor(cursor)

    def toggle_logging(self, state: bool) -> None:
        """
        Toggle a logging state on and off.

        :param state: State of logging
        """
        self.paused = not state
