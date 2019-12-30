from struct import pack
from typing import Callable, Set


def byte2int(b: bytes) -> int:
    """
    Convert byte to intiger.

    :param b:
    :return:
    """
    return b[0]


class ProtocolParser:
    def __init__(self) -> None:
        """Basic constructor."""
        self.__state = 'WAIT_FOR_SYNC'
        self.__sync_byte_count = 0
        self.__address = 0
        self.__count = 0
        self.__data = 0
        self.write_callbacks: Set[Callable] = set()
        self.frame_sync_callbacks: Set[Callable] = set()

    def process_byte(self, c: bytes) -> None:
        """
        Precess byte.

        :param c:
        """
        c = byte2int(c)
        if self.__state == 'ADDRESS_LOW':
            self.__address = c
            self.__state = 'ADDRESS_HIGH'
        elif self.__state == 'ADDRESS_HIGH':
            self.__address += c * 256
            if self.__address != 0x5555:
                self.__state = 'COUNT_LOW'
            else:
                self.__state = 'WAIT_FOR_SYNC'
        elif self.__state == 'COUNT_LOW':
            self.__count = c
            self.__state = 'COUNT_HIGH'
        elif self.__state == 'COUNT_HIGH':
            self.__count += 256 * c
            self.__state = 'DATA_LOW'
        elif self.__state == 'DATA_LOW':
            self.__data = c
            self.__count -= 1
            self.__state = 'DATA_HIGH'
        elif self.__state == 'DATA_HIGH':
            self.__data += 256 * c
            self.__count -= 1
            for callback in self.write_callbacks:
                callback(self.__address, self.__data)
            self.__address += 2
            if self.__count == 0:
                self.__state = 'ADDRESS_LOW'
            else:
                self.__state = 'DATA_LOW'

        if c == 0x55:
            self.__sync_byte_count += 1
        else:
            self.__sync_byte_count = 0

        if self.__sync_byte_count == 4:
            self.__state = 'ADDRESS_LOW'
            self.__sync_byte_count = 0
            for callback in self.frame_sync_callbacks:
                callback()


class StringBuffer:
    def __init__(self, parser: ProtocolParser, address: int, length: int, callback: Callable) -> None:
        """
        Basic constructor.

        :param parser:
        :param address:
        :param length:
        :param callback:
        """
        self.__address = address
        self.__length = length
        self.__dirty = False
        self.buffer = bytearray(length)
        self.callbacks: Set[Callable] = set()
        if callback:
            self.callbacks.add(callback)
        parser.write_callbacks.add(lambda address, data: self.on_dcsbios_write(address, data))

    def set_char(self, i, c) -> None:
        """
        Set char.

        :param i:
        :param c:
        """
        if self.buffer[i] != c:
            self.buffer[i] = c
            self.__dirty = True

    def on_dcsbios_write(self, address, data) -> None:
        """
        Callback function.

        :param address:
        :param data:
        """
        if self.__address <= address < self.__address + self.__length:
            data_bytes = pack("<H", data)
            self.set_char(address - self.__address, data_bytes[0])
            if self.__address + self.__length > (address + 1):
                self.set_char(address - self.__address + 1, data_bytes[1])

        if address == 0xfffe and self.__dirty:
            self.__dirty = False
            s = self.buffer.split(b"\x00")[0].decode('latin-1')
            for callback in self.callbacks:
                callback(s)


class IntegerBuffer:
    def __init__(self, parser: ProtocolParser, address: int, mask: int, shift_by: int, callback: Callable) -> None:
        """
        Basic constructor.

        :param parser:
        :param address:
        :param mask:
        :param shift_by:
        :param callback:
        """
        self.__address = address
        self.__mask = mask
        self.__shift_by = shift_by
        self.__value = None
        self.callbacks: Set[Callable] = set()
        if callback:
            self.callbacks.add(callback)
        parser.write_callbacks.add(lambda address, data: self.on_dcsbios_write(address, data))

    def on_dcsbios_write(self, address: int, data: int) -> None:
        """
        Callback function.

        :param address:
        :param data:
        """
        if address == self.__address:
            value = (data & self.__mask) >> self.__shift_by
            if self.__value != value:
                self.__value = value
                for callback in self.callbacks:
                    callback(value)
