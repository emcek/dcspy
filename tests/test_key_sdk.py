from pytest import mark


@mark.parametrize('function, args, result', [
    ('logi_gkey_init', (), False),
    ('logi_gkey_is_keyboard_gkey_pressed', (1, 1), False),
    ('logi_gkey_is_keyboard_gkey_string', (2, 2), ''),
    ('logi_gkey_is_mouse_pressed', (1,), False),
    ('logi_gkey_is_mouse_string', (2,), ''),
    ('logi_gkey_shutdown', (), None),
], ids=['init', 'is gkey pressed', 'is gkey string', 'is mouse pressed', 'is mouse string', 'shutdown'])
def test_all_failure_cases(function, args, result):
    from dcspy.sdk.key_sdk import GkeySdkManager

    def gkey_callback(key_idx: int, mode: int, key_down, mouse: int) -> None:
        print(key_idx, mode, key_down)

    key_sdk = GkeySdkManager(callback=gkey_callback)
    key_sdk.key_dll = None
    assert getattr(key_sdk, function)(*args) is result


def test_user_callback():
    from dcspy.sdk.key_sdk import GkeyCode, GkeySdkManager

    def gkey_callback(key_idx: int, mode: int, key_down, mouse: int) -> None:
        assert key_idx == 2
        assert mode == 3
        assert key_down == 1

    key_sdk = GkeySdkManager(callback=gkey_callback)
    gkey_code = GkeyCode()
    gkey_code.keyIdx = 2
    gkey_code.mState = 3
    gkey_code.keyDown = 1

    key_sdk._callback(gkey_code, 'G2/M3', None)
