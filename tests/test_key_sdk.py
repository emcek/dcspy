from pytest import mark

from dcspy.sdk.key_sdk import GkeySdkManager


@mark.parametrize('function, args, result', [
    ('logi_gkey_init', (), False),
    ('logi_gkey_shutdown', (), None),
], ids=['init', 'shutdown'])
def test_all_failure_cases(function, args, result):
    key_sdk = GkeySdkManager(gkey_callback_handler=lambda *args: None)
    key_sdk.KEY_DLL = None
    assert getattr(key_sdk, function)(*args) is result
