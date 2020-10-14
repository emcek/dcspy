from unittest.mock import Mock, patch, call
from pytest import mark


@mark.parametrize('function, args, result', [('logi_lcd_init', ('test', 1), False),
                                             ('logi_lcd_is_connected', (1,), False),
                                             ('logi_lcd_is_button_pressed', (1,), False),
                                             ('logi_lcd_update', (), None),
                                             ('logi_lcd_shutdown', (), None),
                                             ('logi_lcd_mono_set_background', ([1, 2, 3],), False),
                                             ('logi_lcd_mono_set_text', (1, ''), False),
                                             ('logi_lcd_color_set_background', ([1, 2, 3],), False),
                                             ('logi_lcd_color_set_title', ('', (1, 2, 3)), False),
                                             ('logi_lcd_color_set_text', (1, '', (1, 2, 3)), False)])
def test_all_failure_cases(function, args, result):
    from dcspy import lcd_sdk
    lcd_sdk.LCD_DLL = None
    assert getattr(lcd_sdk, function)(*args) is result


@mark.parametrize('py_func, c_func, args, result', [('logi_lcd_init', 'LogiLcdInit', ('test', 1), True),
                                                    ('logi_lcd_is_connected', 'LogiLcdIsConnected', (1,), True),
                                                    ('logi_lcd_is_button_pressed', 'LogiLcdIsButtonPressed', (1,), True),
                                                    ('logi_lcd_update', 'LogiLcdUpdate', (), None),
                                                    ('logi_lcd_shutdown', 'LogiLcdShutdown', (), None),
                                                    ('logi_lcd_mono_set_background', 'LogiLcdMonoSetBackground', ([1, 2, 3],), True),
                                                    ('logi_lcd_mono_set_text', 'LogiLcdMonoSetText', (1, ''), True),
                                                    ('logi_lcd_color_set_background', 'LogiLcdColorSetBackground', ([1, 2, 3],), True),
                                                    ('logi_lcd_color_set_title', 'LogiLcdColorSetTitle', ('', (1, 2, 3)), True),
                                                    ('logi_lcd_color_set_text', 'LogiLcdColorSetText', (1, '', (1, 2, 3)), True)])
def test_all_success_cases(py_func, c_func, args, result):
    from dcspy import lcd_sdk
    mocked_c_func = Mock()
    mocked_c_func.return_value = result
    lcd_sdk.LCD_DLL = {c_func: mocked_c_func}
    assert getattr(lcd_sdk, py_func)(*args) is result


@mark.parametrize('c_funcs, effect, args', [(('logi_lcd_mono_set_background', 'logi_lcd_mono_set_text'),
                                             [True],
                                             (1, 160 * 43, [call(0, ''), call(1, ''), call(2, ''), call(3, '')])),
                                            (('logi_lcd_color_set_background', 'logi_lcd_color_set_text'),
                                             [False, True],
                                             (2, 320 * 240, [call(0, ''), call(1, ''), call(2, ''), call(3, ''),
                                                             call(4, ''), call(5, ''), call(6, ''), call(7, '')]))])
def test_clear_display(c_funcs, effect, args):
    from dcspy import lcd_sdk
    with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=effect) as connected:
        with patch.object(lcd_sdk, c_funcs[0], return_value=True) as set_background:
            with patch.object(lcd_sdk, c_funcs[1], return_value=True) as set_text:
                with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                    lcd_sdk.clear_display(true_clear=True)
                    connected.assert_called_with(args[0])
                    set_background.assert_called_once_with([0] * args[1])
                    set_text.assert_has_calls(args[2])
