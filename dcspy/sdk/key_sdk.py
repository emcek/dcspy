from logging import getLogger
from time import sleep

from _cffi_backend import Lib
from cffi import FFI

from dcspy import LOGITECH_MAX_GKEYS, LOGITECH_MAX_M_STATES
from dcspy.sdk import KeyDll, load_dll

LOG = getLogger(__name__)
KEY_DLL: Lib = load_dll(KeyDll)
ffi = FFI()

KEY_DLL.LogiGkeyInit(ffi.NULL)

try:
    while True:
        for index in range(1, LOGITECH_MAX_GKEYS):
            for mKeyIndex in range(1, LOGITECH_MAX_M_STATES):
                if KEY_DLL.LogiGkeyIsKeyboardGkeyPressed(index, mKeyIndex):
                    gkey = KEY_DLL.LogiGkeyGetKeyboardGkeyString(index, mKeyIndex)
                    gkey_str = ffi.string(gkey)
                    print(f"Button {gkey_str.split('/')} is pressed")
                    LOG.debug(f"Button {gkey_str} is pressed")
        sleep(0.1)
except KeyboardInterrupt:
    KEY_DLL.LogiGkeyShutdown()
