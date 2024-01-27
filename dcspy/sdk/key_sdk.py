from logging import getLogger

from _cffi_backend import Lib
from cffi import FFI

from dcspy.sdk import KeyDll, load_dll

LOG = getLogger(__name__)
KEY_DLL: Lib = load_dll(KeyDll)  # type: ignore[assignment]
ffi = FFI()


def logi_gkey_init() -> bool:
    """
    Make necessary initializations.

    It must be called before your application can see G-key/button events.
    :return: If the function succeeds, it returns True. Otherwise, False.
    """
    try:
        return KEY_DLL.LogiGkeyInit(ffi.NULL)  # type: ignore[attr-defined]
    except AttributeError:
        return False


def logi_gkey_is_keyboard_gkey_pressed(g_key: int, mode: int) -> bool:
    """
    Indicate whether a keyboard G-key is currently being pressed.

    :param g_key: number of the G-key to check (for example between 1 and 29 for G13).
    :param mode: number of the mode currently selected (1, 2 or 3)
    :return: True if the specified G-key for the specified Mode is currently being pressed, False otherwise.
    """
    try:
        return KEY_DLL.LogiGkeyIsKeyboardGkeyPressed(g_key, mode)  # type: ignore[attr-defined]
    except AttributeError:
        return False


def logi_gkey_is_keyboard_gkey_string(g_key: int, mode: int) -> str:
    """
    Return a G-key-specific friendly string.

    :param g_key: number of the G-key to check (for example between 1 and 29 for G13).
    :param mode: number of the mode currently selected (1, 2 or 3)
    :return: Friendly string for specified G-key and Mode number. For example 'G5/M1'.
    """
    try:
        return ffi.string(KEY_DLL.LogiGkeyGetKeyboardGkeyString(g_key, mode))  # type: ignore[attr-defined,return-value]
    except AttributeError:
        return ''


def logi_gkey_shutdown() -> None:
    """Unload the corresponding DLL and frees up any allocated resources."""
    try:
        KEY_DLL.LogiGkeyShutdown()  # type: ignore[attr-defined]
    except AttributeError:
        pass
