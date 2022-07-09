from unittest.mock import Mock, patch

from pytest import mark


@mark.parametrize('function, args, result', [('logi_led_init', (), False),
                                             ('logi_led_init_with_name', ('name',), False),
                                             ('logi_led_set_target_device', (1,), False),
                                             ('logi_led_save_current_lighting', (), False),
                                             ('logi_led_restore_lighting', (), False),
                                             ('logi_led_set_lighting', ((1, 2, 3),), False),
                                             ('logi_led_flash_lighting', ((1, 2, 3), 1, 1), False),
                                             ('logi_led_pulse_lighting', ((1, 2, 3), 1, 1), False),
                                             ('logi_led_stop_effects', (), False),
                                             ('logi_led_shutdown', (), None)])
def test_all_failure_cases(function, args, result):
    from dcspy.sdk import led_sdk
    led_sdk.LED_DLL = None
    assert getattr(led_sdk, function)(*args) is result


@mark.parametrize('py_func, c_func, args, result', [('logi_led_init', 'LogiLedInit', (), True),
                                                    ('logi_led_init_with_name', 'LogiLedInitWithName', ('name',), True),
                                                    ('logi_led_set_target_device', 'LogiLedSetTargetDevice', (1,), True),
                                                    ('logi_led_save_current_lighting', 'LogiLedSaveCurrentLighting', (), True),
                                                    ('logi_led_restore_lighting', 'LogiLedRestoreLighting', (), True),
                                                    ('logi_led_set_lighting', 'LogiLedSetLighting', ((1, 2, 3),), True),
                                                    ('logi_led_flash_lighting', 'LogiLedFlashLighting', ((1, 2, 3), 1, 1), True),
                                                    ('logi_led_pulse_lighting', 'LogiLedPulseLighting', ((1, 2, 3), 1, 1), True),
                                                    ('logi_led_stop_effects', 'LogiLedStopEffects', (), True),
                                                    ('logi_led_shutdown', 'LogiLedShutdown', (), None)])
def test_all_success_cases(py_func, c_func, args, result):
    from dcspy.sdk import led_sdk
    mocked_c_func = Mock()
    mocked_c_func.return_value = result
    led_sdk.LED_DLL = {c_func: mocked_c_func}
    assert getattr(led_sdk, py_func)(*args) is result


def test_start_led_pulse():
    from dcspy.sdk import led_sdk
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from time import sleep

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
