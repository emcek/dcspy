from logging import getLogger
from time import sleep

from _cffi_backend import Lib
from cffi import FFI

from dcspy import LOGITECH_MAX_GKEYS, LOGITECH_MAX_M_STATES
from dcspy.sdk import KeyDll, load_dll

LOG = getLogger(__name__)
KEY_DLL: Lib = load_dll(KeyDll)
ffi = FFI()


def logi_gkey_init() -> bool:
    """
    Make necessary initializations.

    It must be called before your application can see G-key/button events.
    :return: If the function succeeds, it returns True. Otherwise False.
    """
    try:
        return KEY_DLL.LogiGkeyInit(ffi.NULL)
    except AttributeError:
        return False


def logi_gkey_is_keyboard_gkey_pressed(g_key: int, mode: int) -> bool:
    """
    Indicates whether a keyboard G-key is currently being pressed.

    :param g_key: number of the G-key to check (for example between 1 and 29 for G13).
    :param mode: number of the mode currently selected (1, 2 or 3)
    :return: True if the specified G-key for the specified Mode is currently being pressed, False otherwise.
    """
    try:
        return KEY_DLL.LogiGkeyIsKeyboardGkeyPressed(g_key, mode)
    except AttributeError:
        return False


def logi_gkey_is_keyboard_gkey_string(g_key: int, mode: int) -> str:
    """
    Returns a G-key-specific friendly string

    :param g_key: number of the G-key to check (for example between 1 and 29 for G13).
    :param mode: number of the mode currently selected (1, 2 or 3)
    :return: Friendly string for specified G-key and Mode number. For example 'G5/M1'.
    """
    try:
        return ffi.string(KEY_DLL.LogiGkeyGetKeyboardGkeyString(g_key, mode))
    except AttributeError:
        return ''


def logi_gkey_shutdown() -> None:
    """Unloads the corresponding DLL and frees up any allocated resources."""
    try:
        KEY_DLL.LogiGkeyShutdown()
    except AttributeError:
        pass


def check_button_pressed():
    logi_gkey_init()
    try:
        while True:
            for key in range(1, LOGITECH_MAX_GKEYS):
                for state in range(1, LOGITECH_MAX_M_STATES):
                    gkey = get_gkey_name(key, state)
                    LOG.debug(f"Button {gkey} is pressed")
            sleep(0.1)
    except KeyboardInterrupt:
        logi_gkey_shutdown()


def get_gkey_name(key: int, state: int) -> str:
    gkey = ''
    if logi_gkey_is_keyboard_gkey_pressed(g_key=key, mode=state):
        gkey = logi_gkey_is_keyboard_gkey_string(key, state)
        print(f"Button {gkey.split('/')} is pressed")
    return gkey
