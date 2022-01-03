from ctypes import c_bool, c_wchar_p, c_int
from logging import getLogger
from threading import Event
from time import sleep
from typing import Tuple

from dcspy.sdk import load_dll

LOG = getLogger(__name__)

LOGI_LED_DURATION_INFINITE = 0
LOGI_DEVICETYPE_MONOCHROME = 1
LOGI_DEVICETYPE_RGB = 2
LOGI_DEVICETYPE_ALL = LOGI_DEVICETYPE_MONOCHROME | LOGI_DEVICETYPE_RGB

LED_DLL = load_dll('LED')


def logi_led_init() -> bool:
    """
    The function makes sure there isn't already another instance running and then makes necessary initializations.

    It saves the current lighting for all connected and supported devices. This function will also stop any effect
    currently going on the connected devices.
    :return: result
    """
    if LED_DLL:
        logiledinit = LED_DLL['LogiLedInit']
        logiledinit.restype = c_bool
        return logiledinit()
    return False


def logi_led_init_with_name(name: str) -> bool:
    """
    The function makes sure there isn't already another instance running and then makes necessary initializations.

    It saves the current lighting for all connected and supported devices.
    This function will also stop any effect currently going on the connected devices. Passing a name into this
    function will make the integration show up with a given custom name. The name is set only once, the first
    time this function or logi_led_init() is called.
    :param name: The referred name for this integration to show u as
    :return: result
    """
    if LED_DLL:
        logiledinitwithname = LED_DLL['LogiLedInitWithName']
        logiledinitwithname.restype = c_bool
        logiledinitwithname.argtypes = (c_wchar_p,)
        return logiledinitwithname(name)
    return False


def logi_led_set_target_device(target_device: int) -> bool:
    """
    The function sets the target device type for future calls.

    The default target device is LOGI_DEVICETYPE_ALL, therefore, if no call is made to LogiLedSetTargetDevice
    the SDK will apply any function to all the connected devices.
    :param target_device: one or a combination of the following values:
                          LOGI_DEVICETYPE_MONOCHROME, LOGI_DEVICETYPE_RGB, LOGI_DEVICETYPE_ALL
    :return: result
    """
    if LED_DLL:
        logiledsettargetdevice = LED_DLL['LogiLedSetTargetDevice']
        logiledsettargetdevice.restype = c_bool
        logiledsettargetdevice.argtypes = (c_int,)
        return logiledsettargetdevice(target_device)
    return False


def logi_led_save_current_lighting() -> bool:
    """
    The function saves the current lighting so that it can be restored after a temporary effect is finished.

    For example if flashing a red warning sign for a few seconds, you would call the logi_led_save_current_lighting()
    function just before starting the warning effect.
    :return: result
    """
    if LED_DLL:
        logiledsavecurrentlighting = LED_DLL['LogiLedSaveCurrentLighting']
        logiledsavecurrentlighting.restype = c_bool
        return logiledsavecurrentlighting()
    return False


def logi_led_restore_lighting() -> bool:
    """
    The function restores the last saved lighting.

    It should be called after a temporary effect is finished.
    For example if flashing a red warning sign for a few seconds, you would call this function right
    after the warning effect is finished.
    :return: result
    """
    if LED_DLL:
        logiledrestorecurrentlighting = LED_DLL['LogiLedRestoreLighting']
        logiledrestorecurrentlighting.restype = c_bool
        return logiledrestorecurrentlighting()
    return False


def logi_led_set_lighting(rgb: Tuple[int, int, int]) -> bool:
    """
    The function sets the lighting on connected and supported devices.

    Do not call this function immediately after logi_led_init(). Instead of leave a little of time after logi_led_init().
    For devices that only support a single color, the highest percentage value given of the three colors will
    define the intensity. For monochrome device, Logitech Gaming Software will reduce
    proportionally the value of the highest color, according to the user hardware brightness setting.

    :param rgb: tuple with integer values range 0 to 100 as amount of red, green, blue
    :return: result
    """
    if LED_DLL:
        logiledsetlighting = LED_DLL['LogiLedSetLighting']
        logiledsetlighting.restype = c_bool
        logiledsetlighting.argtypes = (c_int, c_int, c_int)
        return logiledsetlighting(*rgb)
    return False


def logi_led_flash_lighting(rgb: Tuple[int, int, int], duration: int, interval: int) -> bool:
    """
    The function saves the current lighting, plays the flashing effect on the targeted devices.

    Finally, restores the saved lighting.
    :param rgb: tuple with integer values range 0 to 100 as amount of red, green, blue
    :param duration: duration of the effect in milliseconds this parameter can be set to LOGI_LED_DURATION_INFINITE
                     to make the effect run until sto ed through logi_led_stop_effects()
    :param interval: duration of the flashing interval in milliseconds
    :return: result
    """
    if LED_DLL:
        logiledflashlighting = LED_DLL['LogiLedFlashLighting']
        logiledflashlighting.restype = c_bool
        logiledflashlighting.argtypes = (c_int, c_int, c_int, c_int, c_int)
        return logiledflashlighting(*rgb, duration, interval)
    return False


def logi_led_pulse_lighting(rgb: Tuple[int, int, int], duration: int, interval: int) -> bool:
    """
    The function saves the current lighting, plays the pulsing effect on the targeted devices.

    Finally, restores the saved lighting.
    :param rgb: tuple with integer values range 0 to 100 as amount of red, green, blue
    :param duration: duration of the effect in milliseconds this parameter can be set to LOGI_LED_DURATION_INFINITE
                     to make the effect run until sto ed through logi_led_stop_effects()
    :param interval: duration of the flashing interval in milliseconds
    :return: result
    """
    if LED_DLL:
        logiledpulselighting = LED_DLL['LogiLedPulseLighting']
        logiledpulselighting.restype = c_bool
        logiledpulselighting.argtypes = (c_int, c_int, c_int, c_int, c_int)
        return logiledpulselighting(*rgb, duration, interval)
    return False


def logi_led_stop_effects() -> bool:
    """
    The function stops any of the presets effects.

    Started from logi_led_flash_lighting() or logi_led_pulse_lighting().
    :return: result
    """
    if LED_DLL:
        logiledstopeffects = LED_DLL['LogiLedStopEffects']
        logiledstopeffects.restype = c_bool
        return logiledstopeffects()
    return False


def logi_led_shutdown() -> None:
    """The function restores the last saved lighting and frees memory used by the SDK."""
    if LED_DLL:
        logiledshutdown = LED_DLL['LogiLedShutdown']
        logiledshutdown.restype = c_bool
        logiledshutdown()


def start_led_pulse(rgb: Tuple[int, int, int], duration: int, interval: int, event: Event):
    """
    The function start the pulsing red effect in thread on the keyboard.

    :param rgb: tuple with integer values range 0 to 100 as amount of red, green, blue
    :param duration: duration of the effect in milliseconds this parameter can be set to 0 (zero)
                     to make the effect run until event is set
    :param interval: duration of the flashing interval in milliseconds
    :param event: stop event for infinite loop
    """
    LOG.debug('Start LED thread')
    logi_led_init()
    sleep(0.05)
    logi_led_set_target_device(LOGI_DEVICETYPE_ALL)
    sleep_time = duration + 0.2
    logi_led_pulse_lighting(rgb, duration, interval)
    sleep(sleep_time)
    while not event.is_set():
        sleep(0.2)
    logi_led_shutdown()
    LOG.debug('Stop LED thread')
