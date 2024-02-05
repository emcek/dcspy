from time import sleep

from dcspy.models import LOGI_DEVICETYPE_ALL, LOGI_LED_DURATION_INFINITE
from dcspy.sdk import led_sdk

rgb = 100, 0, 0
duration = 10
interval = 270


def flash():
    led_sdk.logi_led_flash_lighting(rgb, LOGI_LED_DURATION_INFINITE, interval)


def pulse():
    led_sdk.logi_led_pulse_lighting(rgb, LOGI_LED_DURATION_INFINITE, interval)


def stop():
    led_sdk.logi_led_stop_effects()


led_sdk.logi_led_init()
sleep(0.05)
led_sdk.logi_led_set_target_device(LOGI_DEVICETYPE_ALL)
sleep_time = duration + 0.2
# led_sdk.logi_led_flash_lighting(rgb, duration * 1000, interval)
for _ in range(20):
    flash()
    sleep(0.4)
    stop()
# sleep(sleep_time)
led_sdk.logi_led_shutdown()
