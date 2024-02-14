from ctypes import CDLL, CFUNCTYPE, POINTER, Structure, c_bool, c_uint, c_void_p, c_wchar_p, pointer
from logging import getLogger
from typing import ClassVar

from dcspy.sdk import KeyDll, load_dll

LOG = getLogger(__name__)


class GkeyCode(Structure):
    _fields_: ClassVar = [
        ('keyIdx', c_uint, 8),
        ('keyDown', c_uint, 1),
        ('mState', c_uint, 2),
        ('mouse', c_uint, 1),
        ('reserved1', c_uint, 4),
        ('reserved2', c_uint, 16)
    ]


CALLBACK = CFUNCTYPE(None, GkeyCode, c_wchar_p, c_void_p)


class logiGkeyCBContext(Structure):
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

    def callback(self, gKeyCode, gkeyOrButtonString, context) -> None:
        """
        Receive callback events for G-key button pushes.

        This function is provided to the Logitech GKey SDK when initialised
        and is called whenever a G-key event occurs. This then calls the
        callback handler provided by the user.
        """
        LOG.debug(f'Gkey callback: gkey {gkeyOrButtonString}, key down: {gKeyCode.keyDown}')
        self.gkey_callback_handler(gkeyOrButtonString, gKeyCode.keyIdx, gKeyCode.mState, gKeyCode.keyDown)

    def logi_gkey_init(self) -> bool:
        """
        Make necessary initializations.

        It must be called before your application can see G-key/button events.
        :return: If the function succeeds, it returns True. Otherwise, False.
        """
        try:
            LOG.info('Initialising Logitch Gkey SDK...')
            self.gkeyContext = logiGkeyCBContext()
            self.gkeyContext.gkeyCallBack = CALLBACK(self.callback)
            self.gkeyContext.gkeyContext = c_void_p()
            self.gkeyContextPointer = pointer(self.gkeyContext)

            self.KEY_DLL.LogiGkeyInit.restype = c_bool
            self.KEY_DLL.LogiGkeyInit.argtypes = [POINTER(logiGkeyCBContext)]

            return self.KEY_DLL.LogiGkeyInit(self.gkeyContextPointer)  # type: ignore[attr-defined]
        except AttributeError:
            return False

    def logi_gkey_shutdown(self) -> None:
        """Unload the corresponding DLL and frees up any allocated resources."""
        try:
            self.KEY_DLL.LogiGkeyShutdown()  # type: ignore[attr-defined]
        except AttributeError:
            pass
