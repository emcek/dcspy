from unittest.mock import patch

from pytest import mark


@mark.parametrize('function, args, result', [
    ('logi_led_init', (), False),
    ('logi_led_init_with_name', ('name',), False),
    ('logi_led_set_target_device', (1,), False),
    ('logi_led_save_current_lighting', (), False),
    ('logi_led_restore_lighting', (), False),
    ('logi_led_set_lighting', ((1, 2, 3),), False),
    ('logi_led_flash_lighting', ((1, 2, 3), 1, 1), False),
    ('logi_led_pulse_lighting', ((1, 2, 3), 1, 1), False),
    ('logi_led_stop_effects', (), False),
    ('logi_led_shutdown', (), None)
], ids=[
    'init',
    'init with name',
    'set target device',
    'save current lighting',
    'restore lighting',
    'set lighting',
    'flash lighting',
    'pulse lighting',
    'stop effects',
    'shutdown',
])
def test_all_failure_cases(function, args, result):
    from dcspy.sdk import led_sdk
    led_sdk.LED_DLL = None
    assert getattr(led_sdk, function)(*args) is result


@mark.slow
def test_start_led_pulse():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from time import sleep

    from dcspy.sdk import led_sdk

    rgb = (100, 0, 0)
    duration = 1
    interval = 1
    event = Event()

    def pulse_led(_rgb, _duration, _interval, _event):
        with patch.object(led_sdk, 'logi_led_init', return_value=True) as logi_led_init, \
                patch.object(led_sdk, 'logi_led_set_target_device', return_value=True) as logi_led_set_target_device, \
                patch.object(led_sdk, 'logi_led_pulse_lighting', return_value=True) as logi_led_pulse_lighting, \
                patch.object(led_sdk, 'logi_led_shutdown', return_value=True) as logi_led_shutdown:
            led_sdk.start_led_pulse(_rgb, _duration, _interval, _event)
            logi_led_init.assert_called_once()
            logi_led_set_target_device.assert_called_once_with(3)
            logi_led_pulse_lighting.assert_called_once_with(_rgb, _duration, _interval)
            logi_led_shutdown.assert_called_once()
        return True

    with ThreadPoolExecutor() as executor:
        future = executor.submit(pulse_led, rgb, duration, interval, event)
        sleep(1.3)
        event.set()
        assert future.result()
