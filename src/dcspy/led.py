from time import sleep

from dcspy.models import LedConstants
from dcspy.sdk import led_sdk

rgb = 100, 0, 0
duration = 10
interval = 270


def flash():
    """Flash the LED with the specified RGB color, duration, and interval."""
    led_sdk.logi_led_flash_lighting(rgb, LedConstants.LOGI_LED_DURATION_INFINITE.value, interval)


def pulse():
    """Pulse the LED with the specified RGB color, duration, and interval."""
    led_sdk.logi_led_pulse_lighting(rgb, LedConstants.LOGI_LED_DURATION_INFINITE.value, interval)


def stop():
    """Stop any of the preset effect."""
    led_sdk.logi_led_stop_effects()


led_sdk.logi_led_init()
sleep(0.05)
led_sdk.logi_led_set_target_device(LedConstants.LOGI_DEVICETYPE_ALL)
sleep_time = duration + 0.2
# led_sdk.logi_led_flash_lighting(rgb, duration * 1000, interval)
for _ in range(20):
    flash()
    sleep(0.4)
    stop()
# sleep(sleep_time)
led_sdk.logi_led_shutdown()
