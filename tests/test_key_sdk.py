from pytest import mark


@mark.parametrize('function, args, result', [
    ('logi_gkey_init', (), False),
    ('logi_gkey_is_keyboard_gkey_pressed', (1, 1), False),
    ('logi_gkey_is_keyboard_gkey_string', (2, 2), ''),
    ('logi_gkey_shutdown', (), None),
], ids=['init', 'is gkey pressed', 'is gkey string', 'shutdown'])
def test_all_failure_cases(function, args, result):
    from dcspy.sdk.key_sdk import GkeySdkManager

    key_sdk = GkeySdkManager(gkey_callback_handler=lambda *args: None)
    key_sdk.KEY_DLL = None
    assert getattr(key_sdk, function)(*args) is result
