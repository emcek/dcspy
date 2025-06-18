def test_load_dll():
    from dcspy.sdk import DllSdk, load_dll

    test_dll = DllSdk(name='TEST', dir='TEST', header='test_header')

    assert load_dll(test_dll) is None
