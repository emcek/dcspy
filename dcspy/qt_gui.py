import os
import shutil
import traceback
import webbrowser
from functools import partial
from importlib import import_module
from logging import getLogger
from pathlib import Path
from sys import exc_info
from threading import Event, Thread
from time import sleep
from typing import Callable, Dict, Optional, Union

import qtawesome
from PySide6 import QtCore, QtUiTools, QtWidgets
from PySide6.QtGui import QAction, QIcon

from dcspy import LCD_TYPES, LOCAL_APPDATA, qtgui_rc
from dcspy.models import KeyboardModel
from dcspy.starter import dcspy_run
from dcspy.utils import (collect_debug_data, defaults_cfg, get_default_yaml,
                         load_cfg, save_cfg)

_ = qtgui_rc  # prevent to remove import statement accidentally
__version__ = '2.3.1'
LOG = getLogger(__name__)


class DcsPyQtGui(QtWidgets.QMainWindow):
    """PySide6 GUI for DCSpy."""

    def __init__(self) -> None:
        """PySide6 GUI for DCSpy."""
        super().__init__()
        UiLoader().loadUi(':/ui/ui/qtdcs.ui', self)
        self._find_children()
        self.threadpool = QtCore.QThreadPool.globalInstance()
        LOG.debug(f'QThreadPool with {self.threadpool.maxThreadCount()} thread(s)')
        self.event = Event()
        self.keyboard = KeyboardModel(name='', klass='', modes=0, gkeys=0, lcdkeys='', lcd='')
        self.mono_font = {'large': 0, 'medium': 0, 'small': 0}
        self.color_font = {'large': 0, 'medium': 0, 'small': 0}
        self.current_row = -1
        self.current_col = -1
        self.cfg_file = get_default_yaml(local_appdata=LOCAL_APPDATA)
        self.config = load_cfg(filename=self.cfg_file)
        self.apply_configuration(cfg=self.config)
        self._visible_items = 0
        self._init_menu_bar()
        self._init_settings()
        self._init_gkeys()
        self._init_keyboards()
        self._init_autosave()

        # self._set_icons()
        if self.config.get('autostart', False):
            self._start_clicked()
        self.statusbar.showMessage(f'ver. {__version__}')

    def _init_menu_bar(self) -> None:
        """Initialize of menubar."""
        self.a_reset_defaults.triggered.connect(self._reset_defaults_cfg)
        self.a_quit.triggered.connect(self.close)
        self.a_show_toolbar.triggered.connect(self._show_toolbar)
        self.a_report_issue.triggered.connect(self._report_issue)
        # self.actionAboutDCSpy.triggered.connect(AboutDialog(self).open)
        self.a_about_qt.triggered.connect(partial(self._show_message_box, kind_of='aboutQt', title='About Qt'))
        self.a_check_updates.triggered.connect(self.check_updates)

    def _init_settings(self) -> None:
        """Initialize of settings."""
        self.pb_dcsdir.clicked.connect(partial(self._run_file_dialog, for_load=True, for_dir=True, last_dir=lambda: 'C:\\', widget_name='le_dcsdir'))
        self.pb_biosdir.clicked.connect(partial(self._run_file_dialog, for_load=True, for_dir=True, last_dir=lambda: 'D:\\', widget_name='le_biosdir'))
        self.pb_collect_data.clicked.connect(self._collect_data_clicked)
        self.pb_start.clicked.connect(self._start_clicked)
        self.pb_stop.clicked.connect(self._stop_clicked)

    def _init_autosave(self) -> None:
        """Initialize of autosave."""
        self.cb_autostart.toggled.connect(self.save_configuration)
        self.cb_show_gui.toggled.connect(self.save_configuration)
        self.cb_check_ver.toggled.connect(self.save_configuration)
        self.cb_ded_font.toggled.connect(self.save_configuration)
        self.cb_lcd_screenshot.toggled.connect(self.save_configuration)
        self.cb_verbose.toggled.connect(self.save_configuration)
        self.cb_autoupdate_bios.toggled.connect(self.save_configuration)
        self.cb_bios_live.toggled.connect(self.save_configuration)

        self.le_dcsdir.textEdited.connect(self.save_configuration)
        self.le_biosdir.textEdited.connect(self.save_configuration)
        self.le_font_name.textEdited.connect(self.save_configuration)
        self.le_bios_live.textEdited.connect(self.save_configuration)

        self.rb_g19.toggled.connect(self.save_configuration)
        self.rb_g13.toggled.connect(self.save_configuration)
        self.rb_g15v1.toggled.connect(self.save_configuration)
        self.rb_g15v2.toggled.connect(self.save_configuration)
        self.rb_g510.toggled.connect(self.save_configuration)

        self.hs_large_font.valueChanged.connect(self.save_configuration)
        self.hs_medium_font.valueChanged.connect(self.save_configuration)
        self.hs_small_font.valueChanged.connect(self.save_configuration)

    def _init_gkeys(self) -> None:
        """Initialize of cells with completer and combobox."""
        p = ["A-10A", "A-10C", "A-10C_2", "A-29B", "A-4E-C", "AC_130", "AH-6", "AH-64D_BLK_II", "AJS37", "AV8BNA",
             "Alphajet", "Bell47_2", "Bf-109K-4", "BlackHawk", "Bronco-OV-10A", "C-101CC", "C-101EB", "Cessna_210N",
             "Christen Eagle II", "DC3", "EA-18G", "Edge540", "Extra330SR", "F-117A", "F-14A-135-GR", "F-14B", "F-15C",
             "F-15ESE", "F-16A", "F-16C_50", "F-16D_50", "F-16D_50_NS", "F-16D_52", "F-16D_52_NS", "F-16D_Barak_30",
             "F-16D_Barak_40", "F-16I", "F-22A", "F-2A", "F-2B", "F-5E-3", "F-86F Sabre", "F4e", "FA-18C_hornet",
             "FA-18E", "FA-18F", "FA_18D", "FW-190A8", "FW-190D9", "FlankerEx", "Flyer1", "Hawk", "Hercules", "I-16",
             "J-11A", "J-20A", "JF-17", "Ka-50", "Ka-50_3", "L-39C", "L-39ZA", "M-2000C", "MB-339A", "MB-339APAN",
             "MB-339PAN", "MQ9_PREDATOR", "Mi-24P", "Mi-8MT", "Mi-8MTV2", "MiG-15bis", "MiG-19P", "MiG-21Bis",
             "MiG-29A", "MiG-29G", "MiG-29S", "Mig-23UB", "Mirage-F1CE", "Mirage-F1EE", "MirageF1", "MirageF1CT",
             "MosquitoFBMkVI", "NONE", "NS430", "NS430_C-101CC", "NS430_C-101EB", "NS430_L-39C", "NS430_MI-8MTV2",
             "NS430_SA342", "P-47D-30", "P-47D-30bl1", "P-47D-40", "P-51D", "P-51D-30-NA", "REISEN52",
             "RST_Eurofighter", "RST_Eurofighter_AG", "Rafale_A_S", "Rafale_B", "Rafale_C", "Rafale_M", "SA342L",
             "SA342M", "SA342Minigun", "SA342Mistral", "SpitfireLFMkIX", "SpitfireLFMkIXCW", "Su-25", "Su-25T", "Su-27",
             "Su-30M", "Su-30MK", "Su-30SM", "Su-33", "Su-57", "Super_Etendard", "Supercarrier", "T-4", "T-45",
             "TF-51D", "UH-1H", "VNAO_Ready_Room", "VSN_AJS37Viggen", "VSN_C17A", "VSN_C5_Galaxy", "VSN_E2D",
             "VSN_Eurofighter", "VSN_Eurofighter_AG", "VSN_F104G", "VSN_F104G_AG", "VSN_F104S", "VSN_F104S_AG",
             "VSN_F105D", "VSN_F105G", "VSN_F14A", "VSN_F14B", "VSN_F15E", "VSN_F15E_AA", "VSN_F16A", "VSN_F16AMLU",
             "VSN_F16CBL50", "VSN_F16CBL52D", "VSN_F16CMBL50", "VSN_F22", "VSN_F35A", "VSN_F35A_AG", "VSN_F35B",
             "VSN_F35B_AG", "VSN_F4E", "VSN_F4E_AG", "VSN_F5E", "VSN_F5N", "VSN_FA18C", "VSN_FA18C_AG",
             "VSN_FA18C_Lot20", "VSN_FA18F", "VSN_FA18F_AG", "VSN_Harrier", "VSN_M2000", "VSN_P3C", "VSN_Su47",
             "VSN_TornadoGR4", "VSN_TornadoIDS", "VSN_UFO", "Yak-52", ]
        completer = QtWidgets.QCompleter(p)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        completer.setMaxVisibleItems(self._visible_items)
        completer.setModelSorting(QtWidgets.QCompleter.ModelSorting.CaseInsensitivelySortedModel)
        self.combo_planes.addItems(p)
        self.combo_planes.setEditable(True)
        self.combo_planes.setCompleter(completer)
        self.combo_planes.currentTextChanged.connect(self._load_new_plane)
        self.sp_completer.valueChanged.connect(self._set_find_value)

    def _load_new_plane(self, text) -> None:
        """Refresh table when new plane is loaded."""
        LOG.debug(text)
        self._load_table_gkeys()

    def _set_find_value(self, value) -> None:
        """
        Refresh configuration of table and completer when visible items value changed.

        :param value: number of items visible
        """
        LOG.debug(value)
        self._visible_items = value
        self._load_table_gkeys()

    def _init_keyboards(self) -> None:
        """Initialize of keyboards."""
        for data in LCD_TYPES.values():
            getattr(self, f'rb_{data["klass"].lower()}').toggled.connect(partial(self._select_keyboard, data["klass"]))
        self.rb_g13.setChecked(True)  # todo: remove when load config will work

    def _select_keyboard(self, keyboard: str, state: bool) -> None:
        """
        Triggered when new keyboard is selected.

        Based of current selected keyboard:
        * Add correct numbers of rows and columns
        * enable DED font checkbox
        * updates font sliders (range and values)
        :param keyboard: name
        :param state: of radio button
        """
        if state:
            for mode_col in range(self.keyboard.modes):
                self.tw_gkeys.removeColumn(mode_col)
            for gkey_row in range(self.keyboard.gkeys):
                self.tw_gkeys.removeRow(gkey_row)
            self.keyboard = getattr(import_module('dcspy.models'), f'Model{keyboard}')
            LOG.debug(f'Select: {self.keyboard}')
            self._set_ded_font_and_font_sliders()
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
            hs: QtWidgets.QSlider = getattr(self, f'hs_{name}_font')
            try:
                hs.valueChanged.disconnect()
            except RuntimeError:
                pass
            hs.setMinimum(minimum)
            hs.setMaximum(maximum)
            hs.valueChanged.connect(partial(self._set_label_and_hs_value, name=name))
            hs.setValue(getattr(self, f'{self.keyboard.lcd}_font')[name])

    def _set_label_and_hs_value(self, value, name) -> None:
        """
        Set internal field for current value of slider and update label.

        :param value: of slider
        :param name: of slider
        """
        getattr(self, f'{self.keyboard.lcd}_font')[name] = value
        getattr(self, f'l_{name}').setText(str(value))

    def _load_table_gkeys(self) -> None:
        """Initialize table with cockpit data."""
        n1 = ['ADI_AUX_FLAG', 'ADI_BANK', 'ADI_BUBBLE', 'ADI_GS_BAR', 'ADI_GS_FLAG', 'ADI_GS_POINTER', 'ADI_LOC_BAR',
              'ADI_LOC_FLAG', 'ADI_OFF_FLAG',
              'ADI_PITCH', 'ADI_PITCH_TRIM', 'ADI_TURNRATE', 'AIRSPEED', 'AIRSPEED_SET_KNB', 'MACH_INDICATOR',
              'MAX_AIRSPEED', 'SET_AIRSPEED',
              'ALT_10000_FT_CNT', 'ALT_1000_FT_CNT', 'ALT_100_FT_CNT', 'ALT_100_FT_PTR', 'ALT_BARO_SET_KNB',
              'ALT_MODE_LV', 'ALT_PNEU_FLAG',
              'ALT_PRESSURE_DRUM_0_CNT', 'ALT_PRESSURE_DRUM_1_CNT', 'ALT_PRESSURE_DRUM_2_CNT',
              'ALT_PRESSURE_DRUM_3_CNT', 'AOA_VALUE', 'COMM1_MODE_KNB',
              'COMM1_PWR_KNB', 'COMM2_MODE_KNB', 'COMM2_PWR_KNB', 'HOT_MIC_SW', 'IFF_ANT_SEL_SW', 'ILS_PWR_KNB',
              'INTERCOM_KNB', 'MSL_KNB', 'SEC_VOICE_KNB',
              'TACAN_KNB', 'TF_KNB', 'THREAT_KNB', 'UHF_ANT_SEL_SW', 'VMS_INHIBIT_SW', 'DL_SW', 'GPS_SW', 'INS_KNB',
              'MAP_SW', 'MFD_SW', 'MIDS_LVT_KNB',
              'MMC_PWR_SW', 'ST_STA_SW', 'UFC_SW', 'CMDS_01_EXP_CAT_SW', 'CMDS_02_EXP_CAT_SW', 'CMDS_CH_Amount',
              'CMDS_CH_EXP_CAT_SW', 'CMDS_DISPENSE_BTN',
              'CMDS_FL_Amount', 'CMDS_FL_EXP_CAT_SW', 'CMDS_JETT_SW', 'CMDS_JMR_SOURCHE_SW', 'CMDS_MODE_KNB',
              'CMDS_MWS_SOURCHE_SW', 'CMDS_O1_Amount',
              'CMDS_O2_Amount', 'CMDS_PROG_KNB', 'CMDS_PWR_SOURCHE_SW', 'CLOCK_CURRTIME_H', 'CLOCK_CURRTIME_MS',
              'CLOCK_ELAPSED', 'CLOCK_ELAPSED_TIME_M',
              'CLOCK_ELAPSED_TIME_SEC', 'CLOCK_SET', 'CLOCK_WIND', 'CANOPY_HANDLE', 'CANOPY_JETT_THANDLE', 'CANOPY_POS',
              'CANOPY_SW', 'HIDE_STICK', 'SEAT_ADJ',
              'SEAT_EJECT_HANDLE', 'SEAT_EJECT_SAFE', 'SEAT_HEIGHT', 'ADV_MODE_SW', 'ALT_FLAPS_SW', 'AP_PITCH_SW',
              'AP_ROLL_SW', 'BIT_SW', 'DIGI_BAK_SW',
              'FLCS_RESET_SW', 'LE_FLAPS_SW', 'MANUAL_PITCH_SW', 'MAN_TF_FLYUP_SW', 'PITCH_TRIM', 'ROLL_TRIM',
              'STORES_CONFIG_SW', 'TRIM_AP_DISC_SW',
              'YAW_TRIM', 'DED_LINE_1', 'DED_LINE_2', 'DED_LINE_3', 'DED_LINE_4', 'DED_LINE_5', 'ECM_1_BTN',
              'ECM_2_BTN', 'ECM_3_BTN', 'ECM_4_BTN', 'ECM_5_BTN',
              'ECM_6_BTN', 'ECM_BIT_BTN', 'ECM_DIM_KNB', 'ECM_FRM_BTN', 'ECM_PW_SW', 'ECM_RESET_BTN', 'ECM_SPL_BTN',
              'ECM_XMIT_SW', 'AIR_SOURCE_KNB',
              'DEFOG_LEVER', 'TEMP_KNB', 'EHSI_CRS_SET', 'EHSI_CRS_SET_KNB', 'EHSI_HDG_SET_BTN', 'EHSI_HDG_SET_KNB',
              'EHSI_MODE', 'EPU_SW', 'EPU_SW_COVER_OFF',
              'EPU_SW_COVER_ON', 'HYDRAZIN_VOLUME', 'ELEC_CAUTION', 'EPU_GEN_TEST_SW', 'FLCS_PWR_TEST_SW',
              'MAIN_PWR_SW', 'PROBE_HEAT_SW', 'AB_RESET_SW',
              'ENGINE_FTIT', 'ENGINE_NOZZLE_POSITION', 'ENGINE_OIL_PRESSURE', 'ENGINE_TACHOMETER', 'ENG_ANTI_ICE',
              'ENG_CONT_SW', 'ENG_CONT_SW_COVER',
              'FIRE_OHEAT_DETECT_BTN', 'JFS_SW', 'MAX_PWR_SW', 'EXT_FORMATION_LIGHTS', 'EXT_POSITION_LIGHTS_WING',
              'EXT_POSITION_LIGHT_FUSELAGE',
              'EXT_SPEED_BRAKE_LEFT', 'EXT_SPEED_BRAKE_RIGHT', 'EXT_STROBE_TAIL', 'EXT_TAIL_LIGHT', 'EXT_WOW_LEFT',
              'EXT_WOW_NOSE', 'EXT_WOW_RIGHT',
              'AIR_REFUEL_LIGHT_KNB', 'ANTI_COLL_LIGHT_KNB', 'ENGINE_FEED_KNB', 'FORM_LIGHT_KNB', 'LAND_TAXI_LIGHT_SW',
              'MAL_IND_LTS_BRT_SW', 'MASTER_LIGHT_SW',
              'POS_FLASH_LIGHT_SW', 'POS_FUSELAGE_LIGHT_SW', 'POS_WING_TAIL_LIGHT_SW', 'AIR_REFUEL_SW',
              'EXT_FUEL_TRANS_SW', 'FUELFLOWCOUNTER_100',
              'FUELFLOWCOUNTER_10K', 'FUELFLOWCOUNTER_1K', 'FUELTOTALIZER_100', 'FUELTOTALIZER_10K', 'FUELTOTALIZER_1K',
              'FUEL_AL', 'FUEL_FR', 'FUEL_MASTER_CV',
              'FUEL_MASTER_SW', 'FUEL_QTY_SEL_KNB', 'FUEL_QTY_SEL_T_KNB', 'TANK_INTERTING_SW', 'ANTI_SKID_SW',
              'BRAKE_CHAN_SW', 'DN_LOCK_BTN', 'GEAR_ALT_BTN',
              'GEAR_ALT_HANDLE', 'GEAR_HANDLE', 'HOOK_SW', 'HORN_SILENCE_BTN', 'HMCS_INT_KNB', 'HUD_ALT_SW',
              'HUD_BRT_SW', 'HUD_DED_DATA_SW',
              'HUD_DEPRESS_RET_SW', 'HUD_FP_MARKER_SW', 'HUD_SCALES_SW', 'HUD_SPEED_SW', 'HUD_TEST_SW', 'SYSA_PRESSURE',
              'SYSB_PRESSURE',
              'IFF_CODE_DRUM_DIGIT_1', 'IFF_CODE_DRUM_DIGIT_2', 'IFF_CODE_DRUM_DIGIT_3', 'IFF_CODE_DRUM_DIGIT_4',
              'IFF_C_I_KNB', 'IFF_ENABLE_SW',
              'IFF_M1_SEL_1', 'IFF_M1_SEL_2', 'IFF_M3_SEL_1', 'IFF_M3_SEL_2', 'IFF_M4_CODE_SW', 'IFF_M4_MONITOR_SW',
              'IFF_M4_REPLY_SW', 'IFF_MASTER_KNB',
              'AOA_INDEX_BRT_KNB', 'AR_STATUS_BRT_KNB', 'FLOOD_CONSOLES_BRT_KNB', 'FLOOD_INST_PNL_BRT_KNB',
              'MAL_IND_LTS_TEST', 'MASTER_CAUTION',
              'PRI_CONSOLES_BRT_KNB', 'PRI_DATA_DISPLAY_BRT_KNB', 'PRI_INST_PNL_BRT_KNB', 'LIGHT_CONSLES',
              'LIGHT_CONSLES_FLOOD', 'LIGHT_INST_PNL',
              'LIGHT_INST_PNL_FLOOD', 'KY58_FILL_KNB', 'KY58_MODE_KNB', 'KY58_PWR_KNB', 'KY58_VOL_KNB',
              'PLAIN_CIPHER_SW', 'ZEROIZE_SW', 'ZEROIZE_SW_COVER',
              'MFD_L_1', 'MFD_L_10', 'MFD_L_11', 'MFD_L_12', 'MFD_L_13', 'MFD_L_14', 'MFD_L_15', 'MFD_L_16', 'MFD_L_17',
              'MFD_L_18', 'MFD_L_19', 'MFD_L_2',
              'MFD_L_20', 'MFD_L_3', 'MFD_L_4', 'MFD_L_5', 'MFD_L_6', 'MFD_L_7', 'MFD_L_8', 'MFD_L_9', 'MFD_L_BRT_SW',
              'MFD_L_CON_SW', 'MFD_L_GAIN_SW',
              'MFD_L_SYM_SW', 'MFD_R_1', 'MFD_R_10', 'MFD_R_11', 'MFD_R_12', 'MFD_R_13', 'MFD_R_14', 'MFD_R_15',
              'MFD_R_16', 'MFD_R_17', 'MFD_R_18', 'MFD_R_19',
              'MFD_R_2', 'MFD_R_20', 'MFD_R_3', 'MFD_R_4', 'MFD_R_5', 'MFD_R_6', 'MFD_R_7', 'MFD_R_8', 'MFD_R_9',
              'MFD_R_BRT_SW', 'MFD_R_CON_SW',
              'MFD_R_GAIN_SW', 'MFD_R_SYM_SW', 'ALT_REL_BTN', 'EMERG_STORE_JETT', 'GND_JETT_ENABLE_SW', 'LASER_ARM_SW',
              'MASTER_ARM_SW', 'COCKPIT_ALITITUDE',
              'FLOW_INDICATOR', 'FLOW_INDICATOR_LIGHT', 'OBOGS_SW', 'OXYGEN_PRESSURE', 'OXY_DILUTER_LVR',
              'OXY_EMERG_LVR', 'OXY_SUPPLY_LVR', 'RWR_ACT_PWR_BTN',
              'RWR_ALT_BTN', 'RWR_HANDOFF_BTN', 'RWR_IND_DIM_KNB', 'RWR_INTENS_KNB', 'RWR_LAUNCH_BTN', 'RWR_MODE_BTN',
              'RWR_PWR_BTN', 'RWR_SEARCH_BTN',
              'RWR_SYS_TEST_BTN', 'RWR_T_BTN', 'RWR_UNKNOWN_SHIP_BTN', 'SAI_AIRCRAFTREFERENCESYMBOL', 'SAI_BANK',
              'SAI_BANK_ARROW', 'SAI_CAGE', 'SAI_KNB_ARROW',
              'SAI_OFF_FLAG', 'SAI_PITCH', 'SAI_PITCH_TRIM', 'FCR_PWR_SW', 'HDPT_SW_L', 'HDPT_SW_R', 'RDR_ALT_PWR_SW',
              'SPEEDBRAKE_INDICATOR', 'PITCHTRIMIND',
              'ROLLTRIMIND', 'F_ACK_BTN', 'ICP_AA_MODE_BTN', 'ICP_AG_MODE_BTN', 'ICP_BTN_0', 'ICP_BTN_1', 'ICP_BTN_2',
              'ICP_BTN_3', 'ICP_BTN_4', 'ICP_BTN_5',
              'ICP_BTN_6', 'ICP_BTN_7', 'ICP_BTN_8', 'ICP_BTN_9', 'ICP_COM1_BTN', 'ICP_COM2_BTN', 'ICP_DATA_RTN_SEQ_SW',
              'ICP_DATA_UP_DN_SW', 'ICP_DED_SW',
              'ICP_DRIFT_SW', 'ICP_ENTR_BTN', 'ICP_FLIR_GAIN_SW', 'ICP_FLIR_SW', 'ICP_HUD_BRT_KNB', 'ICP_IFF_BTN',
              'ICP_LIST_BTN', 'ICP_RASTER_BRT_KNB',
              'ICP_RASTER_CONTR_KNB', 'ICP_RCL_BTN', 'ICP_RETICLE_DEPRESS_KNB', 'ICP_WX_BTN', 'IFF_ID_BTN', 'RF_SW',
              'UHF_CHAN_DISP', 'UHF_CHAN_KNB',
              'UHF_DOOR', 'UHF_FREQ_0025_KNB', 'UHF_FREQ_01_KNB', 'UHF_FREQ_100_KNB', 'UHF_FREQ_10_KNB',
              'UHF_FREQ_1_KNB', 'UHF_FREQ_DISP', 'UHF_FUNC_KNB',
              'UHF_MODE_KNB', 'UHF_SQUELCH_SW', 'UHF_STATUS_BTN', 'UHF_TEST_BTN', 'UHF_TONE_BTN', 'UHF_VOL_KNB', 'VVI',
              'LIGHT_ACFT_BATT_FAIL', 'LIGHT_ACTIVE',
              'LIGHT_AFT_FUEL_LOW', 'LIGHT_AIR', 'LIGHT_ANTI_SKID', 'LIGHT_AOA_DN', 'LIGHT_AOA_MID', 'LIGHT_AOA_UP',
              'LIGHT_AR_NWS', 'LIGHT_ATF_NOT',
              'LIGHT_AVIONICS_FAULT', 'LIGHT_BUC', 'LIGHT_CABIN_PRESS', 'LIGHT_CADC', 'LIGHT_CANOPY', 'LIGHT_CAUTION_1',
              'LIGHT_CAUTION_2', 'LIGHT_CAUTION_3',
              'LIGHT_CAUTION_4', 'LIGHT_CAUTION_5', 'LIGHT_CAUTION_6', 'LIGHT_CMDS_DISP', 'LIGHT_CMDS_GO',
              'LIGHT_CMDS_NO_GO', 'LIGHT_CMDS_RDY', 'LIGHT_DBU_ON',
              'LIGHT_DISC', 'LIGHT_ECM', 'LIGHT_ECM_1_A', 'LIGHT_ECM_1_F', 'LIGHT_ECM_1_S', 'LIGHT_ECM_1_T',
              'LIGHT_ECM_2_A', 'LIGHT_ECM_2_F', 'LIGHT_ECM_2_S',
              'LIGHT_ECM_2_T', 'LIGHT_ECM_3_A', 'LIGHT_ECM_3_F', 'LIGHT_ECM_3_S', 'LIGHT_ECM_3_T', 'LIGHT_ECM_4_A',
              'LIGHT_ECM_4_F', 'LIGHT_ECM_4_S',
              'LIGHT_ECM_4_T', 'LIGHT_ECM_5_A', 'LIGHT_ECM_5_F', 'LIGHT_ECM_5_S', 'LIGHT_ECM_5_T', 'LIGHT_ECM_A',
              'LIGHT_ECM_F', 'LIGHT_ECM_FRM_A',
              'LIGHT_ECM_FRM_F', 'LIGHT_ECM_FRM_S', 'LIGHT_ECM_FRM_T', 'LIGHT_ECM_S', 'LIGHT_ECM_SPL_A',
              'LIGHT_ECM_SPL_F', 'LIGHT_ECM_SPL_S',
              'LIGHT_ECM_SPL_T', 'LIGHT_ECM_T', 'LIGHT_EDGE', 'LIGHT_EEC', 'LIGHT_ELEC', 'LIGHT_ELEC_SYS',
              'LIGHT_ENGINE', 'LIGHT_ENGINE_FAULT',
              'LIGHT_ENG_FIRE', 'LIGHT_EPU', 'LIGHT_EPU_GEN', 'LIGHT_EPU_PMG', 'LIGHT_EQUIP_HOT', 'LIGHT_FLCS',
              'LIGHT_FLCS_FAULT', 'LIGHT_FLCS_PMG',
              'LIGHT_FLCS_PWR_A', 'LIGHT_FLCS_PWR_B', 'LIGHT_FLCS_PWR_C', 'LIGHT_FLCS_PWR_D', 'LIGHT_FLCS_RLY',
              'LIGHT_FL_FAIL', 'LIGHT_FL_RUN',
              'LIGHT_FUEL_OIL_HOT', 'LIGHT_FWD_FUEL_LOW', 'LIGHT_GEAR_L', 'LIGHT_GEAR_N', 'LIGHT_GEAR_R',
              'LIGHT_GEAR_WARN', 'LIGHT_HOOK', 'LIGHT_HYDRAZN',
              'LIGHT_HYD_OIL_PRESS', 'LIGHT_IFF', 'LIGHT_INLET_ICING', 'LIGHT_JFS_RUN', 'LIGHT_MAIN_GEN',
              'LIGHT_MARKER_BEACON', 'LIGHT_MASTER_CAUTION',
              'LIGHT_NUCLEAR', 'LIGHT_NWS_FAIL', 'LIGHT_OBOGS', 'LIGHT_OVERHEAT', 'LIGHT_OXY_LOW', 'LIGHT_PROBE_HEAT',
              'LIGHT_RADAR_ALT', 'LIGHT_RDY',
              'LIGHT_RWR_ACTIVITY', 'LIGHT_RWR_ACT_POWER', 'LIGHT_RWR_ALT', 'LIGHT_RWR_ALT_LOW', 'LIGHT_RWR_HANDOFF_H',
              'LIGHT_RWR_HANDOFF_UP',
              'LIGHT_RWR_MODE_OPEN', 'LIGHT_RWR_MODE_PRI', 'LIGHT_RWR_MSL_LAUNCH', 'LIGHT_RWR_POWER',
              'LIGHT_RWR_SEARCH', 'LIGHT_RWR_SHIP_UNK',
              'LIGHT_RWR_SYSTEST', 'LIGHT_RWR_TGTSEP_DN', 'LIGHT_RWR_TGTSEP_UP', 'LIGHT_SEAT_NOT', 'LIGHT_SEC',
              'LIGHT_STBY', 'LIGHT_STBY_GEN',
              'LIGHT_STORES_CONFIG', 'LIGHT_TF_FAIL', 'LIGHT_TO_FLCS', 'LIGHT_TO_LDG_CONFIG']
        n2 = ['', '-- ADI --', 'ADI_AUX_FLAG', 'ADI_BANK', 'ADI_BUBBLE', 'ADI_GS_BAR', 'ADI_GS_FLAG', 'ADI_GS_POINTER',
              'ADI_LOC_BAR', 'ADI_LOC_FLAG',
              'ADI_OFF_FLAG', 'ADI_PITCH', 'ADI_PITCH_TRIM', 'ADI_TURNRATE', '-- Airspeed Indicator --', 'AIRSPEED',
              'AIRSPEED_SET_KNB', 'MACH_INDICATOR',
              'MAX_AIRSPEED', 'SET_AIRSPEED', '-- Altimeter --', 'ALT_10000_FT_CNT', 'ALT_1000_FT_CNT',
              'ALT_100_FT_CNT', 'ALT_100_FT_PTR', 'ALT_BARO_SET_KNB',
              'ALT_MODE_LV', 'ALT_PNEU_FLAG', 'ALT_PRESSURE_DRUM_0_CNT', 'ALT_PRESSURE_DRUM_1_CNT',
              'ALT_PRESSURE_DRUM_2_CNT', 'ALT_PRESSURE_DRUM_3_CNT',
              '-- AoA --', 'AOA_VALUE', '-- Audio Panel --', 'COMM1_MODE_KNB', 'COMM1_PWR_KNB', 'COMM2_MODE_KNB',
              'COMM2_PWR_KNB', 'HOT_MIC_SW',
              'IFF_ANT_SEL_SW', 'ILS_PWR_KNB', 'INTERCOM_KNB', 'MSL_KNB', 'SEC_VOICE_KNB', 'TACAN_KNB', 'TF_KNB',
              'THREAT_KNB', 'UHF_ANT_SEL_SW',
              'VMS_INHIBIT_SW', '-- Avionic Panel --', 'DL_SW', 'GPS_SW', 'INS_KNB', 'MAP_SW', 'MFD_SW', 'MIDS_LVT_KNB',
              'MMC_PWR_SW', 'ST_STA_SW', 'UFC_SW',
              '-- CMDS --', 'CMDS_01_EXP_CAT_SW', 'CMDS_02_EXP_CAT_SW', 'CMDS_CH_Amount', 'CMDS_CH_EXP_CAT_SW',
              'CMDS_DISPENSE_BTN', 'CMDS_FL_Amount',
              'CMDS_FL_EXP_CAT_SW', 'CMDS_JETT_SW', 'CMDS_JMR_SOURCHE_SW', 'CMDS_MODE_KNB', 'CMDS_MWS_SOURCHE_SW',
              'CMDS_O1_Amount', 'CMDS_O2_Amount',
              'CMDS_PROG_KNB', 'CMDS_PWR_SOURCHE_SW', '-- Clock --', 'CLOCK_CURRTIME_H', 'CLOCK_CURRTIME_MS',
              'CLOCK_ELAPSED', 'CLOCK_ELAPSED_TIME_M',
              'CLOCK_ELAPSED_TIME_SEC', 'CLOCK_SET', 'CLOCK_WIND', '-- Cockpit Mechanics --', 'CANOPY_HANDLE',
              'CANOPY_JETT_THANDLE', 'CANOPY_POS', 'CANOPY_SW',
              'HIDE_STICK', 'SEAT_ADJ', 'SEAT_EJECT_HANDLE', 'SEAT_EJECT_SAFE', 'SEAT_HEIGHT',
              '-- Control Interface --', 'ADV_MODE_SW', 'ALT_FLAPS_SW',
              'AP_PITCH_SW', 'AP_ROLL_SW', 'BIT_SW', 'DIGI_BAK_SW', 'FLCS_RESET_SW', 'LE_FLAPS_SW', 'MANUAL_PITCH_SW',
              'MAN_TF_FLYUP_SW', 'PITCH_TRIM',
              'ROLL_TRIM', 'STORES_CONFIG_SW', 'TRIM_AP_DISC_SW', 'YAW_TRIM', '-- DED Output Data --', 'DED_LINE_1',
              'DED_LINE_2', 'DED_LINE_3', 'DED_LINE_4',
              'DED_LINE_5', '-- ECM --', 'ECM_1_BTN', 'ECM_2_BTN', 'ECM_3_BTN', 'ECM_4_BTN', 'ECM_5_BTN', 'ECM_6_BTN',
              'ECM_BIT_BTN', 'ECM_DIM_KNB',
              'ECM_FRM_BTN', 'ECM_PW_SW', 'ECM_RESET_BTN', 'ECM_SPL_BTN', 'ECM_XMIT_SW', '-- ECS --', 'AIR_SOURCE_KNB',
              'DEFOG_LEVER', 'TEMP_KNB', '-- EHSI --',
              'EHSI_CRS_SET', 'EHSI_CRS_SET_KNB', 'EHSI_HDG_SET_BTN', 'EHSI_HDG_SET_KNB', 'EHSI_MODE', '-- EPU --',
              'EPU_SW', 'EPU_SW_COVER_OFF',
              'EPU_SW_COVER_ON', 'HYDRAZIN_VOLUME', '-- Electric System --', 'ELEC_CAUTION', 'EPU_GEN_TEST_SW',
              'FLCS_PWR_TEST_SW', 'MAIN_PWR_SW',
              'PROBE_HEAT_SW', '-- Engine --', 'AB_RESET_SW', 'ENGINE_FTIT', 'ENGINE_NOZZLE_POSITION',
              'ENGINE_OIL_PRESSURE', 'ENGINE_TACHOMETER',
              'ENG_ANTI_ICE', 'ENG_CONT_SW', 'ENG_CONT_SW_COVER', 'FIRE_OHEAT_DETECT_BTN', 'JFS_SW', 'MAX_PWR_SW',
              '-- External Aircraft Model --',
              'EXT_FORMATION_LIGHTS', 'EXT_POSITION_LIGHTS_WING', 'EXT_POSITION_LIGHT_FUSELAGE', 'EXT_SPEED_BRAKE_LEFT',
              'EXT_SPEED_BRAKE_RIGHT',
              'EXT_STROBE_TAIL', 'EXT_TAIL_LIGHT', 'EXT_WOW_LEFT', 'EXT_WOW_NOSE', 'EXT_WOW_RIGHT',
              '-- External Lights --', 'AIR_REFUEL_LIGHT_KNB',
              'ANTI_COLL_LIGHT_KNB', 'ENGINE_FEED_KNB', 'FORM_LIGHT_KNB', 'LAND_TAXI_LIGHT_SW', 'MAL_IND_LTS_BRT_SW',
              'MASTER_LIGHT_SW', 'POS_FLASH_LIGHT_SW',
              'POS_FUSELAGE_LIGHT_SW', 'POS_WING_TAIL_LIGHT_SW', '-- Fuel System --', 'AIR_REFUEL_SW',
              'EXT_FUEL_TRANS_SW', 'FUELFLOWCOUNTER_100',
              'FUELFLOWCOUNTER_10K', 'FUELFLOWCOUNTER_1K', 'FUELTOTALIZER_100', 'FUELTOTALIZER_10K', 'FUELTOTALIZER_1K',
              'FUEL_AL', 'FUEL_FR', 'FUEL_MASTER_CV',
              'FUEL_MASTER_SW', 'FUEL_QTY_SEL_KNB', 'FUEL_QTY_SEL_T_KNB', 'TANK_INTERTING_SW', '-- Gear System --',
              'ANTI_SKID_SW', 'BRAKE_CHAN_SW',
              'DN_LOCK_BTN', 'GEAR_ALT_BTN', 'GEAR_ALT_HANDLE', 'GEAR_HANDLE', 'HOOK_SW', 'HORN_SILENCE_BTN',
              '-- HMCS --', 'HMCS_INT_KNB',
              '-- HUD Control Panel --', 'HUD_ALT_SW', 'HUD_BRT_SW', 'HUD_DED_DATA_SW', 'HUD_DEPRESS_RET_SW',
              'HUD_FP_MARKER_SW', 'HUD_SCALES_SW',
              'HUD_SPEED_SW', 'HUD_TEST_SW', '-- Hydraulic Pressure Indicators --', 'SYSA_PRESSURE', 'SYSB_PRESSURE',
              '-- IFF --', 'IFF_CODE_DRUM_DIGIT_1',
              'IFF_CODE_DRUM_DIGIT_2', 'IFF_CODE_DRUM_DIGIT_3', 'IFF_CODE_DRUM_DIGIT_4', 'IFF_C_I_KNB', 'IFF_ENABLE_SW',
              'IFF_M1_SEL_1', 'IFF_M1_SEL_2',
              'IFF_M3_SEL_1', 'IFF_M3_SEL_2', 'IFF_M4_CODE_SW', 'IFF_M4_MONITOR_SW', 'IFF_M4_REPLY_SW',
              'IFF_MASTER_KNB', '-- Interior Lights --',
              'AOA_INDEX_BRT_KNB', 'AR_STATUS_BRT_KNB', 'FLOOD_CONSOLES_BRT_KNB', 'FLOOD_INST_PNL_BRT_KNB',
              'MAL_IND_LTS_TEST', 'MASTER_CAUTION',
              'PRI_CONSOLES_BRT_KNB', 'PRI_DATA_DISPLAY_BRT_KNB', 'PRI_INST_PNL_BRT_KNB',
              '-- Interior Lights Indicators --', 'LIGHT_CONSLES',
              'LIGHT_CONSLES_FLOOD', 'LIGHT_INST_PNL', 'LIGHT_INST_PNL_FLOOD', '-- KY-58 --', 'KY58_FILL_KNB',
              'KY58_MODE_KNB', 'KY58_PWR_KNB', 'KY58_VOL_KNB',
              'PLAIN_CIPHER_SW', 'ZEROIZE_SW', 'ZEROIZE_SW_COVER', '-- MFD Left --', 'MFD_L_1', 'MFD_L_10', 'MFD_L_11',
              'MFD_L_12', 'MFD_L_13', 'MFD_L_14',
              'MFD_L_15', 'MFD_L_16', 'MFD_L_17', 'MFD_L_18', 'MFD_L_19', 'MFD_L_2', 'MFD_L_20', 'MFD_L_3', 'MFD_L_4',
              'MFD_L_5', 'MFD_L_6', 'MFD_L_7',
              'MFD_L_8', 'MFD_L_9', 'MFD_L_BRT_SW', 'MFD_L_CON_SW', 'MFD_L_GAIN_SW', 'MFD_L_SYM_SW', '-- MFD Right --',
              'MFD_R_1', 'MFD_R_10', 'MFD_R_11',
              'MFD_R_12', 'MFD_R_13', 'MFD_R_14', 'MFD_R_15', 'MFD_R_16', 'MFD_R_17', 'MFD_R_18', 'MFD_R_19', 'MFD_R_2',
              'MFD_R_20', 'MFD_R_3', 'MFD_R_4',
              'MFD_R_5', 'MFD_R_6', 'MFD_R_7', 'MFD_R_8', 'MFD_R_9', 'MFD_R_BRT_SW', 'MFD_R_CON_SW', 'MFD_R_GAIN_SW',
              'MFD_R_SYM_SW', '-- MMC --',
              'ALT_REL_BTN', 'EMERG_STORE_JETT', 'GND_JETT_ENABLE_SW', 'LASER_ARM_SW', 'MASTER_ARM_SW',
              '-- Oxygen System --', 'COCKPIT_ALITITUDE',
              'FLOW_INDICATOR', 'FLOW_INDICATOR_LIGHT', 'OBOGS_SW', 'OXYGEN_PRESSURE', 'OXY_DILUTER_LVR',
              'OXY_EMERG_LVR', 'OXY_SUPPLY_LVR', '-- RWR --',
              'RWR_ACT_PWR_BTN', 'RWR_ALT_BTN', 'RWR_HANDOFF_BTN', 'RWR_IND_DIM_KNB', 'RWR_INTENS_KNB',
              'RWR_LAUNCH_BTN', 'RWR_MODE_BTN', 'RWR_PWR_BTN',
              'RWR_SEARCH_BTN', 'RWR_SYS_TEST_BTN', 'RWR_T_BTN', 'RWR_UNKNOWN_SHIP_BTN', '-- SAI --',
              'SAI_AIRCRAFTREFERENCESYMBOL', 'SAI_BANK',
              'SAI_BANK_ARROW', 'SAI_CAGE', 'SAI_KNB_ARROW', 'SAI_OFF_FLAG', 'SAI_PITCH', 'SAI_PITCH_TRIM',
              '-- Sensor Panel --', 'FCR_PWR_SW', 'HDPT_SW_L',
              'HDPT_SW_R', 'RDR_ALT_PWR_SW', '-- Speed Brake --', 'SPEEDBRAKE_INDICATOR', '-- Trim Indicators --',
              'PITCHTRIMIND', 'ROLLTRIMIND', '-- UFC --',
              'F_ACK_BTN', 'ICP_AA_MODE_BTN', 'ICP_AG_MODE_BTN', 'ICP_BTN_0', 'ICP_BTN_1', 'ICP_BTN_2', 'ICP_BTN_3',
              'ICP_BTN_4', 'ICP_BTN_5', 'ICP_BTN_6',
              'ICP_BTN_7', 'ICP_BTN_8', 'ICP_BTN_9', 'ICP_COM1_BTN', 'ICP_COM2_BTN', 'ICP_DATA_RTN_SEQ_SW',
              'ICP_DATA_UP_DN_SW', 'ICP_DED_SW', 'ICP_DRIFT_SW',
              'ICP_ENTR_BTN', 'ICP_FLIR_GAIN_SW', 'ICP_FLIR_SW', 'ICP_HUD_BRT_KNB', 'ICP_IFF_BTN', 'ICP_LIST_BTN',
              'ICP_RASTER_BRT_KNB', 'ICP_RASTER_CONTR_KNB',
              'ICP_RCL_BTN', 'ICP_RETICLE_DEPRESS_KNB', 'ICP_WX_BTN', 'IFF_ID_BTN', 'RF_SW', '-- UHF --',
              'UHF_CHAN_DISP', 'UHF_CHAN_KNB', 'UHF_DOOR',
              'UHF_FREQ_0025_KNB', 'UHF_FREQ_01_KNB', 'UHF_FREQ_100_KNB', 'UHF_FREQ_10_KNB', 'UHF_FREQ_1_KNB',
              'UHF_FREQ_DISP', 'UHF_FUNC_KNB', 'UHF_MODE_KNB',
              'UHF_SQUELCH_SW', 'UHF_STATUS_BTN', 'UHF_TEST_BTN', 'UHF_TONE_BTN', 'UHF_VOL_KNB',
              '-- Vertical Velocity Indicator --', 'VVI',
              '-- Warning, Caution and IndicatorLights --', 'LIGHT_ACFT_BATT_FAIL', 'LIGHT_ACTIVE',
              'LIGHT_AFT_FUEL_LOW', 'LIGHT_AIR', 'LIGHT_ANTI_SKID',
              'LIGHT_AOA_DN', 'LIGHT_AOA_MID', 'LIGHT_AOA_UP', 'LIGHT_AR_NWS', 'LIGHT_ATF_NOT', 'LIGHT_AVIONICS_FAULT',
              'LIGHT_BUC', 'LIGHT_CABIN_PRESS',
              'LIGHT_CADC', 'LIGHT_CANOPY', 'LIGHT_CAUTION_1', 'LIGHT_CAUTION_2', 'LIGHT_CAUTION_3', 'LIGHT_CAUTION_4',
              'LIGHT_CAUTION_5', 'LIGHT_CAUTION_6',
              'LIGHT_CMDS_DISP', 'LIGHT_CMDS_GO', 'LIGHT_CMDS_NO_GO', 'LIGHT_CMDS_RDY', 'LIGHT_DBU_ON', 'LIGHT_DISC',
              'LIGHT_ECM', 'LIGHT_ECM_1_A',
              'LIGHT_ECM_1_F', 'LIGHT_ECM_1_S', 'LIGHT_ECM_1_T', 'LIGHT_ECM_2_A', 'LIGHT_ECM_2_F', 'LIGHT_ECM_2_S',
              'LIGHT_ECM_2_T', 'LIGHT_ECM_3_A',
              'LIGHT_ECM_3_F', 'LIGHT_ECM_3_S', 'LIGHT_ECM_3_T', 'LIGHT_ECM_4_A', 'LIGHT_ECM_4_F', 'LIGHT_ECM_4_S',
              'LIGHT_ECM_4_T', 'LIGHT_ECM_5_A',
              'LIGHT_ECM_5_F', 'LIGHT_ECM_5_S', 'LIGHT_ECM_5_T', 'LIGHT_ECM_A', 'LIGHT_ECM_F', 'LIGHT_ECM_FRM_A',
              'LIGHT_ECM_FRM_F', 'LIGHT_ECM_FRM_S',
              'LIGHT_ECM_FRM_T', 'LIGHT_ECM_S', 'LIGHT_ECM_SPL_A', 'LIGHT_ECM_SPL_F', 'LIGHT_ECM_SPL_S',
              'LIGHT_ECM_SPL_T', 'LIGHT_ECM_T', 'LIGHT_EDGE',
              'LIGHT_EEC', 'LIGHT_ELEC', 'LIGHT_ELEC_SYS', 'LIGHT_ENGINE', 'LIGHT_ENGINE_FAULT', 'LIGHT_ENG_FIRE',
              'LIGHT_EPU', 'LIGHT_EPU_GEN',
              'LIGHT_EPU_PMG', 'LIGHT_EQUIP_HOT', 'LIGHT_FLCS', 'LIGHT_FLCS_FAULT', 'LIGHT_FLCS_PMG',
              'LIGHT_FLCS_PWR_A', 'LIGHT_FLCS_PWR_B',
              'LIGHT_FLCS_PWR_C', 'LIGHT_FLCS_PWR_D', 'LIGHT_FLCS_RLY', 'LIGHT_FL_FAIL', 'LIGHT_FL_RUN',
              'LIGHT_FUEL_OIL_HOT', 'LIGHT_FWD_FUEL_LOW',
              'LIGHT_GEAR_L', 'LIGHT_GEAR_N', 'LIGHT_GEAR_R', 'LIGHT_GEAR_WARN', 'LIGHT_HOOK', 'LIGHT_HYDRAZN',
              'LIGHT_HYD_OIL_PRESS', 'LIGHT_IFF',
              'LIGHT_INLET_ICING', 'LIGHT_JFS_RUN', 'LIGHT_MAIN_GEN', 'LIGHT_MARKER_BEACON', 'LIGHT_MASTER_CAUTION',
              'LIGHT_NUCLEAR', 'LIGHT_NWS_FAIL',
              'LIGHT_OBOGS', 'LIGHT_OVERHEAT', 'LIGHT_OXY_LOW', 'LIGHT_PROBE_HEAT', 'LIGHT_RADAR_ALT', 'LIGHT_RDY',
              'LIGHT_RWR_ACTIVITY', 'LIGHT_RWR_ACT_POWER',
              'LIGHT_RWR_ALT', 'LIGHT_RWR_ALT_LOW', 'LIGHT_RWR_HANDOFF_H', 'LIGHT_RWR_HANDOFF_UP',
              'LIGHT_RWR_MODE_OPEN', 'LIGHT_RWR_MODE_PRI',
              'LIGHT_RWR_MSL_LAUNCH', 'LIGHT_RWR_POWER', 'LIGHT_RWR_SEARCH', 'LIGHT_RWR_SHIP_UNK', 'LIGHT_RWR_SYSTEST',
              'LIGHT_RWR_TGTSEP_DN',
              'LIGHT_RWR_TGTSEP_UP', 'LIGHT_SEAT_NOT', 'LIGHT_SEC', 'LIGHT_STBY', 'LIGHT_STBY_GEN',
              'LIGHT_STORES_CONFIG', 'LIGHT_TF_FAIL', 'LIGHT_TO_FLCS',
              'LIGHT_TO_LDG_CONFIG']
        self.tw_gkeys.currentCellChanged.connect(self._save_current_cell)
        self.pb_copy.clicked.connect(self._copy_cell_to_row)
        self.tw_gkeys.setColumnCount(self.keyboard.modes)
        for mode_col in range(self.keyboard.modes):
            self.tw_gkeys.setColumnWidth(mode_col, 200)
        self.tw_gkeys.setRowCount(self.keyboard.gkeys)
        self.tw_gkeys.setVerticalHeaderLabels([f'G{i}' for i in range(1, self.keyboard.gkeys + 1)])
        self.tw_gkeys.setHorizontalHeaderLabels([f'M{i}' for i in range(1, self.keyboard.modes + 1)])

        for r in range(0, self.keyboard.gkeys + 1):
            for c in range(0, self.keyboard.modes + 1):
                completer = QtWidgets.QCompleter(n1)
                completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
                completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
                completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
                completer.setMaxVisibleItems(self._visible_items)
                completer.setModelSorting(QtWidgets.QCompleter.ModelSorting.CaseInsensitivelySortedModel)

                combo = QtWidgets.QComboBox()
                combo.setEditable(True)
                combo.addItems(n2)
                combo.setCompleter(completer)
                self.tw_gkeys.setCellWidget(r, c, combo)

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

    def _copy_cell_to_row(self) -> None:
        """Copy content of current cell to whole row."""
        current_index = self.tw_gkeys.cellWidget(self.current_row, self.current_col).currentIndex()
        for col in {0, 1, 2} - {self.current_col}:  # todo: get number of columns from keyboard
            self.tw_gkeys.cellWidget(self.current_row, col).setCurrentIndex(current_index)

    def event_set(self) -> None:
        """Set event to close running thread."""
        self.event.set()

    def _collect_data_clicked(self) -> None:
        """Collect data for troubleshooting and ask user where to save."""
        zip_file = collect_debug_data()
        try:
            dst_dir = str(Path(os.environ['USERPROFILE']) / 'Desktop')
        except KeyError:
            dst_dir = 'C:\\'
        directory = self._run_file_dialog(for_load=True, for_dir=True, last_dir=lambda: dst_dir)
        try:
            destination = Path(directory) / zip_file.name
            shutil.copy(zip_file, destination)
            LOG.debug(f'Save debug file: {destination}')
        except PermissionError as err:
            LOG.debug(f'Error: {err}, Collected data: {zip_file}')
            self._show_message_box(kind_of='warning', title=err.args[1], message=f'Can not save file:\n{err.filename}')

    def _stop_clicked(self) -> None:
        """Set event to stop DCSpy."""
        self.run_in_background(job=partial(self._fake_progress, total_time=0.3),
                               signal_handlers={'progress': self._progress_by_abs_value})
        self.statusbar.showMessage('Start again or close DCSpy')
        self.pb_start.setEnabled(True)
        self.pb_stop.setEnabled(False)
        self.event_set()

    def _start_clicked(self) -> None:
        """Run real application in thread."""
        # LOG.debug(f'Local DCS-BIOS version: {self._check_local_bios().ver}')
        # keyboard = self.lcd_type.get()
        self.run_in_background(job=partial(self._fake_progress, total_time=0.5),
                               signal_handlers={'progress': self._progress_by_abs_value})
        # self._save_cfg()
        app_params = {'lcd_type': self.keyboard.klass, 'event': self.event}
        app_thread = Thread(target=dcspy_run, kwargs=app_params)
        app_thread.name = 'dcspy-app'
        LOG.debug(f'Starting thread {app_thread} for: {app_params}')
        self.pb_start.setEnabled(False)
        self.pb_stop.setEnabled(True)
        app_thread.start()

    # <=><=><=><=><=><=><=><=><=><=><=> configuration <=><=><=><=><=><=><=><=><=><=><=>
    def apply_configuration(self, cfg: dict) -> None:
        """
        Apply configuration to GUI widgets.

        :param cfg: dictionary with configuration
        """
        self.cb_autostart.setChecked(cfg['autostart'])
        self.cb_show_gui.setChecked(cfg['show_gui'])
        self.cb_lcd_screenshot.setChecked(cfg['save_lcd'])
        self.cb_check_ver.setChecked(cfg['check_ver'])
        self.cb_verbose.setChecked(cfg['verbose'])
        self.cb_ded_font.setChecked(cfg['f16_ded_font'])
        self.le_dcsdir.setText(cfg['dcs'])
        self.le_biosdir.setText(cfg['dcsbios'])
        self.cb_bios_live.setChecked(cfg['git_bios'])
        self.cb_autoupdate_bios.setChecked(cfg['check_bios'])
        self.le_bios_live.setText(cfg['git_bios_ref'])
        self.le_font_name.setText(str(cfg['font_name']))
        self.mono_font = {'large': cfg["font_mono_l"], 'medium': cfg["font_mono_s"], 'small': cfg["font_mono_xs"]}
        self.color_font = {'large': cfg["font_color_l"], 'medium': cfg["font_color_s"], 'small': cfg["font_color_xs"]}

    def save_configuration(self) -> None:
        """Save configuration from GUI."""
        cfg = {
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
            'font_mono_s': self.mono_font['medium'],
            'font_mono_xs': self.mono_font['small'],
            'font_color_l': self.color_font['large'],
            'font_color_s': self.color_font['medium'],
            'font_color_xs': self.color_font['small'],
        }
        if self.keyboard.lcd == 'color':
            font_cfg = {'font_color_l': self.hs_large_font.value(),
                        'font_color_s': self.hs_medium_font.value(),
                        'font_color_xs': self.hs_small_font.value()}
        else:
            font_cfg = {'font_mono_l': self.hs_large_font.value(),
                        'font_mono_s': self.hs_medium_font.value(),
                        'font_mono_xs': self.hs_small_font.value()}
        cfg.update(font_cfg)
        save_cfg(cfg_dict=cfg, filename=self.cfg_file)

    def _reset_defaults_cfg(self) -> None:
        """Set defaults and stop application."""
        save_cfg(cfg_dict=defaults_cfg, filename=self.cfg_file)
        self.config = load_cfg(filename=self.cfg_file)
        self.apply_configuration(self.config)
        for name in ['large', 'medium', 'small']:
            getattr(self, f'hs_{name}_font').setValue(getattr(self, f'{self.keyboard.lcd}_font')[name])
        self._show_message_box(kind_of='warning', title='Restart', message='DCSpy needs to be close.\nPlease start again manually!')
        self.close()

    # <=><=><=><=><=><=><=><=><=><=><=> helpers <=><=><=><=><=><=><=><=><=><=><=>
    def activated(self, reason: QtWidgets.QSystemTrayIcon.ActivationReason) -> None:
        """
        Signal of activation.

        :param reason: reason of activation
        """
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def check_updates(self) -> None:
        """Check for updates and show result."""
        pass

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
    def _fake_progress(progress_callback: QtCore.SignalInstance, total_time: int, steps: int = 100,
                       clean_after: bool = True) -> None:
        """
        Make fake progress for progressbar.

        :param progress_callback: signal to update progress bar
        :param total_time: time for fill-up whole bar (in seconds)
        :param steps: number of steps (default 100)
        :param clean_after: clean progress bar when finish
        """
        for progress_step in range(1, steps + 1):
            sleep(total_time / steps)
            progress_callback.emit(progress_step)
        if clean_after:
            sleep(0.1)
            progress_callback.emit(0)

    def _progress_by_abs_value(self, value: int) -> None:
        """
        Update progress bar by absolute value.

        :param value: absolute value of progress bar
        """
        self.progressbar.setValue(value)

    def _set_icons(self, button: Optional[str] = None, icon_name: Optional[str] = None, color: str = 'black',
                   spin: bool = False) -> None:
        """
        Universal method to set icon for QPushButtons.

        When button is provided without icon_name, current button icon will be removed.
        When none of button nor icon_name are provided, default starting icons are set for all buttons.

        :param button: button name
        :param icon_name: ex: spinner, check, times, pause
        :param color: ex: red, green, black
        :param spin: spinning icon: True or False
        """
        if not (button or icon_name):
            self.pb_mods_dir.setIcon(qtawesome.icon('fa5s.folder', color='brown'))
            self.pb_morrowind_dir.setIcon(qtawesome.icon('fa5s.folder', color='brown'))
            self.pb_tes3cmd.setIcon(qtawesome.icon('fa5s.file', color='brown'))
            self.pb_clean.setIcon(qtawesome.icon('fa5s.snowplow', color='brown'))
            self.pb_report.setIcon(qtawesome.icon('fa5s.file-contract', color='brown'))
            self.pb_back_clean.setIcon(qtawesome.icon('fa5s.arrow-left', color='brown'))
            self.pb_masters_select.setIcon(qtawesome.icon('fa5s.folder', color='brown'))
            self.pb_masters_run.setIcon(qtawesome.icon('fa5s.play', color='brown'))
            return
        btn = getattr(self, button)  # type: ignore
        if spin and icon_name:
            icon = qtawesome.icon(f'{icon_name}', color=color, animation=qtawesome.Spin(btn, 2, 1))
        elif not spin and icon_name:
            icon = qtawesome.icon(f'{icon_name}', color=color)
        else:
            icon = QIcon()
        btn.setIcon(icon)

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
            result_path = QtWidgets.QFileDialog.getExistingDirectory(self, caption='Open Directory', dir=last_dir(),
                                                                     options=QtWidgets.QFileDialog.Option.ShowDirsOnly)
        if for_load and not for_dir:
            result_path = QtWidgets.QFileDialog.getOpenFileName(self, caption='Open File', dir=last_dir(),
                                                                filter=file_filter, options=QtWidgets.QFileDialog.Option.ReadOnly)[0]
        if not for_load and not for_dir:
            result_path = QtWidgets.QFileDialog.getSaveFileName(self, caption='Save File', dir=last_dir(),
                                                                filter=file_filter, options=QtWidgets.QFileDialog.Option.ReadOnly)[0]
        if widget_name is not None and result_path:
            getattr(self, widget_name).setText(result_path)
        return result_path

    def _show_message_box(self, kind_of: str, title: str, message: str = '') -> None:
        """
        Show any QMessageBox delivered with Qt.

        :param kind_of: any of: information, question, warning, critical, about or aboutQt
        :param title: Title of modal window
        :param message: text of message, default is empty
        """
        message_box = getattr(QtWidgets.QMessageBox, kind_of)
        if kind_of == 'aboutQt':
            message_box(self, title)
        else:
            message_box(self, title, message)

    @staticmethod
    def _report_issue() -> None:
        """Open report issue web page in default browser."""
        webbrowser.open('https://github.com/emcek/dcspy/issues', new=2)

    def _show_toolbar(self) -> None:
        """Toggle show and hide toolbar."""
        if self.a_show_toolbar.isChecked():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    def _find_children(self) -> None:
        """Find all widgets of main window."""
        self.statusbar: QtWidgets.QStatusBar = self.findChild(QtWidgets.QStatusBar, 'statusbar')
        self.progressbar: QtWidgets.QProgressBar = self.findChild(QtWidgets.QProgressBar, 'progressbar')
        self.toolbar: QtWidgets.QToolBar = self.findChild(QtWidgets.QToolBar, 'toolbar')
        self.tw_gkeys: QtWidgets.QTableWidget = self.findChild(QtWidgets.QTableWidget, 'tw_gkeys')
        self.sp_completer: QtWidgets.QSpinBox = self.findChild(QtWidgets.QSpinBox, 'sp_completer')
        self.combo_planes: QtWidgets.QComboBox = self.findChild(QtWidgets.QComboBox, 'combo_planes')

        self.a_quit: QAction = self.findChild(QAction, 'a_quit')
        self.a_reset_defaults: QAction = self.findChild(QAction, 'a_reset_defaults')
        self.a_show_toolbar: QAction = self.findChild(QAction, 'a_show_toolbar')
        self.a_about_dcspy: QAction = self.findChild(QAction, 'a_about_dcspy')
        self.a_about_qt: QAction = self.findChild(QAction, 'a_about_qt')
        self.a_report_issue: QAction = self.findChild(QAction, 'a_report_issue')
        self.a_check_updates: QAction = self.findChild(QAction, 'a_check_updates')
        self.a_donate: QAction = self.findChild(QAction, 'a_donate')

        self.pb_start: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'pb_start')
        self.pb_stop: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'pb_stop')
        self.pb_close: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'pb_close')
        self.pb_dcsdir: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'pb_dcsdir')
        self.pb_biosdir: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'pb_biosdir')
        self.pb_collect_data: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'pb_collect_data')
        self.pb_copy: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'pb_copy')

        self.cb_autostart: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'cb_autostart')
        self.cb_show_gui: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'cb_show_gui')
        self.cb_check_ver: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'cb_check_ver')
        self.cb_ded_font: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'cb_ded_font')
        self.cb_lcd_screenshot: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'cb_lcd_screenshot')
        self.cb_verbose: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'cb_verbose')
        self.cb_autoupdate_bios: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'cb_autoupdate_bios')
        self.cb_bios_live: QtWidgets.QCheckBox = self.findChild(QtWidgets.QCheckBox, 'cb_bios_live')

        self.le_dcsdir: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, 'le_dcsdir')
        self.le_biosdir: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, 'le_biosdir')
        self.le_font_name: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, 'le_font_name')
        self.le_bios_live: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, 'le_bios_live')

        self.rb_g19: QtWidgets.QRadioButton = self.findChild(QtWidgets.QRadioButton, 'rb_g19')
        self.rb_g13: QtWidgets.QRadioButton = self.findChild(QtWidgets.QRadioButton, 'rb_g13')
        self.rb_g15v1: QtWidgets.QRadioButton = self.findChild(QtWidgets.QRadioButton, 'rb_g15v1')
        self.rb_g15v2: QtWidgets.QRadioButton = self.findChild(QtWidgets.QRadioButton, 'rb_g15v2')
        self.rb_g510: QtWidgets.QRadioButton = self.findChild(QtWidgets.QRadioButton, 'rb_g510')

        self.hs_large_font: QtWidgets.QSlider = self.findChild(QtWidgets.QSlider, 'hs_large_font')
        self.hs_medium_font: QtWidgets.QSlider = self.findChild(QtWidgets.QSlider, 'hs_medium_font')
        self.hs_small_font: QtWidgets.QSlider = self.findChild(QtWidgets.QSlider, 'hs_small_font')


class WorkerSignals(QtCore.QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:
    * finished - no data
    * error - tuple with exctype, value, traceback.format_exc()
    * result - object/any type - data returned from processing
    * progress - float between 0 and 1 as indication of progress
    """

    finished = QtCore.Signal()
    error = QtCore.Signal(tuple)
    result = QtCore.Signal(object)
    progress = QtCore.Signal(float)


class Worker(QtCore.QRunnable):
    """Runnable worker."""

    def __init__(self, func: Union[partial, Callable], with_progress: bool) -> None:
        """
        Worker thread.

        Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
        :param func: The function callback to run on worker thread
        """
        super().__init__()
        self.func = func
        self.signals = WorkerSignals()
        self.kwargs = {}
        if with_progress:
            self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.Slot()
    def run(self) -> None:
        """Initialise the runner function with passed additional kwargs."""
        try:
            result = self.func(**self.kwargs)
        except Exception:
            exctype, value = exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class UiLoader(QtUiTools.QUiLoader):
    """UI file loader."""
    _baseinstance = None

    def createWidget(self, classname: str, parent: Optional[QtWidgets.QWidget] = None, name='') -> QtWidgets.QWidget:
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

    def loadUi(self, ui_path: Union[str, bytes, os.PathLike], baseinstance=None) -> QtWidgets.QWidget:
        """
        Load UI file.

        :param ui_path: path to UI file
        :param baseinstance:
        :return: QWidget
        """
        self._baseinstance = baseinstance
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QIODevice.ReadOnly)
        try:
            widget = self.load(ui_file)
            QtCore.QMetaObject.connectSlotsByName(widget)
            return widget
        finally:
            ui_file.close()
