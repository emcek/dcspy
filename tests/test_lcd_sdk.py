from unittest.mock import call, patch

from pytest import mark

from dcspy.models import LcdButton, LcdSize, LcdType


@mark.parametrize('function, lcd, args, result', [
    ('logi_lcd_init', LcdType.MONO, ('test', 1), False),
    ('logi_lcd_is_connected', LcdType.MONO, (LcdType.MONO,), False),
    ('logi_lcd_is_button_pressed', LcdType.MONO, (LcdButton.ONE,), False),
    ('logi_lcd_update', LcdType.MONO, (), None),
    ('logi_lcd_shutdown', LcdType.MONO, (), None),
    ('logi_lcd_mono_set_background', LcdType.MONO, ([1, 2, 3],), False),
    ('logi_lcd_mono_set_text', LcdType.MONO, (1, ''), False),
    ('logi_lcd_color_set_background', LcdType.COLOR, ([(1, 2, 3)],), False),
    ('logi_lcd_color_set_title', LcdType.COLOR, ('', (1, 2, 3)), False),
    ('logi_lcd_color_set_text', LcdType.COLOR, (1, '', (1, 2, 3)), False)
], ids=[
    'init',
    'is connected',
    'is button pressed',
    'update',
    'shutdown',
    'mono set background',
    'mono set text',
    'color set background',
    'color_set title',
    'color set text'])
def test_all_failure_cases(function, lcd, args, result):
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    lcd_sdk = LcdSdkManager('test', lcd)
    lcd_sdk.lcd_dll = None
    assert getattr(lcd_sdk, function)(*args) is result


@mark.parametrize('c_func, effect, lcd, size', [
    ('logi_lcd_mono_set_background', [True], LcdType.MONO, (16, 4)),
    ('logi_lcd_color_set_background', [False, True], LcdType.COLOR, (32, 24))
], ids=['Mono', 'Color'])
def test_update_display(c_func, effect, lcd, size):
    from PIL import Image

    from dcspy.sdk.lcd_sdk import LcdSdkManager

    lcd_sdk = LcdSdkManager('test', LcdType.MONO)

    with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=effect) as connected, \
            patch.object(lcd_sdk, c_func, return_value=True) as set_background, \
            patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
        lcd_sdk.update_display(Image.new('1', (size[0], size[1]), 0))
        connected.assert_called_with(lcd)
        set_background.assert_called_once_with([0] * size[0] * size[1])


@mark.parametrize('c_func, effect, lcd, list_txt', [
    ('logi_lcd_mono_set_text', [True], LcdType.MONO, ['1', '2', '3', '4']),
    ('logi_lcd_color_set_text', [False, True], LcdType.COLOR, ['1', '2', '3', '4', '5', '6', '7', '8'])
], ids=['Mono', 'Color'])
def test_update_text(c_func, effect, lcd, list_txt):
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    lcd_sdk = LcdSdkManager('test', LcdType.MONO)

    with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=effect) as connected:
        with patch.object(lcd_sdk, c_func, return_value=True) as set_text:
            with patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
                lcd_sdk.update_text(list_txt)
                connected.assert_called_with(lcd)
                set_text.assert_has_calls([call(i, j) for i, j in enumerate(list_txt)])


@mark.parametrize('c_funcs, effect, lcd, clear, text', [
    (('logi_lcd_mono_set_background', 'logi_lcd_mono_set_text'), [True],
     LcdType.MONO, [0] * LcdSize.MONO_WIDTH.value * LcdSize.MONO_HEIGHT.value,
     [call(0, ''), call(1, ''), call(2, ''), call(3, '')]),
    (('logi_lcd_color_set_background', 'logi_lcd_color_set_text'), [False, True],
     LcdType.COLOR, [(0,) * 4] * LcdSize.COLOR_WIDTH.value * LcdSize.COLOR_HEIGHT.value,
     [call(0, ''), call(1, ''), call(2, ''), call(3, ''), call(4, ''), call(5, ''), call(6, ''), call(7, '')])
], ids=['Mono', 'Color'])
def test_clear_display(c_funcs, effect, lcd, clear, text):
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    lcd_sdk = LcdSdkManager('test', LcdType.MONO)

    with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=effect) as connected, \
            patch.object(lcd_sdk, c_funcs[0], return_value=True) as set_background, \
            patch.object(lcd_sdk, c_funcs[1], return_value=True) as set_text, \
            patch.object(lcd_sdk, 'logi_lcd_update', return_value=True):
        lcd_sdk.clear_display(true_clear=True)
        connected.assert_called_with(lcd)
        set_background.assert_called_once_with(clear)
        set_text.assert_has_calls(text)


def test_update_text_no_lcd():
    from dcspy.sdk.lcd_sdk import LcdSdkManager

    lcd_sdk = LcdSdkManager('test', LcdType.MONO)

    with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=[False, False]) as connected:
        lcd_sdk.update_text(['1'])
        connected.assert_has_calls([call(LcdType.MONO), call(LcdType.COLOR)])


def test_update_display_no_lcd():
    from PIL import Image

    from dcspy.sdk.lcd_sdk import LcdSdkManager

    lcd_sdk = LcdSdkManager('test', LcdType.COLOR)

    with patch.object(lcd_sdk, 'logi_lcd_is_connected', side_effect=[False, False]) as connected:
        lcd_sdk.update_display(Image.new('1', (16, 4), 0))
        connected.assert_has_calls([call(LcdType.MONO), call(LcdType.COLOR)])
