from calendar import LocaleHTMLCalendar
from unittest.mock import Mock

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
    from dcspy.sdk import lcd_sdk
    assert lcd_sdk.LCD_DLL is False
    assert type(lcd_sdk.LCD_DLL) == ''
    lcd_sdk.LCD_DLL = False
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
def test_init2(py_func, c_func, args, result):
    from dcspy.sdk import lcd_sdk
    mocked_c_func = Mock()
    mocked_c_func.return_value = result
    lcd_sdk.LCD_DLL = {c_func: mocked_c_func}
    assert getattr(lcd_sdk, py_func)(*args) is result
