from ctypes import CDLL, CFUNCTYPE, POINTER, Structure, c_bool, c_uint, c_void_p, c_wchar_p, pointer
from logging import getLogger
from typing import ClassVar

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


CALLBACK = CFUNCTYPE(None, GkeyCode, c_wchar_p, c_void_p)


class LogiGkeyCBContext(Structure):
    """A class representing the Logitech G-Key Callback Context."""
    _fields_: ClassVar = [
        ('gkeyCallBack', CALLBACK),
        ('gkeyContext', c_void_p)
    ]


class GkeySdkManager:
    """G-key SDK manager."""
    def __init__(self, gkey_callback_handler) -> None:
        """
        Create G-key SDK manager.

        :param gkey_callback_handler: callback handler
        """
        self.gkey_callback_handler = gkey_callback_handler
        self.KEY_DLL: CDLL = load_dll(KeyDll)  # type: ignore[assignment]
        self.gkey_context = LogiGkeyCBContext()
        self.gkey_context.gkeyCallBack = CALLBACK(self.callback)
        self.gkey_context.gkeyContext = c_void_p()
        self.gkey_context_ptr = pointer(self.gkey_context)

    def logi_gkey_init(self) -> bool:
        """
        Make necessary initializations.

        It must be called before your application can see G-key/button events.
        :return: If the function succeeds, it returns True. Otherwise, False.
        """
        try:
            LOG.info('Initialising Logitech Gkey SDK...')
            self.KEY_DLL.LogiGkeyInit.restype = c_bool
            self.KEY_DLL.LogiGkeyInit.argtypes = [POINTER(LogiGkeyCBContext)]

            return self.KEY_DLL.LogiGkeyInit(self.gkey_context_ptr)
        except AttributeError:
            return False

    def logi_gkey_shutdown(self) -> None:
        """Unload the corresponding DLL and frees up any allocated resources."""
        try:
            self.KEY_DLL.LogiGkeyShutdown()
        except AttributeError:
            pass

    def logi_gkey_is_keyboard_gkey_pressed(self, g_key: int, mode: int) -> bool:
        """
        Indicate whether a keyboard G-key is currently being pressed.

        :param g_key: number of the G-key to check (for example between 1 and 29 for G13).
        :param mode: number of the mode currently selected (1, 2 or 3)
        :return: True if the specified G-key for the specified Mode is currently being pressed, False otherwise.
        """
        try:
            return self.KEY_DLL.LogiGkeyIsKeyboardGkeyPressed(g_key, mode)
        except AttributeError:
            return False

    def logi_gkey_is_keyboard_gkey_string(self, g_key: int, mode: int) -> str:
        """
        Return a G-key-specific friendly string.

        :param g_key: number of the G-key to check (for example between 1 and 29 for G13).
        :param mode: number of the mode currently selected (1, 2 or 3)
        :return: Friendly string for specified G-key and Mode number. For example 'G5/M1'.
        """
        try:
            return self.KEY_DLL.LogiGkeyGetKeyboardGkeyString(g_key, mode)
        except AttributeError:
            return ''
