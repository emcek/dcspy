from unittest.mock import patch

from pytest import mark

from dcspy.models import EffectInfo, LedEffectType, LedSupport


@mark.parametrize('function, args, result', [
    ('logi_led_init', (), False),
    ('logi_led_init_with_name', ('name',), False),
    ('logi_led_set_target_device', (LedSupport.LOGI_DEVICETYPE_MONOCHROME,), False),
    ('logi_led_save_current_lighting', (), False),
    ('logi_led_restore_lighting', (), False),
    ('logi_led_set_lighting', ((1, 2, 3),), False),
    ('logi_led_flash_lighting', ((1, 2, 3), 1, 1), False),
    ('logi_led_pulse_lighting', ((1, 2, 3), 1, 1), False),
    ('logi_led_stop_effects', (), False),
    ('logi_led_shutdown', (), None),
], ids=['init', 'init with name', 'set target device', 'save current lighting', 'restore lighting',
        'set lighting', 'flash lighting', 'pulse lighting', 'stop effects', 'shutdown',
])
def test_all_failure_cases(function, args, result):
    from dcspy.sdk.led_sdk import LedSdkManager

    led_sdk = LedSdkManager('test')
    led_sdk.led_dll = None
    assert getattr(led_sdk, function)(*args) is result


def test_start_led_effect_pulse():
    from dcspy.sdk.led_sdk import LedSdkManager

    led_sdk = LedSdkManager('test')
    effect, rgb, duration, interval = LedEffectType.PULSE, (100, 0, 0), 1, 1

    with patch.object(led_sdk, 'logi_led_pulse_lighting', return_value=True) as logi_led_pulse_lighting:
        led_sdk.start_led_effect(effect=EffectInfo(type=effect, rgb=rgb, duration=duration, interval=interval))
        logi_led_pulse_lighting.assert_called_once_with(rgb=rgb, duration=duration, interval=interval)

def test_start_led_effect_flash():
    from dcspy.sdk.led_sdk import LedSdkManager

    led_sdk = LedSdkManager('test')
    effect, rgb, duration, interval = LedEffectType.FLASH, (0, 0, 100), 2, 2
    with patch.object(led_sdk, 'logi_led_flash_lighting', return_value=True) as logi_led_flash_lighting:
        led_sdk.start_led_effect(effect=EffectInfo(type=effect, rgb=rgb, duration=duration, interval=interval))
        logi_led_flash_lighting.assert_called_once_with(rgb=rgb, duration=duration, interval=interval)
