def test_load_dll_wrong_header():
    from dcspy.models import DllSdk
    from dcspy.sdk import load_dll

    test_dll = DllSdk(name='TEST', directory='TEST', header_file='test_header.h')

    assert load_dll(lib_type=test_dll) is None


def test_load_dll_no_ddl_to_load():
    from dcspy.models import DllSdk
    from dcspy.sdk import load_dll

    test_dll = DllSdk(name='Gkey', directory='TEST', header_file='LogitechGkeyLib.h')

    assert load_dll(lib_type=test_dll) is None
