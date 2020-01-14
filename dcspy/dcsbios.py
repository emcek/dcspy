from struct import pack
from typing import Callable, Set


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

    def process_byte(self, byte: bytes) -> None:
        """
        State machine - processing of byte.

        Allowed states are: ADDRESS_LOW, ADDRESS_HIGH, COUNT_LOW, COUNT_HIGH, DATA_LOW, DATA_HIGH, WAIT_FOR_SYNC

        :param byte:
        """
        int_byte = ord(byte)
        getattr(self, f'_{self.__state.lower()}')(int_byte)
        if int_byte == 0x55:
            self.__sync_byte_count += 1
        else:
            self.__sync_byte_count = 0
        self._wait_for_sync()

    def _address_low(self, int_byte: int) -> None:
        """
        Handling of ADDRESS_LOW state.

        :param int_byte: data to process
        """
        self.__address = int_byte
        self.__state = 'ADDRESS_HIGH'

    def _address_high(self, int_byte: int) -> None:
        """
        Handling of ADDRESS_HIGH state.

        :param int_byte: data to process
        """
        self.__address += int_byte * 256
        if self.__address != 0x5555:
            self.__state = 'COUNT_LOW'
        else:
            self.__state = 'WAIT_FOR_SYNC'

    def _count_low(self, int_byte: int) -> None:
        """
        Handling of COUNT_LOW state.

        :param int_byte: data to process
        """
        self.__count = int_byte
        self.__state = 'COUNT_HIGH'

    def _count_high(self, int_byte: int) -> None:
        """
        Handling of COUNT_HIGH state.

        :param int_byte: data to process
        """
        self.__count += 256 * int_byte
        self.__state = 'DATA_LOW'

    def _data_low(self, int_byte: int) -> None:
        """
        Handling of DATA_LOW state.

        :param int_byte: data to process
        """
        self.__data = int_byte
        self.__count -= 1
        self.__state = 'DATA_HIGH'

    def _data_high(self, int_byte: int) -> None:
        """
        Handling of DATA_HIGH state.

        :param int_byte: data to process
        """
        self.__data += 256 * int_byte
        self.__count -= 1
        for callback in self.write_callbacks:
            callback(self.__address, self.__data)
        self.__address += 2
        if self.__count == 0:
            self.__state = 'ADDRESS_LOW'
        else:
            self.__state = 'DATA_LOW'

    def _wait_for_sync(self, *args: int) -> None:
        """
        Handling of WAIT_FOR_SYNC state.

        :param args: dumb, just to be similar to other state handling method.
        """
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
        parser.write_callbacks.add(lambda addr, data: self.on_dcsbios_write(address=addr, data=data))

    def set_char(self, index, char) -> None:
        """
        Set char.

        :param index:
        :param char:
        """
        if self.buffer[index] != char:
            self.buffer[index] = char
            self.__dirty = True

    def on_dcsbios_write(self, address: int, data: int) -> None:
        """
        Callback function.

        :param address:
        :param data:
        """
        if self.__address <= address < self.__address + self.__length:
            data_bytes = pack('<H', data)
            self.set_char(address - self.__address, data_bytes[0])
            if self.__address + self.__length > (address + 1):
                self.set_char(address - self.__address + 1, data_bytes[1])

        if address == 0xfffe and self.__dirty:
            self.__dirty = False
            str_buff = self.buffer.split(b'\x00')[0].decode('latin-1')
            for callback in self.callbacks:
                callback(str_buff)


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
        parser.write_callbacks.add(lambda addr, data: self.on_dcsbios_write(address=addr, data=data))

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
