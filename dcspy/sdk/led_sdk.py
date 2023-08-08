from logging import getLogger
from threading import Event
from time import sleep
from typing import Tuple
from cffi import FFI
from dcspy.sdk import load_dll, LED

LOG = getLogger(__name__)

LOGI_LED_DURATION_INFINITE = 0
LOGI_DEVICETYPE_MONOCHROME = 1
LOGI_DEVICETYPE_RGB = 2
LOGI_DEVICETYPE_ALL = LOGI_DEVICETYPE_MONOCHROME | LOGI_DEVICETYPE_RGB

LED_DLL = load_dll(LED)


def logi_led_init() -> bool:
    """
    Make sure there isn't already another instance running and then makes necessary initializations.

    It saves the current lighting for all connected and supported devices. This function will also stop any effect
    currently going on the connected devices.
    :return: result
    """
    if LED_DLL:
        ret = LED_DLL.LogiLedInit()
        return ret
    return False


def logi_led_init_with_name(name: str) -> bool:
    """
    Make sure there isn't already another instance running and then makes necessary initializations.

    It saves the current lighting for all connected and supported devices.
    This function will also stop any effect currently going on the connected devices. Passing a name into this
    function will make the integration show up with a given custom name. The name is set only once, the first
    time this function or logi_led_init() is called.
    :param name: The referred name for this integration to show u as
    :return: result
    """
    if LED_DLL:
        ffi = FFI()
        ret = LED_DLL.LogiLedInitWithName(ffi.new('wchar_t[]', name))
        return ret
    return False


def logi_led_set_target_device(target_device: int) -> bool:
    """
    Set the target device type for future calls.

    The default target device is LOGI_DEVICETYPE_ALL, therefore, if no call is made to LogiLedSetTargetDevice
    the SDK will apply any function to all the connected devices.
    :param target_device: one or a combination of the following values:
                          LOGI_DEVICETYPE_MONOCHROME, LOGI_DEVICETYPE_RGB, LOGI_DEVICETYPE_ALL
    :return: result
    """
    if LED_DLL:
        ret = LED_DLL.LogiLedSetTargetDevice(target_device)
        return ret
    return False


def logi_led_save_current_lighting() -> bool:
    """
    Save the current lighting so that it can be restored after a temporary effect is finished.

    For example if flashing a red warning sign for a few seconds, you would call the logi_led_save_current_lighting()
    function just before starting the warning effect.
    :return: result
    """
    if LED_DLL:
        ret = LED_DLL.LogiLedSaveCurrentLighting()
        return ret
    return False


def logi_led_restore_lighting() -> bool:
    """
    Restore the last saved lighting.

    It should be called after a temporary effect is finished.
    For example if flashing a red warning sign for a few seconds, you would call this function right
    after the warning effect is finished.
    :return: result
    """
    if LED_DLL:
        ret = LED_DLL.LogiLedRestoreLighting()
        return ret
    return False


def logi_led_set_lighting(rgb: Tuple[int, int, int]) -> bool:
    """
    Set the lighting on connected and supported devices.

    Do not call this function immediately after logi_led_init(). Instead of leave a little of time after logi_led_init().
    For devices that only support a single color, the highest percentage value given of the three colors will
    define the intensity. For monochrome device, Logitech Gaming Software will reduce
    proportionally the value of the highest color, according to the user hardware brightness setting.

    :param rgb: tuple with integer values range 0 to 100 as amount of red, green, blue
    :return: result
    """
    if LED_DLL:
        ret = LED_DLL.LogiLedSetLighting(*rgb)
        return ret
    return False


def logi_led_flash_lighting(rgb: Tuple[int, int, int], duration: int, interval: int) -> bool:
    """
    Save the current lighting, plays the flashing effect on the targeted devices.

    Finally, restores the saved lighting.
    :param rgb: tuple with integer values range 0 to 100 as amount of red, green, blue
    :param duration: duration of the effect in milliseconds this parameter can be set to LOGI_LED_DURATION_INFINITE
                     to make the effect run until sto ed through logi_led_stop_effects()
    :param interval: duration of the flashing interval in milliseconds
    :return: result
    """
    if LED_DLL:
        ret = LED_DLL.LogiLedFlashLighting(*rgb, duration, interval)
        return ret
    return False


def logi_led_pulse_lighting(rgb: Tuple[int, int, int], duration: int, interval: int) -> bool:
    """
    Save the current lighting, plays the pulsing effect on the targeted devices.

    Finally, restores the saved lighting.
    :param rgb: tuple with integer values range 0 to 100 as amount of red, green, blue
    :param duration: duration of the effect in milliseconds this parameter can be set to LOGI_LED_DURATION_INFINITE
                     to make the effect run until sto ed through logi_led_stop_effects()
    :param interval: duration of the flashing interval in milliseconds
    :return: result
    """
    if LED_DLL:
        ret = LED_DLL.LogiLedPulseLighting(*rgb, duration, interval)
        return ret
    return False


def logi_led_stop_effects() -> bool:
    """
    Stop any of the presets effects.

    Started from logi_led_flash_lighting() or logi_led_pulse_lighting().
    :return: result
    """
    if LED_DLL:
        ret = LED_DLL.LogiLedStopEffects()
        return ret
    return False


def logi_led_shutdown() -> None:
    """Restore the last saved lighting and frees memory used by the SDK."""
    if LED_DLL:
        LED_DLL.LogiLedShutdown()


def start_led_pulse(rgb: Tuple[int, int, int], duration: int, interval: int, event: Event) -> None:
    """
    Start the pulsing red effect in thread on the keyboard.

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
