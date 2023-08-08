from ctypes import c_void_p, sizeof
from dataclasses import dataclass
from logging import getLogger
from os import environ
from platform import architecture
from sys import maxsize
from typing import Optional

from _cffi_backend import Lib
from cffi import FFI

LOG = getLogger(__name__)


@dataclass
class DllSdk:
    """DLL SDK."""
    name: str
    header: str


lcd_header = '''
bool LogiLcdInit(wchar_t* friendlyName, int lcdType);
bool LogiLcdIsConnected(int lcdType);
bool LogiLcdIsButtonPressed(int button);
void LogiLcdUpdate();
void LogiLcdShutdown();

// Monochrome LCD functions
bool LogiLcdMonoSetBackground(BYTE monoBitmap[]);
bool LogiLcdMonoSetText(int lineNumber, wchar_t* text);

// Color LCD functions
bool LogiLcdColorSetBackground(BYTE colorBitmap[]);
bool LogiLcdColorSetTitle(wchar_t* text, int red, int green, int blue);
bool LogiLcdColorSetText(int lineNumber, wchar_t* text, int red, int green, int blue);
'''
led_header = '''
bool LogiLedInit();
bool LogiLedInitWithName(const char name[]);

bool LogiLedGetSdkVersion(int *majorNum, int *minorNum, int *buildNum);
bool LogiLedGetConfigOptionNumber(const wchar_t *configPath, double *defaultValue);
bool LogiLedGetConfigOptionBool(const wchar_t *configPath, bool *defaultValue);
bool LogiLedGetConfigOptionColor(const wchar_t *configPath, int *defaultRed, int *defaultGreen, int *defaultBlue);
bool LogiLedGetConfigOptionRect(const wchar_t *configPath, int *defaultX, int *defaultY, int *defaultWidth, int *defaultHeight);
bool LogiLedGetConfigOptionString(const wchar_t *configPath, wchar_t *defaultValue, int bufferSize);
bool LogiLedGetConfigOptionKeyInput(const wchar_t *configPath, wchar_t *defaultValue, int bufferSize);
bool LogiLedGetConfigOptionSelect(const wchar_t *configPath, wchar_t *defaultValue, int *valueSize, const wchar_t *values, int bufferSize);
bool LogiLedGetConfigOptionRange(const wchar_t *configPath, int *defaultValue, int min, int max);
bool LogiLedSetConfigOptionLabel(const wchar_t *configPath, wchar_t *label);

//Generic functions => Apply to any device type.
bool LogiLedSetTargetDevice(int targetDevice);
bool LogiLedSaveCurrentLighting();
bool LogiLedSetLighting(int redPercentage, int greenPercentage, int bluePercentage);
bool LogiLedRestoreLighting();
bool LogiLedFlashLighting(int redPercentage, int greenPercentage, int bluePercentage, int milliSecondsDuration, int milliSecondsInterval);
bool LogiLedPulseLighting(int redPercentage, int greenPercentage, int bluePercentage, int milliSecondsDuration, int milliSecondsInterval);
bool LogiLedStopEffects();

//Per-key functions => only apply to LOGI_DEVICETYPE_PERKEY_RGB devices.
bool LogiLedSetLightingFromBitmap(unsigned char bitmap[]);
bool LogiLedSetLightingForKeyWithScanCode(int keyCode, int redPercentage, int greenPercentage, int bluePercentage);
bool LogiLedSetLightingForKeyWithHidCode(int keyCode, int redPercentage, int greenPercentage, int bluePercentage);
bool LogiLedSetLightingForKeyWithQuartzCode(int keyCode, int redPercentage, int greenPercentage, int bluePercentage);
bool LogiLedSetLightingForKeyWithKeyName(LogiLed::KeyName keyName, int redPercentage, int greenPercentage, int bluePercentage);
bool LogiLedSaveLightingForKey(LogiLed::KeyName keyName);
bool LogiLedRestoreLightingForKey(LogiLed::KeyName keyName);
bool LogiLedExcludeKeysFromBitmap(LogiLed::KeyName *keyList, int listCount);

//Per-key effects => only apply to LOGI_DEVICETYPE_PERKEY_RGB devices.
bool LogiLedFlashSingleKey(LogiLed::KeyName keyName, int redPercentage, int greenPercentage, int bluePercentage, int msDuration, int msInterval);
bool LogiLedPulseSingleKey(LogiLed::KeyName keyName, int startRedPercentage, int startGreenPercentage, int startBluePercentage, int finishRedPercentage, int finishGreenPercentage, int finishBluePercentage, int msDuration, bool isInfinite);
bool LogiLedStopEffectsOnKey(LogiLed::KeyName keyName);

//Zonal functions => only apply to devices with zones.
bool LogiLedSetLightingForTargetZone(LogiLed::DeviceType deviceType, int zone, int redPercentage, int greenPercentage, int bluePercentage);

void LogiLedShutdown();
'''
LCD = DllSdk(name='LCD', header=lcd_header)
LED = DllSdk(name='LED', header=led_header)


def _init_dll(lib_type: DllSdk) -> Lib:
    """
    Initialize C dynamic linking library.

    :param lib_type: LCD or LED
    :return: C DLL instance
    """
    arch = 'x64' if all([architecture()[0] == '64bit', maxsize > 2 ** 32, sizeof(c_void_p) > 4]) else 'x86'
    try:
        prog_files = environ['PROGRAMW6432']
    except KeyError:
        prog_files = environ['PROGRAMFILES']
    dll_path = f"{prog_files}\\Logitech Gaming Software\\SDK\\{lib_type.name}\\{arch}\\Logitech{lib_type.name.capitalize()}.dll"
    LOG.debug(f'Selected DLL: {dll_path}')
    ffi = FFI()
    ffi.cdef(lib_type.header)
    dll = ffi.dlopen(dll_path)
    return dll


def load_dll(lib_type: DllSdk) -> Optional[Lib]:
    """
    Initialize and load of C dynamic linking library.

    :param lib_type: library to load: LCD or LED
    :return: C DLL instance
    """
    try:
        dll = _init_dll(lib_type)
        LOG.info(f'Loading of {lib_type.name} SDK success')
        return dll
    except (KeyError, OSError) as err:
        header = '*' * 44
        LOG.error(f'\n{header}\n*{type(err).__name__:^42}*\n{header}\nLoading of {lib_type.name} SDK failed !', exc_info=True)
        LOG.error(f'{header}')
        return None
