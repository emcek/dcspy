def test_load_dll():
    from dcspy.models import DllSdk
    from dcspy.sdk import load_dll

    test_dll = DllSdk(name='TEST', directory='TEST', header_file='test_header.h')

    assert load_dll(lib_type=test_dll) is None
