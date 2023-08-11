from logging import getLogger
from time import sleep

from _cffi_backend import Lib
from cffi import FFI

from dcspy.sdk import KeyDll, load_dll

LOG = getLogger(__name__)
LOGITECH_MAX_GKEYS = 30
LOGITECH_MAX_M_STATES = 4
KEY_DLL: Lib = load_dll(KeyDll)
ffi = FFI()

KEY_DLL.LogiGkeyInit(ffi.NULL)

try:
    while True:
        for index in range(1, LOGITECH_MAX_GKEYS):
            for mKeyIndex in range(1, LOGITECH_MAX_M_STATES):
                if KEY_DLL.LogiGkeyIsKeyboardGkeyPressed(index, mKeyIndex):
                    LOG.debug(f"Button {index} is pressed")
                    gkey_str = KEY_DLL.LogiGkeyGetKeyboardGkeyString(index, mKeyIndex)
                    print(f"Button: {ffi.string(gkey_str)}")
        sleep(0.1)
except KeyboardInterrupt:
    pass

# Shutdown the G-key SDK
KEY_DLL.LogiGkeyShutdown()
