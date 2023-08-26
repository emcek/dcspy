import traceback
import webbrowser
from functools import partial
from logging import getLogger
from sys import exc_info
from typing import Callable, Dict, Optional, Union

import qtawesome
from PySide6 import QtCore, QtUiTools
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QLineEdit, QMainWindow,
                               QMessageBox, QProgressBar, QPushButton,
                               QRadioButton, QStatusBar,
                               QSystemTrayIcon, QSlider, QToolBar, QTableWidget, QCompleter, QComboBox)

from dcspy import qtgui_rc

_ = qtgui_rc  # prevent to remove import statement accidentally
__version__ = '2.3.1'
LOG = getLogger(__name__)


class UiLoader(QtUiTools.QUiLoader):
    _baseinstance = None

    def createWidget(self, classname, parent=None, name=''):
        if parent is None and self._baseinstance is not None:
            widget = self._baseinstance
        else:
            widget = super(UiLoader, self).createWidget(classname, parent, name)
            if self._baseinstance is not None:
                setattr(self._baseinstance, name, widget)
        return widget

    def loadUi(self, ui_path, baseinstance=None):
        self._baseinstance = baseinstance
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QIODevice.ReadOnly)
        try:
            widget = self.load(ui_file)
            QtCore.QMetaObject.connectSlotsByName(widget)
            return widget
        finally:
            ui_file.close()


class DcsPyQtGui(QMainWindow):
    """DCSpy Qt6 GUI."""

    def __init__(self) -> None:
        """DCspy Qt6 GUI."""
        super().__init__()
        UiLoader().loadUi(':/ui/ui/qtdcs.ui', self)
        self._find_children()
        self.threadpool = QtCore.QThreadPool.globalInstance()
        LOG.debug(f'QThreadPool with {self.threadpool.maxThreadCount()} thread(s)')
        self.conf_file = ''
        self.config = {}
        self._init_menu_bar()
        # self._apply_gui_configuration(self._get_yaml_file(cli_args.yamlfile))
        self.statusbar.showMessage(f'ver. {__version__}')
        self._init_gkeys()
        self.pb_copy.clicked.connect(self._btn_clicled)
        self.tw_gkeys.currentCellChanged.connect(self.cell7)
        # self._set_icons()
        self.current_row = -1
        self.current_col = -1

    def cell7(self, currentRow, currentColumn, previousRow, previousColumn):
        self.current_row = currentRow
        self.current_col = currentColumn

    def _init_menu_bar(self) -> None:
        """Initialize of menubar."""
        self.a_quit.triggered.connect(self.close)
        self.a_show_toolbar.triggered.connect(self._show_toolbar)
        self.a_report_issue.triggered.connect(self._report_issue)
        # self.actionAboutDCSpy.triggered.connect(AboutDialog(self).open)
        self.a_about_qt.triggered.connect(partial(self._show_message_box, kind_of='aboutQt', title='About Qt'))
        self.a_check_updates.triggered.connect(self.check_updates)

    def _init_gkeys(self):
        n1 = ['ADI_AUX_FLAG', 'ADI_BANK', 'ADI_BUBBLE', 'ADI_GS_BAR', 'ADI_GS_FLAG', 'ADI_GS_POINTER', 'ADI_LOC_BAR', 'ADI_LOC_FLAG', 'ADI_OFF_FLAG',
              'ADI_PITCH', 'ADI_PITCH_TRIM', 'ADI_TURNRATE', 'AIRSPEED', 'AIRSPEED_SET_KNB', 'MACH_INDICATOR', 'MAX_AIRSPEED', 'SET_AIRSPEED',
              'ALT_10000_FT_CNT', 'ALT_1000_FT_CNT', 'ALT_100_FT_CNT', 'ALT_100_FT_PTR', 'ALT_BARO_SET_KNB', 'ALT_MODE_LV', 'ALT_PNEU_FLAG',
              'ALT_PRESSURE_DRUM_0_CNT', 'ALT_PRESSURE_DRUM_1_CNT', 'ALT_PRESSURE_DRUM_2_CNT', 'ALT_PRESSURE_DRUM_3_CNT', 'AOA_VALUE', 'COMM1_MODE_KNB',
              'COMM1_PWR_KNB', 'COMM2_MODE_KNB', 'COMM2_PWR_KNB', 'HOT_MIC_SW', 'IFF_ANT_SEL_SW', 'ILS_PWR_KNB', 'INTERCOM_KNB', 'MSL_KNB', 'SEC_VOICE_KNB',
              'TACAN_KNB', 'TF_KNB', 'THREAT_KNB', 'UHF_ANT_SEL_SW', 'VMS_INHIBIT_SW', 'DL_SW', 'GPS_SW', 'INS_KNB', 'MAP_SW', 'MFD_SW', 'MIDS_LVT_KNB',
              'MMC_PWR_SW', 'ST_STA_SW', 'UFC_SW', 'CMDS_01_EXP_CAT_SW', 'CMDS_02_EXP_CAT_SW', 'CMDS_CH_Amount', 'CMDS_CH_EXP_CAT_SW', 'CMDS_DISPENSE_BTN',
              'CMDS_FL_Amount', 'CMDS_FL_EXP_CAT_SW', 'CMDS_JETT_SW', 'CMDS_JMR_SOURCHE_SW', 'CMDS_MODE_KNB', 'CMDS_MWS_SOURCHE_SW', 'CMDS_O1_Amount',
              'CMDS_O2_Amount', 'CMDS_PROG_KNB', 'CMDS_PWR_SOURCHE_SW', 'CLOCK_CURRTIME_H', 'CLOCK_CURRTIME_MS', 'CLOCK_ELAPSED', 'CLOCK_ELAPSED_TIME_M',
              'CLOCK_ELAPSED_TIME_SEC', 'CLOCK_SET', 'CLOCK_WIND', 'CANOPY_HANDLE', 'CANOPY_JETT_THANDLE', 'CANOPY_POS', 'CANOPY_SW', 'HIDE_STICK', 'SEAT_ADJ',
              'SEAT_EJECT_HANDLE', 'SEAT_EJECT_SAFE', 'SEAT_HEIGHT', 'ADV_MODE_SW', 'ALT_FLAPS_SW', 'AP_PITCH_SW', 'AP_ROLL_SW', 'BIT_SW', 'DIGI_BAK_SW',
              'FLCS_RESET_SW', 'LE_FLAPS_SW', 'MANUAL_PITCH_SW', 'MAN_TF_FLYUP_SW', 'PITCH_TRIM', 'ROLL_TRIM', 'STORES_CONFIG_SW', 'TRIM_AP_DISC_SW',
              'YAW_TRIM', 'DED_LINE_1', 'DED_LINE_2', 'DED_LINE_3', 'DED_LINE_4', 'DED_LINE_5', 'ECM_1_BTN', 'ECM_2_BTN', 'ECM_3_BTN', 'ECM_4_BTN', 'ECM_5_BTN',
              'ECM_6_BTN', 'ECM_BIT_BTN', 'ECM_DIM_KNB', 'ECM_FRM_BTN', 'ECM_PW_SW', 'ECM_RESET_BTN', 'ECM_SPL_BTN', 'ECM_XMIT_SW', 'AIR_SOURCE_KNB',
              'DEFOG_LEVER', 'TEMP_KNB', 'EHSI_CRS_SET', 'EHSI_CRS_SET_KNB', 'EHSI_HDG_SET_BTN', 'EHSI_HDG_SET_KNB', 'EHSI_MODE', 'EPU_SW', 'EPU_SW_COVER_OFF',
              'EPU_SW_COVER_ON', 'HYDRAZIN_VOLUME', 'ELEC_CAUTION', 'EPU_GEN_TEST_SW', 'FLCS_PWR_TEST_SW', 'MAIN_PWR_SW', 'PROBE_HEAT_SW', 'AB_RESET_SW',
              'ENGINE_FTIT', 'ENGINE_NOZZLE_POSITION', 'ENGINE_OIL_PRESSURE', 'ENGINE_TACHOMETER', 'ENG_ANTI_ICE', 'ENG_CONT_SW', 'ENG_CONT_SW_COVER',
              'FIRE_OHEAT_DETECT_BTN', 'JFS_SW', 'MAX_PWR_SW', 'EXT_FORMATION_LIGHTS', 'EXT_POSITION_LIGHTS_WING', 'EXT_POSITION_LIGHT_FUSELAGE',
              'EXT_SPEED_BRAKE_LEFT', 'EXT_SPEED_BRAKE_RIGHT', 'EXT_STROBE_TAIL', 'EXT_TAIL_LIGHT', 'EXT_WOW_LEFT', 'EXT_WOW_NOSE', 'EXT_WOW_RIGHT',
              'AIR_REFUEL_LIGHT_KNB', 'ANTI_COLL_LIGHT_KNB', 'ENGINE_FEED_KNB', 'FORM_LIGHT_KNB', 'LAND_TAXI_LIGHT_SW', 'MAL_IND_LTS_BRT_SW', 'MASTER_LIGHT_SW',
              'POS_FLASH_LIGHT_SW', 'POS_FUSELAGE_LIGHT_SW', 'POS_WING_TAIL_LIGHT_SW', 'AIR_REFUEL_SW', 'EXT_FUEL_TRANS_SW', 'FUELFLOWCOUNTER_100',
              'FUELFLOWCOUNTER_10K', 'FUELFLOWCOUNTER_1K', 'FUELTOTALIZER_100', 'FUELTOTALIZER_10K', 'FUELTOTALIZER_1K', 'FUEL_AL', 'FUEL_FR', 'FUEL_MASTER_CV',
              'FUEL_MASTER_SW', 'FUEL_QTY_SEL_KNB', 'FUEL_QTY_SEL_T_KNB', 'TANK_INTERTING_SW', 'ANTI_SKID_SW', 'BRAKE_CHAN_SW', 'DN_LOCK_BTN', 'GEAR_ALT_BTN',
              'GEAR_ALT_HANDLE', 'GEAR_HANDLE', 'HOOK_SW', 'HORN_SILENCE_BTN', 'HMCS_INT_KNB', 'HUD_ALT_SW', 'HUD_BRT_SW', 'HUD_DED_DATA_SW',
              'HUD_DEPRESS_RET_SW', 'HUD_FP_MARKER_SW', 'HUD_SCALES_SW', 'HUD_SPEED_SW', 'HUD_TEST_SW', 'SYSA_PRESSURE', 'SYSB_PRESSURE',
              'IFF_CODE_DRUM_DIGIT_1', 'IFF_CODE_DRUM_DIGIT_2', 'IFF_CODE_DRUM_DIGIT_3', 'IFF_CODE_DRUM_DIGIT_4', 'IFF_C_I_KNB', 'IFF_ENABLE_SW',
              'IFF_M1_SEL_1', 'IFF_M1_SEL_2', 'IFF_M3_SEL_1', 'IFF_M3_SEL_2', 'IFF_M4_CODE_SW', 'IFF_M4_MONITOR_SW', 'IFF_M4_REPLY_SW', 'IFF_MASTER_KNB',
              'AOA_INDEX_BRT_KNB', 'AR_STATUS_BRT_KNB', 'FLOOD_CONSOLES_BRT_KNB', 'FLOOD_INST_PNL_BRT_KNB', 'MAL_IND_LTS_TEST', 'MASTER_CAUTION',
              'PRI_CONSOLES_BRT_KNB', 'PRI_DATA_DISPLAY_BRT_KNB', 'PRI_INST_PNL_BRT_KNB', 'LIGHT_CONSLES', 'LIGHT_CONSLES_FLOOD', 'LIGHT_INST_PNL',
              'LIGHT_INST_PNL_FLOOD', 'KY58_FILL_KNB', 'KY58_MODE_KNB', 'KY58_PWR_KNB', 'KY58_VOL_KNB', 'PLAIN_CIPHER_SW', 'ZEROIZE_SW', 'ZEROIZE_SW_COVER',
              'MFD_L_1', 'MFD_L_10', 'MFD_L_11', 'MFD_L_12', 'MFD_L_13', 'MFD_L_14', 'MFD_L_15', 'MFD_L_16', 'MFD_L_17', 'MFD_L_18', 'MFD_L_19', 'MFD_L_2',
              'MFD_L_20', 'MFD_L_3', 'MFD_L_4', 'MFD_L_5', 'MFD_L_6', 'MFD_L_7', 'MFD_L_8', 'MFD_L_9', 'MFD_L_BRT_SW', 'MFD_L_CON_SW', 'MFD_L_GAIN_SW',
              'MFD_L_SYM_SW', 'MFD_R_1', 'MFD_R_10', 'MFD_R_11', 'MFD_R_12', 'MFD_R_13', 'MFD_R_14', 'MFD_R_15', 'MFD_R_16', 'MFD_R_17', 'MFD_R_18', 'MFD_R_19',
              'MFD_R_2', 'MFD_R_20', 'MFD_R_3', 'MFD_R_4', 'MFD_R_5', 'MFD_R_6', 'MFD_R_7', 'MFD_R_8', 'MFD_R_9', 'MFD_R_BRT_SW', 'MFD_R_CON_SW',
              'MFD_R_GAIN_SW', 'MFD_R_SYM_SW', 'ALT_REL_BTN', 'EMERG_STORE_JETT', 'GND_JETT_ENABLE_SW', 'LASER_ARM_SW', 'MASTER_ARM_SW', 'COCKPIT_ALITITUDE',
              'FLOW_INDICATOR', 'FLOW_INDICATOR_LIGHT', 'OBOGS_SW', 'OXYGEN_PRESSURE', 'OXY_DILUTER_LVR', 'OXY_EMERG_LVR', 'OXY_SUPPLY_LVR', 'RWR_ACT_PWR_BTN',
              'RWR_ALT_BTN', 'RWR_HANDOFF_BTN', 'RWR_IND_DIM_KNB', 'RWR_INTENS_KNB', 'RWR_LAUNCH_BTN', 'RWR_MODE_BTN', 'RWR_PWR_BTN', 'RWR_SEARCH_BTN',
              'RWR_SYS_TEST_BTN', 'RWR_T_BTN', 'RWR_UNKNOWN_SHIP_BTN', 'SAI_AIRCRAFTREFERENCESYMBOL', 'SAI_BANK', 'SAI_BANK_ARROW', 'SAI_CAGE', 'SAI_KNB_ARROW',
              'SAI_OFF_FLAG', 'SAI_PITCH', 'SAI_PITCH_TRIM', 'FCR_PWR_SW', 'HDPT_SW_L', 'HDPT_SW_R', 'RDR_ALT_PWR_SW', 'SPEEDBRAKE_INDICATOR', 'PITCHTRIMIND',
              'ROLLTRIMIND', 'F_ACK_BTN', 'ICP_AA_MODE_BTN', 'ICP_AG_MODE_BTN', 'ICP_BTN_0', 'ICP_BTN_1', 'ICP_BTN_2', 'ICP_BTN_3', 'ICP_BTN_4', 'ICP_BTN_5',
              'ICP_BTN_6', 'ICP_BTN_7', 'ICP_BTN_8', 'ICP_BTN_9', 'ICP_COM1_BTN', 'ICP_COM2_BTN', 'ICP_DATA_RTN_SEQ_SW', 'ICP_DATA_UP_DN_SW', 'ICP_DED_SW',
              'ICP_DRIFT_SW', 'ICP_ENTR_BTN', 'ICP_FLIR_GAIN_SW', 'ICP_FLIR_SW', 'ICP_HUD_BRT_KNB', 'ICP_IFF_BTN', 'ICP_LIST_BTN', 'ICP_RASTER_BRT_KNB',
              'ICP_RASTER_CONTR_KNB', 'ICP_RCL_BTN', 'ICP_RETICLE_DEPRESS_KNB', 'ICP_WX_BTN', 'IFF_ID_BTN', 'RF_SW', 'UHF_CHAN_DISP', 'UHF_CHAN_KNB',
              'UHF_DOOR', 'UHF_FREQ_0025_KNB', 'UHF_FREQ_01_KNB', 'UHF_FREQ_100_KNB', 'UHF_FREQ_10_KNB', 'UHF_FREQ_1_KNB', 'UHF_FREQ_DISP', 'UHF_FUNC_KNB',
              'UHF_MODE_KNB', 'UHF_SQUELCH_SW', 'UHF_STATUS_BTN', 'UHF_TEST_BTN', 'UHF_TONE_BTN', 'UHF_VOL_KNB', 'VVI', 'LIGHT_ACFT_BATT_FAIL', 'LIGHT_ACTIVE',
              'LIGHT_AFT_FUEL_LOW', 'LIGHT_AIR', 'LIGHT_ANTI_SKID', 'LIGHT_AOA_DN', 'LIGHT_AOA_MID', 'LIGHT_AOA_UP', 'LIGHT_AR_NWS', 'LIGHT_ATF_NOT',
              'LIGHT_AVIONICS_FAULT', 'LIGHT_BUC', 'LIGHT_CABIN_PRESS', 'LIGHT_CADC', 'LIGHT_CANOPY', 'LIGHT_CAUTION_1', 'LIGHT_CAUTION_2', 'LIGHT_CAUTION_3',
              'LIGHT_CAUTION_4', 'LIGHT_CAUTION_5', 'LIGHT_CAUTION_6', 'LIGHT_CMDS_DISP', 'LIGHT_CMDS_GO', 'LIGHT_CMDS_NO_GO', 'LIGHT_CMDS_RDY', 'LIGHT_DBU_ON',
              'LIGHT_DISC', 'LIGHT_ECM', 'LIGHT_ECM_1_A', 'LIGHT_ECM_1_F', 'LIGHT_ECM_1_S', 'LIGHT_ECM_1_T', 'LIGHT_ECM_2_A', 'LIGHT_ECM_2_F', 'LIGHT_ECM_2_S',
              'LIGHT_ECM_2_T', 'LIGHT_ECM_3_A', 'LIGHT_ECM_3_F', 'LIGHT_ECM_3_S', 'LIGHT_ECM_3_T', 'LIGHT_ECM_4_A', 'LIGHT_ECM_4_F', 'LIGHT_ECM_4_S',
              'LIGHT_ECM_4_T', 'LIGHT_ECM_5_A', 'LIGHT_ECM_5_F', 'LIGHT_ECM_5_S', 'LIGHT_ECM_5_T', 'LIGHT_ECM_A', 'LIGHT_ECM_F', 'LIGHT_ECM_FRM_A',
              'LIGHT_ECM_FRM_F', 'LIGHT_ECM_FRM_S', 'LIGHT_ECM_FRM_T', 'LIGHT_ECM_S', 'LIGHT_ECM_SPL_A', 'LIGHT_ECM_SPL_F', 'LIGHT_ECM_SPL_S',
              'LIGHT_ECM_SPL_T', 'LIGHT_ECM_T', 'LIGHT_EDGE', 'LIGHT_EEC', 'LIGHT_ELEC', 'LIGHT_ELEC_SYS', 'LIGHT_ENGINE', 'LIGHT_ENGINE_FAULT',
              'LIGHT_ENG_FIRE', 'LIGHT_EPU', 'LIGHT_EPU_GEN', 'LIGHT_EPU_PMG', 'LIGHT_EQUIP_HOT', 'LIGHT_FLCS', 'LIGHT_FLCS_FAULT', 'LIGHT_FLCS_PMG',
              'LIGHT_FLCS_PWR_A', 'LIGHT_FLCS_PWR_B', 'LIGHT_FLCS_PWR_C', 'LIGHT_FLCS_PWR_D', 'LIGHT_FLCS_RLY', 'LIGHT_FL_FAIL', 'LIGHT_FL_RUN',
              'LIGHT_FUEL_OIL_HOT', 'LIGHT_FWD_FUEL_LOW', 'LIGHT_GEAR_L', 'LIGHT_GEAR_N', 'LIGHT_GEAR_R', 'LIGHT_GEAR_WARN', 'LIGHT_HOOK', 'LIGHT_HYDRAZN',
              'LIGHT_HYD_OIL_PRESS', 'LIGHT_IFF', 'LIGHT_INLET_ICING', 'LIGHT_JFS_RUN', 'LIGHT_MAIN_GEN', 'LIGHT_MARKER_BEACON', 'LIGHT_MASTER_CAUTION',
              'LIGHT_NUCLEAR', 'LIGHT_NWS_FAIL', 'LIGHT_OBOGS', 'LIGHT_OVERHEAT', 'LIGHT_OXY_LOW', 'LIGHT_PROBE_HEAT', 'LIGHT_RADAR_ALT', 'LIGHT_RDY',
              'LIGHT_RWR_ACTIVITY', 'LIGHT_RWR_ACT_POWER', 'LIGHT_RWR_ALT', 'LIGHT_RWR_ALT_LOW', 'LIGHT_RWR_HANDOFF_H', 'LIGHT_RWR_HANDOFF_UP',
              'LIGHT_RWR_MODE_OPEN', 'LIGHT_RWR_MODE_PRI', 'LIGHT_RWR_MSL_LAUNCH', 'LIGHT_RWR_POWER', 'LIGHT_RWR_SEARCH', 'LIGHT_RWR_SHIP_UNK',
              'LIGHT_RWR_SYSTEST', 'LIGHT_RWR_TGTSEP_DN', 'LIGHT_RWR_TGTSEP_UP', 'LIGHT_SEAT_NOT', 'LIGHT_SEC', 'LIGHT_STBY', 'LIGHT_STBY_GEN',
              'LIGHT_STORES_CONFIG', 'LIGHT_TF_FAIL', 'LIGHT_TO_FLCS', 'LIGHT_TO_LDG_CONFIG']
        n2 = ['', '-- ADI --', 'ADI_AUX_FLAG', 'ADI_BANK', 'ADI_BUBBLE', 'ADI_GS_BAR', 'ADI_GS_FLAG', 'ADI_GS_POINTER', 'ADI_LOC_BAR', 'ADI_LOC_FLAG',
              'ADI_OFF_FLAG', 'ADI_PITCH', 'ADI_PITCH_TRIM', 'ADI_TURNRATE', '-- Airspeed Indicator --', 'AIRSPEED', 'AIRSPEED_SET_KNB', 'MACH_INDICATOR',
              'MAX_AIRSPEED', 'SET_AIRSPEED', '-- Altimeter --', 'ALT_10000_FT_CNT', 'ALT_1000_FT_CNT', 'ALT_100_FT_CNT', 'ALT_100_FT_PTR', 'ALT_BARO_SET_KNB',
              'ALT_MODE_LV', 'ALT_PNEU_FLAG', 'ALT_PRESSURE_DRUM_0_CNT', 'ALT_PRESSURE_DRUM_1_CNT', 'ALT_PRESSURE_DRUM_2_CNT', 'ALT_PRESSURE_DRUM_3_CNT',
              '-- AoA --', 'AOA_VALUE', '-- Audio Panel --', 'COMM1_MODE_KNB', 'COMM1_PWR_KNB', 'COMM2_MODE_KNB', 'COMM2_PWR_KNB', 'HOT_MIC_SW',
              'IFF_ANT_SEL_SW', 'ILS_PWR_KNB', 'INTERCOM_KNB', 'MSL_KNB', 'SEC_VOICE_KNB', 'TACAN_KNB', 'TF_KNB', 'THREAT_KNB', 'UHF_ANT_SEL_SW',
              'VMS_INHIBIT_SW', '-- Avionic Panel --', 'DL_SW', 'GPS_SW', 'INS_KNB', 'MAP_SW', 'MFD_SW', 'MIDS_LVT_KNB', 'MMC_PWR_SW', 'ST_STA_SW', 'UFC_SW',
              '-- CMDS --', 'CMDS_01_EXP_CAT_SW', 'CMDS_02_EXP_CAT_SW', 'CMDS_CH_Amount', 'CMDS_CH_EXP_CAT_SW', 'CMDS_DISPENSE_BTN', 'CMDS_FL_Amount',
              'CMDS_FL_EXP_CAT_SW', 'CMDS_JETT_SW', 'CMDS_JMR_SOURCHE_SW', 'CMDS_MODE_KNB', 'CMDS_MWS_SOURCHE_SW', 'CMDS_O1_Amount', 'CMDS_O2_Amount',
              'CMDS_PROG_KNB', 'CMDS_PWR_SOURCHE_SW', '-- Clock --', 'CLOCK_CURRTIME_H', 'CLOCK_CURRTIME_MS', 'CLOCK_ELAPSED', 'CLOCK_ELAPSED_TIME_M',
              'CLOCK_ELAPSED_TIME_SEC', 'CLOCK_SET', 'CLOCK_WIND', '-- Cockpit Mechanics --', 'CANOPY_HANDLE', 'CANOPY_JETT_THANDLE', 'CANOPY_POS', 'CANOPY_SW',
              'HIDE_STICK', 'SEAT_ADJ', 'SEAT_EJECT_HANDLE', 'SEAT_EJECT_SAFE', 'SEAT_HEIGHT', '-- Control Interface --', 'ADV_MODE_SW', 'ALT_FLAPS_SW',
              'AP_PITCH_SW', 'AP_ROLL_SW', 'BIT_SW', 'DIGI_BAK_SW', 'FLCS_RESET_SW', 'LE_FLAPS_SW', 'MANUAL_PITCH_SW', 'MAN_TF_FLYUP_SW', 'PITCH_TRIM',
              'ROLL_TRIM', 'STORES_CONFIG_SW', 'TRIM_AP_DISC_SW', 'YAW_TRIM', '-- DED Output Data --', 'DED_LINE_1', 'DED_LINE_2', 'DED_LINE_3', 'DED_LINE_4',
              'DED_LINE_5', '-- ECM --', 'ECM_1_BTN', 'ECM_2_BTN', 'ECM_3_BTN', 'ECM_4_BTN', 'ECM_5_BTN', 'ECM_6_BTN', 'ECM_BIT_BTN', 'ECM_DIM_KNB',
              'ECM_FRM_BTN', 'ECM_PW_SW', 'ECM_RESET_BTN', 'ECM_SPL_BTN', 'ECM_XMIT_SW', '-- ECS --', 'AIR_SOURCE_KNB', 'DEFOG_LEVER', 'TEMP_KNB', '-- EHSI --',
              'EHSI_CRS_SET', 'EHSI_CRS_SET_KNB', 'EHSI_HDG_SET_BTN', 'EHSI_HDG_SET_KNB', 'EHSI_MODE', '-- EPU --', 'EPU_SW', 'EPU_SW_COVER_OFF',
              'EPU_SW_COVER_ON', 'HYDRAZIN_VOLUME', '-- Electric System --', 'ELEC_CAUTION', 'EPU_GEN_TEST_SW', 'FLCS_PWR_TEST_SW', 'MAIN_PWR_SW',
              'PROBE_HEAT_SW', '-- Engine --', 'AB_RESET_SW', 'ENGINE_FTIT', 'ENGINE_NOZZLE_POSITION', 'ENGINE_OIL_PRESSURE', 'ENGINE_TACHOMETER',
              'ENG_ANTI_ICE', 'ENG_CONT_SW', 'ENG_CONT_SW_COVER', 'FIRE_OHEAT_DETECT_BTN', 'JFS_SW', 'MAX_PWR_SW', '-- External Aircraft Model --',
              'EXT_FORMATION_LIGHTS', 'EXT_POSITION_LIGHTS_WING', 'EXT_POSITION_LIGHT_FUSELAGE', 'EXT_SPEED_BRAKE_LEFT', 'EXT_SPEED_BRAKE_RIGHT',
              'EXT_STROBE_TAIL', 'EXT_TAIL_LIGHT', 'EXT_WOW_LEFT', 'EXT_WOW_NOSE', 'EXT_WOW_RIGHT', '-- External Lights --', 'AIR_REFUEL_LIGHT_KNB',
              'ANTI_COLL_LIGHT_KNB', 'ENGINE_FEED_KNB', 'FORM_LIGHT_KNB', 'LAND_TAXI_LIGHT_SW', 'MAL_IND_LTS_BRT_SW', 'MASTER_LIGHT_SW', 'POS_FLASH_LIGHT_SW',
              'POS_FUSELAGE_LIGHT_SW', 'POS_WING_TAIL_LIGHT_SW', '-- Fuel System --', 'AIR_REFUEL_SW', 'EXT_FUEL_TRANS_SW', 'FUELFLOWCOUNTER_100',
              'FUELFLOWCOUNTER_10K', 'FUELFLOWCOUNTER_1K', 'FUELTOTALIZER_100', 'FUELTOTALIZER_10K', 'FUELTOTALIZER_1K', 'FUEL_AL', 'FUEL_FR', 'FUEL_MASTER_CV',
              'FUEL_MASTER_SW', 'FUEL_QTY_SEL_KNB', 'FUEL_QTY_SEL_T_KNB', 'TANK_INTERTING_SW', '-- Gear System --', 'ANTI_SKID_SW', 'BRAKE_CHAN_SW',
              'DN_LOCK_BTN', 'GEAR_ALT_BTN', 'GEAR_ALT_HANDLE', 'GEAR_HANDLE', 'HOOK_SW', 'HORN_SILENCE_BTN', '-- HMCS --', 'HMCS_INT_KNB',
              '-- HUD Control Panel --', 'HUD_ALT_SW', 'HUD_BRT_SW', 'HUD_DED_DATA_SW', 'HUD_DEPRESS_RET_SW', 'HUD_FP_MARKER_SW', 'HUD_SCALES_SW',
              'HUD_SPEED_SW', 'HUD_TEST_SW', '-- Hydraulic Pressure Indicators --', 'SYSA_PRESSURE', 'SYSB_PRESSURE', '-- IFF --', 'IFF_CODE_DRUM_DIGIT_1',
              'IFF_CODE_DRUM_DIGIT_2', 'IFF_CODE_DRUM_DIGIT_3', 'IFF_CODE_DRUM_DIGIT_4', 'IFF_C_I_KNB', 'IFF_ENABLE_SW', 'IFF_M1_SEL_1', 'IFF_M1_SEL_2',
              'IFF_M3_SEL_1', 'IFF_M3_SEL_2', 'IFF_M4_CODE_SW', 'IFF_M4_MONITOR_SW', 'IFF_M4_REPLY_SW', 'IFF_MASTER_KNB', '-- Interior Lights --',
              'AOA_INDEX_BRT_KNB', 'AR_STATUS_BRT_KNB', 'FLOOD_CONSOLES_BRT_KNB', 'FLOOD_INST_PNL_BRT_KNB', 'MAL_IND_LTS_TEST', 'MASTER_CAUTION',
              'PRI_CONSOLES_BRT_KNB', 'PRI_DATA_DISPLAY_BRT_KNB', 'PRI_INST_PNL_BRT_KNB', '-- Interior Lights Indicators --', 'LIGHT_CONSLES',
              'LIGHT_CONSLES_FLOOD', 'LIGHT_INST_PNL', 'LIGHT_INST_PNL_FLOOD', '-- KY-58 --', 'KY58_FILL_KNB', 'KY58_MODE_KNB', 'KY58_PWR_KNB', 'KY58_VOL_KNB',
              'PLAIN_CIPHER_SW', 'ZEROIZE_SW', 'ZEROIZE_SW_COVER', '-- MFD Left --', 'MFD_L_1', 'MFD_L_10', 'MFD_L_11', 'MFD_L_12', 'MFD_L_13', 'MFD_L_14',
              'MFD_L_15', 'MFD_L_16', 'MFD_L_17', 'MFD_L_18', 'MFD_L_19', 'MFD_L_2', 'MFD_L_20', 'MFD_L_3', 'MFD_L_4', 'MFD_L_5', 'MFD_L_6', 'MFD_L_7',
              'MFD_L_8', 'MFD_L_9', 'MFD_L_BRT_SW', 'MFD_L_CON_SW', 'MFD_L_GAIN_SW', 'MFD_L_SYM_SW', '-- MFD Right --', 'MFD_R_1', 'MFD_R_10', 'MFD_R_11',
              'MFD_R_12', 'MFD_R_13', 'MFD_R_14', 'MFD_R_15', 'MFD_R_16', 'MFD_R_17', 'MFD_R_18', 'MFD_R_19', 'MFD_R_2', 'MFD_R_20', 'MFD_R_3', 'MFD_R_4',
              'MFD_R_5', 'MFD_R_6', 'MFD_R_7', 'MFD_R_8', 'MFD_R_9', 'MFD_R_BRT_SW', 'MFD_R_CON_SW', 'MFD_R_GAIN_SW', 'MFD_R_SYM_SW', '-- MMC --',
              'ALT_REL_BTN', 'EMERG_STORE_JETT', 'GND_JETT_ENABLE_SW', 'LASER_ARM_SW', 'MASTER_ARM_SW', '-- Oxygen System --', 'COCKPIT_ALITITUDE',
              'FLOW_INDICATOR', 'FLOW_INDICATOR_LIGHT', 'OBOGS_SW', 'OXYGEN_PRESSURE', 'OXY_DILUTER_LVR', 'OXY_EMERG_LVR', 'OXY_SUPPLY_LVR', '-- RWR --',
              'RWR_ACT_PWR_BTN', 'RWR_ALT_BTN', 'RWR_HANDOFF_BTN', 'RWR_IND_DIM_KNB', 'RWR_INTENS_KNB', 'RWR_LAUNCH_BTN', 'RWR_MODE_BTN', 'RWR_PWR_BTN',
              'RWR_SEARCH_BTN', 'RWR_SYS_TEST_BTN', 'RWR_T_BTN', 'RWR_UNKNOWN_SHIP_BTN', '-- SAI --', 'SAI_AIRCRAFTREFERENCESYMBOL', 'SAI_BANK',
              'SAI_BANK_ARROW', 'SAI_CAGE', 'SAI_KNB_ARROW', 'SAI_OFF_FLAG', 'SAI_PITCH', 'SAI_PITCH_TRIM', '-- Sensor Panel --', 'FCR_PWR_SW', 'HDPT_SW_L',
              'HDPT_SW_R', 'RDR_ALT_PWR_SW', '-- Speed Brake --', 'SPEEDBRAKE_INDICATOR', '-- Trim Indicators --', 'PITCHTRIMIND', 'ROLLTRIMIND', '-- UFC --',
              'F_ACK_BTN', 'ICP_AA_MODE_BTN', 'ICP_AG_MODE_BTN', 'ICP_BTN_0', 'ICP_BTN_1', 'ICP_BTN_2', 'ICP_BTN_3', 'ICP_BTN_4', 'ICP_BTN_5', 'ICP_BTN_6',
              'ICP_BTN_7', 'ICP_BTN_8', 'ICP_BTN_9', 'ICP_COM1_BTN', 'ICP_COM2_BTN', 'ICP_DATA_RTN_SEQ_SW', 'ICP_DATA_UP_DN_SW', 'ICP_DED_SW', 'ICP_DRIFT_SW',
              'ICP_ENTR_BTN', 'ICP_FLIR_GAIN_SW', 'ICP_FLIR_SW', 'ICP_HUD_BRT_KNB', 'ICP_IFF_BTN', 'ICP_LIST_BTN', 'ICP_RASTER_BRT_KNB', 'ICP_RASTER_CONTR_KNB',
              'ICP_RCL_BTN', 'ICP_RETICLE_DEPRESS_KNB', 'ICP_WX_BTN', 'IFF_ID_BTN', 'RF_SW', '-- UHF --', 'UHF_CHAN_DISP', 'UHF_CHAN_KNB', 'UHF_DOOR',
              'UHF_FREQ_0025_KNB', 'UHF_FREQ_01_KNB', 'UHF_FREQ_100_KNB', 'UHF_FREQ_10_KNB', 'UHF_FREQ_1_KNB', 'UHF_FREQ_DISP', 'UHF_FUNC_KNB', 'UHF_MODE_KNB',
              'UHF_SQUELCH_SW', 'UHF_STATUS_BTN', 'UHF_TEST_BTN', 'UHF_TONE_BTN', 'UHF_VOL_KNB', '-- Vertical Velocity Indicator --', 'VVI',
              '-- Warning, Caution and IndicatorLights --', 'LIGHT_ACFT_BATT_FAIL', 'LIGHT_ACTIVE', 'LIGHT_AFT_FUEL_LOW', 'LIGHT_AIR', 'LIGHT_ANTI_SKID',
              'LIGHT_AOA_DN', 'LIGHT_AOA_MID', 'LIGHT_AOA_UP', 'LIGHT_AR_NWS', 'LIGHT_ATF_NOT', 'LIGHT_AVIONICS_FAULT', 'LIGHT_BUC', 'LIGHT_CABIN_PRESS',
              'LIGHT_CADC', 'LIGHT_CANOPY', 'LIGHT_CAUTION_1', 'LIGHT_CAUTION_2', 'LIGHT_CAUTION_3', 'LIGHT_CAUTION_4', 'LIGHT_CAUTION_5', 'LIGHT_CAUTION_6',
              'LIGHT_CMDS_DISP', 'LIGHT_CMDS_GO', 'LIGHT_CMDS_NO_GO', 'LIGHT_CMDS_RDY', 'LIGHT_DBU_ON', 'LIGHT_DISC', 'LIGHT_ECM', 'LIGHT_ECM_1_A',
              'LIGHT_ECM_1_F', 'LIGHT_ECM_1_S', 'LIGHT_ECM_1_T', 'LIGHT_ECM_2_A', 'LIGHT_ECM_2_F', 'LIGHT_ECM_2_S', 'LIGHT_ECM_2_T', 'LIGHT_ECM_3_A',
              'LIGHT_ECM_3_F', 'LIGHT_ECM_3_S', 'LIGHT_ECM_3_T', 'LIGHT_ECM_4_A', 'LIGHT_ECM_4_F', 'LIGHT_ECM_4_S', 'LIGHT_ECM_4_T', 'LIGHT_ECM_5_A',
              'LIGHT_ECM_5_F', 'LIGHT_ECM_5_S', 'LIGHT_ECM_5_T', 'LIGHT_ECM_A', 'LIGHT_ECM_F', 'LIGHT_ECM_FRM_A', 'LIGHT_ECM_FRM_F', 'LIGHT_ECM_FRM_S',
              'LIGHT_ECM_FRM_T', 'LIGHT_ECM_S', 'LIGHT_ECM_SPL_A', 'LIGHT_ECM_SPL_F', 'LIGHT_ECM_SPL_S', 'LIGHT_ECM_SPL_T', 'LIGHT_ECM_T', 'LIGHT_EDGE',
              'LIGHT_EEC', 'LIGHT_ELEC', 'LIGHT_ELEC_SYS', 'LIGHT_ENGINE', 'LIGHT_ENGINE_FAULT', 'LIGHT_ENG_FIRE', 'LIGHT_EPU', 'LIGHT_EPU_GEN',
              'LIGHT_EPU_PMG', 'LIGHT_EQUIP_HOT', 'LIGHT_FLCS', 'LIGHT_FLCS_FAULT', 'LIGHT_FLCS_PMG', 'LIGHT_FLCS_PWR_A', 'LIGHT_FLCS_PWR_B',
              'LIGHT_FLCS_PWR_C', 'LIGHT_FLCS_PWR_D', 'LIGHT_FLCS_RLY', 'LIGHT_FL_FAIL', 'LIGHT_FL_RUN', 'LIGHT_FUEL_OIL_HOT', 'LIGHT_FWD_FUEL_LOW',
              'LIGHT_GEAR_L', 'LIGHT_GEAR_N', 'LIGHT_GEAR_R', 'LIGHT_GEAR_WARN', 'LIGHT_HOOK', 'LIGHT_HYDRAZN', 'LIGHT_HYD_OIL_PRESS', 'LIGHT_IFF',
              'LIGHT_INLET_ICING', 'LIGHT_JFS_RUN', 'LIGHT_MAIN_GEN', 'LIGHT_MARKER_BEACON', 'LIGHT_MASTER_CAUTION', 'LIGHT_NUCLEAR', 'LIGHT_NWS_FAIL',
              'LIGHT_OBOGS', 'LIGHT_OVERHEAT', 'LIGHT_OXY_LOW', 'LIGHT_PROBE_HEAT', 'LIGHT_RADAR_ALT', 'LIGHT_RDY', 'LIGHT_RWR_ACTIVITY', 'LIGHT_RWR_ACT_POWER',
              'LIGHT_RWR_ALT', 'LIGHT_RWR_ALT_LOW', 'LIGHT_RWR_HANDOFF_H', 'LIGHT_RWR_HANDOFF_UP', 'LIGHT_RWR_MODE_OPEN', 'LIGHT_RWR_MODE_PRI',
              'LIGHT_RWR_MSL_LAUNCH', 'LIGHT_RWR_POWER', 'LIGHT_RWR_SEARCH', 'LIGHT_RWR_SHIP_UNK', 'LIGHT_RWR_SYSTEST', 'LIGHT_RWR_TGTSEP_DN',
              'LIGHT_RWR_TGTSEP_UP', 'LIGHT_SEAT_NOT', 'LIGHT_SEC', 'LIGHT_STBY', 'LIGHT_STBY_GEN', 'LIGHT_STORES_CONFIG', 'LIGHT_TF_FAIL', 'LIGHT_TO_FLCS',
              'LIGHT_TO_LDG_CONFIG']
        self.tw_gkeys.setColumnCount(3)
        self.tw_gkeys.setColumnWidth(0, 200)
        self.tw_gkeys.setColumnWidth(1, 200)
        self.tw_gkeys.setColumnWidth(2, 200)
        self.tw_gkeys.setRowCount(5)
        self.tw_gkeys.setVerticalHeaderLabels([f'G{i}' for i in range(1, 6)])
        self.tw_gkeys.setHorizontalHeaderLabels([f'M{i}' for i in range(1, 4)])

        for e in range(0, 5):
            for c in range(0, 3):
                # self.tw_gkeys.setItem(row, 0, QTableWidgetItem(e['First Name']))
                # self.tw_gkeys.setItem(row, 1, QTableWidgetItem(e['Last Name']))
                # self.tw_gkeys.setItem(row, 2, QTableWidgetItem(str(e['Age'])))
                completer = QCompleter(n1)
                completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
                completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
                completer.setFilterMode(QtCore.Qt.MatchFlag.MatchStartsWith)
                completer.setMaxVisibleItems(9)
                completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)

                combo = QComboBox(self)
                combo.setEditable(True)
                combo.addItems(n2)
                combo.setCompleter(completer)
                self.tw_gkeys.setCellWidget(e, c, combo)

    def _btn_clicled(self):
        t = self.tw_gkeys.cellWidget(self.current_row, self.current_col).currentIndex()
        s = {0, 1, 2} - {self.current_col}
        for col in s:
            self.tw_gkeys.cellWidget(self.current_row, col).setCurrentIndex(t)

    # <=><=><=><=><=><=><=><=><=><=><=> helpers <=><=><=><=><=><=><=><=><=><=><=>
    def activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Signal of activation.

        :param reason: reason of activation
        """
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def trigger_autosave(self) -> None:
        """Just trigger save configuration."""
        self.save_config()

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
        self.logger.debug(f'bg job for: {job_name} args: {args} kwargs: {kwargs} signals {signals}')
        self.threadpool.start(worker)

    def _set_icons(self, button: Optional[str] = None, icon_name: Optional[str] = None, color: str = 'black', spin: bool = False):
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
            result_path = QFileDialog.getExistingDirectory(self, caption='Open Directory', directory=last_dir(),
                                                           options=QFileDialog.Option.ShowDirsOnly)
        if for_load and not for_dir:
            result_path = QFileDialog.getOpenFileName(self, caption='Open File', directory=last_dir(),
                                                      filter=file_filter, options=QFileDialog.Option.ReadOnly)[0]
        if not for_load and not for_dir:
            result_path = QFileDialog.getSaveFileName(self, caption='Save File', directory=last_dir(),
                                                      filter=file_filter, options=QFileDialog.Option.ReadOnly)[0]
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
        message_box = getattr(QMessageBox, kind_of)
        if kind_of == 'aboutQt':
            message_box(self, title)
        else:
            message_box(self, title, message)

    @staticmethod
    def _report_issue():
        """Open report issue web page in default browser."""
        webbrowser.open('https://github.com/emcek/dcspy/issues', new=2)

    def _show_toolbar(self):
        if self.a_show_toolbar.isChecked():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    def _find_children(self) -> None:
        """Find all widgets of main window."""
        self.statusbar = self.findChild(QStatusBar, 'statusbar')
        self.progressbar = self.findChild(QProgressBar, 'progressbar')
        self.toolbar = self.findChild(QToolBar, 'toolbar')
        self.tw_gkeys = self.findChild(QTableWidget, 'tw_gkeys')

        self.a_quit = self.findChild(QAction, 'a_quit')
        self.a_show_toolbar = self.findChild(QAction, 'a_show_toolbar')
        self.a_about_dcspy = self.findChild(QAction, 'a_about_dcspy')
        self.a_about_qt = self.findChild(QAction, 'a_about_qt')
        self.a_report_issue = self.findChild(QAction, 'a_report_issue')
        self.a_check_updates = self.findChild(QAction, 'a_check_updates')

        self.pb_start = self.findChild(QPushButton, 'pb_start')
        self.pb_stop = self.findChild(QPushButton, 'pb_stop')
        self.pb_close = self.findChild(QPushButton, 'pb_close')
        self.pb_dcsdir = self.findChild(QPushButton, 'pb_dcsdir')
        self.pb_biosdir = self.findChild(QPushButton, 'pb_biosdir')
        self.pb_collect_data = self.findChild(QPushButton, 'pb_collect_data')
        self.pb_copy = self.findChild(QPushButton, 'pb_copy')

        self.cb_autostart = self.findChild(QCheckBox, 'cb_autostart')
        self.cb_show_gui = self.findChild(QCheckBox, 'cb_show_gui')
        self.cb_check_ver = self.findChild(QCheckBox, 'cb_check_ver')
        self.cb_ded_font = self.findChild(QCheckBox, 'cb_ded_font')
        self.cb_lcd_screenshot = self.findChild(QCheckBox, 'cb_lcd_screenshot')
        self.cb_verbose = self.findChild(QCheckBox, 'cb_verbose')
        self.cb_autoupdate_bios = self.findChild(QCheckBox, 'cb_autoupdate_bios')
        self.cb_bios_live = self.findChild(QCheckBox, 'cb_bios_live')
        self.cb_ded_font = self.findChild(QCheckBox, 'cb_ded_font')

        self.le_dcsdir = self.findChild(QLineEdit, 'le_dcsdir')
        self.le_biosdir = self.findChild(QLineEdit, 'le_biosdir')
        self.le_font_name = self.findChild(QLineEdit, 'le_font_name')
        self.le_bios_live = self.findChild(QLineEdit, 'le_bios_live')

        self.rb_g19 = self.findChild(QRadioButton, 'rb_g19')
        self.rb_g13 = self.findChild(QRadioButton, 'rb_g19')
        self.rb_g15v1 = self.findChild(QRadioButton, 'rb_g19')
        self.rb_g15v2 = self.findChild(QRadioButton, 'rb_g19')
        self.rb_g510 = self.findChild(QRadioButton, 'rb_g19')

        self.hs_large_font = self.findChild(QSlider, 'hs_large_font')
        self.hs_medium_font = self.findChild(QSlider, 'hs_medium_font')
        self.hs_small_font = self.findChild(QSlider, 'hs_small_font')


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
    def run(self):
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
