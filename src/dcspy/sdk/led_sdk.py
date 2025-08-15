from logging import getLogger

from _cffi_backend import Lib
from cffi import FFI

from dcspy.models import EffectInfo, LedDll, LedEffectType, LedSupport
from dcspy.sdk import load_dll

LOG = getLogger(__name__)


class LedSdkManager:
    """LED SDK manager."""

    def __init__(self, name: str = '', target_dev: LedSupport = LedSupport.LOGI_DEVICETYPE_ALL) -> None:
        """
        Create Led SDK manager.

        :param name: A name of the LED integration
        :param target_device: One or a combination of the following values:
                              LOGI_DEVICETYPE_MONOCHROME, LOGI_DEVICETYPE_RGB, LOGI_DEVICETYPE_ALL
        """
        if name:
            self.led_dll: Lib = load_dll(LedDll)  # type: ignore[assignment]
            result = self.logi_led_init_with_name(name=name)
        else:
            result = self.logi_led_init()
        # todo: maybe sleep needed
        self.logi_led_set_target_device(target_dev)
        LOG.debug(f'LED is turned on: {result}')

    def logi_led_init(self) -> bool:
        """
        Make sure there isn't already another instance running and then makes the necessary initializations.

        It saves the current lighting for all connected and supported devices. This function will also stop any effect
        currently going on the connected devices.
        :return: A result of execution
        """
        try:
            return self.led_dll.LogiLedInit()  # type: ignore[attr-defined]
        except AttributeError:
            return False

    def logi_led_init_with_name(self, name: str) -> bool:
        """
        Make sure there isn't already another instance running and then makes the necessary initializations.

        It saves the current lighting for all connected and supported devices.
        This function will also stop any effect currently going on the connected devices. Passing a name into this
        function will make the integration show up with a given custom name. The name is set only once, the first
        time this function or logi_led_init() is called.
        :param name: The referred name for this integration
        :return: A result of execution
        """
        try:
            return self.led_dll.LogiLedInitWithName(FFI().new('wchar_t[]', name))  # type: ignore[attr-defined]
        except AttributeError:
            return False

    def logi_led_set_target_device(self, target_device: LedSupport) -> bool:
        """
        Set the target device type for future calls.

        The default target device is LOGI_DEVICETYPE_ALL, therefore, if no call is made to LogiLedSetTargetDevice
        the SDK will apply any function to all the connected devices.
        :param target_device: One or a combination of the following values:
                              LOGI_DEVICETYPE_MONOCHROME, LOGI_DEVICETYPE_RGB, LOGI_DEVICETYPE_ALL
        :return: A result of execution
        """
        try:
            return self.led_dll.LogiLedSetTargetDevice(target_device.value)  # type: ignore[attr-defined]
        except AttributeError:
            return False

    def logi_led_save_current_lighting(self) -> bool:
        """
        Save the current lighting so that it can be restored after a temporary effect is finished.

        For example, if flashing a red warning sign for a few seconds, you would call the logi_led_save_current_lighting()
        function just before starting the warning effect.
        :return: A result of execution
        """
        try:
            return self.led_dll.LogiLedSaveCurrentLighting()  # type: ignore[attr-defined]
        except AttributeError:
            return False

    def logi_led_restore_lighting(self) -> bool:
        """
        Restore the last saved lighting.

        It should be called after a temporary effect is finished.
        For example, if flashing a red warning sign for a few seconds, you would call this function right
        after the warning effect is finished.
        :return: A result of execution
        """
        try:
            return self.led_dll.LogiLedRestoreLighting()  # type: ignore[attr-defined]
        except AttributeError:
            return False

    def logi_led_set_lighting(self, rgb: tuple[int, int, int]) -> bool:
        """
        Set the lighting on connected and supported devices.

        Do not call this function immediately after logi_led_init(), instead of wait a little of time after logi_led_init().
        For devices that only support a single color, the highest percentage value given of the three colors will
        define the intensity. For monochrome device, Logitech Gaming Software will proportionally reduce
        the value of the highest color, according to the user hardware brightness setting.

        :param rgb: Tuple with integer range 0 to 100 as an amount of red, green, blue
        :return: A result of execution
        """
        try:
            return self.led_dll.LogiLedSetLighting(*rgb)  # type: ignore[attr-defined]
        except AttributeError:
            return False

    def logi_led_flash_lighting(self, rgb: tuple[int, int, int], duration: int, interval: int) -> bool:
        """
        Save the current lighting, plays the flashing effect on the targeted devices.

        Finally, restores the saved lighting.
        :param rgb: Tuple with integer range 0 to 100 as an amount of red, green, blue
        :param duration: Parameter can be set (in millisecond) to 0 (zero)
                         to make the effect run until stopped with logi_led_stop_effects()
        :param interval: Duration of the flashing interval in millisecond
        :return: A result of execution
        """
        try:
            return self.led_dll.LogiLedFlashLighting(*rgb, duration, interval)  # type: ignore[attr-defined]
        except AttributeError:
            return False

    def logi_led_pulse_lighting(self, rgb: tuple[int, int, int], duration: int, interval: int) -> bool:
        """
        Save the current lighting, plays the pulsing effect on the targeted devices.

        Finally, restores the saved lighting.
        :param rgb: Tuple with integer values range 0 to 100 as an amount of red, green, blue.
        :param duration: Parameter can be set (in millisecond) to 0 (zero)
                         to make the effect run until stopped with logi_led_stop_effects().
        :param interval: Duration of the flashing interval in millisecond.
        :return: A result of execution.
        """
        try:
            return self.led_dll.LogiLedPulseLighting(*rgb, duration, interval)  # type: ignore[attr-defined]
        except AttributeError:
            return False

    def logi_led_stop_effects(self) -> bool:
        """
        Stop any of the preset effect.

        Started from logi_led_flash_lighting() or logi_led_pulse_lighting().
        :return: A result of execution
        """
        try:
            return self.led_dll.LogiLedStopEffects()  # type: ignore[attr-defined]
        except AttributeError:
            return False

    def logi_led_shutdown(self) -> None:
        """Restore the last saved lighting and frees memory used by the SDK."""
        try:
            self.led_dll.LogiLedShutdown()  # type: ignore[attr-defined]
        except AttributeError:
            pass

    def start_led_effect(self, effect: EffectInfo) -> bool:
        """
        Start the pulsing red effect in the thread on the keyboard.

        :param effect: Led effect info object containing RGB, duration, and interval.
        """
        result = False
        if effect.type == LedEffectType.PULSE:
            result = self.logi_led_pulse_lighting(rgb=effect.rgb, duration=effect.duration, interval=effect.interval)
        elif effect.type == LedEffectType.FLASH:
            result = self.logi_led_flash_lighting(rgb=effect.rgb, duration=effect.duration, interval=effect.interval)
        return result
