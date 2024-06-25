from ctypes import CDLL, CFUNCTYPE, POINTER, Structure, c_bool, c_uint, c_void_p, c_wchar_p, pointer
from logging import getLogger
from typing import Callable, ClassVar, Optional

from dcspy.sdk import KeyDll, load_dll

LOG = getLogger(__name__)


class GkeyCode(Structure):
    """Represent a structure that defines the layout of G key codes."""
    _fields_: ClassVar = [
        ('keyIdx', c_uint, 8),
        ('keyDown', c_uint, 1),
        ('mState', c_uint, 2),
        ('mouse', c_uint, 1),
        ('reserved1', c_uint, 4),
        ('reserved2', c_uint, 16)
    ]


GKEY_CALLBACK = CFUNCTYPE(None, GkeyCode, c_wchar_p, c_void_p)


class LogiGkeyCBContext(Structure):
    """A class representing the Logitech G-Key Callback Context."""
    _fields_: ClassVar = [
        ('gkeyCallBack', GKEY_CALLBACK),
        ('gkeyContext', c_void_p)
    ]


class GkeySdkManager:
    """G-key SDK manager."""
    def __init__(self, callback: Callable[[int, int, int, int], None]) -> None:
        """
        Create G-key SDK manager.

        :param callback: callback handler
        """
        self.key_dll: CDLL = load_dll(KeyDll)  # type: ignore[assignment]
        self.gkey_context = LogiGkeyCBContext()
        self.user_callback = callback
        self.gkey_context.gkeyCallBack = GKEY_CALLBACK(self.callback)
        self.gkey_context.gkeyContext = c_void_p()
        self.gkey_context_ptr = pointer(self.gkey_context)

    def callback(self, g_key_code: GkeyCode, gkey_or_button_str: str, context: Optional[int] = None) -> None:
        """
        Receive callback events for G-key button pushes.

        This function is called whenever a G-key event occurs.
        This then calls the callback handler provided by the user.

        :param g_key_code: The gkey code object representing the current gkey event.
        :param gkey_or_button_str: The string representation of the gkey or button being pressed.
        :param context: The context in which the gkey event occurred.
        """
        LOG.debug(f'Gkey callback: gkey {gkey_or_button_str}, key code: {g_key_code} {context=}')
        self.user_callback(g_key_code.keyIdx, g_key_code.mState, g_key_code.keyDown, g_key_code.mouse)

    def logi_gkey_init(self) -> bool:
        """
        Make the necessary initializations.

        It must be called before your application can see G-key/button events.
        :return: If the function succeeds, it returns True. Otherwise, False.
        """
        try:
            self.key_dll.LogiGkeyInit.restype = c_bool
            self.key_dll.LogiGkeyInit.argtypes = [POINTER(LogiGkeyCBContext)]

            return self.key_dll.LogiGkeyInit(self.gkey_context_ptr)
        except AttributeError:
            return False

    def logi_gkey_shutdown(self) -> None:
        """Unload the corresponding DLL and frees up any allocated resources."""
        try:
            self.key_dll.LogiGkeyShutdown()
        except AttributeError:
            pass

    def logi_gkey_is_keyboard_gkey_pressed(self, g_key: int, mode: int) -> bool:
        """
        Indicate whether a keyboard G-key is currently being pressed.

        :param g_key: Number of the G-key to check, example between 1 and 29 for G13
        :param mode: Number of the mode currently selected, example 1, 2 or 3
        :return: True if the specified G-key for the specified Mode is currently being pressed, False otherwise
        """
        try:
            return self.key_dll.LogiGkeyIsKeyboardGkeyPressed(g_key, mode)
        except AttributeError:
            return False

    def logi_gkey_is_keyboard_gkey_string(self, g_key: int, mode: int) -> str:
        """
        Return a G-key-specific friendly string.

        :param g_key: Number of the G-key to check, example between 1 and 29 for G13
        :param mode: Number of the mode currently selected (1, 2 or 3)
        :return: Friendly string for specified G-key and Mode number, example 'G5/M1'
        """
        try:
            return self.key_dll.LogiGkeyGetKeyboardGkeyString(g_key, mode)
        except AttributeError:
            return ''

    def logi_gkey_is_mouse_pressed(self, button_number: int) -> bool:
        """
        Indicate whether a mouse button is currently being pressed.

        :param button_number: Number of the button to check, example between 6 and 20 for G600
        :return: True if the specified button is currently being pressed, False otherwise
        """
        try:
            return self.key_dll.LogiGkeyIsMousePressed(button_number)
        except AttributeError:
            return False

    def logi_gkey_is_mouse_string(self, button_number: int) -> str:
        """
        Return a button-specific friendly string.

        :param button_number: Number of the button to check, example between 6 and 20 for G600
        :return: Friendly string for specified button number, example 'Mouse Btn 8'
        """
        try:
            return self.key_dll.LogiGkeyGetMouseString(button_number)
        except AttributeError:
            return ''
