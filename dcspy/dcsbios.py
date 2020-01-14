# from functools import partial
from struct import pack
from typing import Callable, Set  # , Dict


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

    @property
    def state(self) -> str:
        """
        Get current state.

        :return: current state
        :rtype: str
        """
        return self.__state

    @state.setter
    def state(self, new_state: str) -> None:
        """
        Set new state.

        Allowed states are: ADDRESS_LOW, ADDRESS_HIGH, COUNT_LOW, COUNT_HIGH, DATA_LOW, DATA_HIGH, WAIT_FOR_SYNC


        :param new_state: one of allowed state
        :type new_state: str
        """
        self.__state = new_state

    def process_byte(self, byte: bytes) -> None:
        """
        Process byte.

        :param byte:
        """
        int_byte = ord(byte)
        # states: Dict[str, Callable] = {
        #     'ADDRESS_LOW': partial(self.address_low, int_byte),
        #     'ADDRESS_HIGH': partial(self.address_high, int_byte),
        #     'COUNT_LOW': partial(self.count_low, int_byte),
        #     'COUNT_HIGH': partial(self.count_high, int_byte),
        #     'DATA_LOW': partial(self.data_low, int_byte),
        #     'DATA_HIGH': partial(self.data_high, int_byte),
        #     'WAIT_FOR_SYNC': partial(self.wait_for_sync, int_byte)}
        # states[self.state]()
        getattr(self, self.state.lower())(int_byte)
        self.wait_for_sync(int_byte)

        # if self.__state == 'ADDRESS_LOW':
        #     self.__address = int_byte
        #     self.__state = 'ADDRESS_HIGH'
        # elif self.__state == 'ADDRESS_HIGH':
        #     self.__address += int_byte * 256
        #     if self.__address != 0x5555:
        #         self.__state = 'COUNT_LOW'
        #     else:
        #         self.__state = 'WAIT_FOR_SYNC'
        # elif self.__state == 'COUNT_LOW':
        #     self.__count = int_byte
        #     self.__state = 'COUNT_HIGH'
        # elif self.__state == 'COUNT_HIGH':
        #     self.__count += 256 * int_byte
        #     self.__state = 'DATA_LOW'
        # elif self.__state == 'DATA_LOW':
        #     self.__data = int_byte
        #     self.__count -= 1
        #     self.__state = 'DATA_HIGH'
        # elif self.__state == 'DATA_HIGH':
        #     self.__data += 256 * int_byte
        #     self.__count -= 1
        #     for callback in self.write_callbacks:
        #         callback(self.__address, self.__data)
        #     self.__address += 2
        #     if self.__count == 0:
        #         self.__state = 'ADDRESS_LOW'
        #     else:
        #         self.__state = 'DATA_LOW'
        #
        # if int_byte == 0x55:
        #     self.__sync_byte_count += 1
        # else:
        #     self.__sync_byte_count = 0
        #
        # if self.__sync_byte_count == 4:
        #     self.__state = 'ADDRESS_LOW'
        #     self.__sync_byte_count = 0
        #     for callback in self.frame_sync_callbacks:
        #         callback()

    def address_low(self, int_byte):
        self.__address = int_byte
        self.state = 'ADDRESS_HIGH'

    def address_high(self, int_byte):
        self.__address += int_byte * 256
        if self.__address != 0x5555:
            self.state = 'COUNT_LOW'
        else:
            self.state = 'WAIT_FOR_SYNC'

    def count_low(self, int_byte):
        self.__count = int_byte
        self.__state = 'COUNT_HIGH'

    def count_high(self, int_byte):
        self.__count += 256 * int_byte
        self.state = 'DATA_LOW'

    def data_low(self, int_byte):
        self.__data = int_byte
        self.__count -= 1
        self.state = 'DATA_HIGH'

    def data_high(self, int_byte):
        self.__data += 256 * int_byte
        self.__count -= 1
        for callback in self.write_callbacks:
            callback(self.__address, self.__data)
        self.__address += 2
        if self.__count == 0:
            self.state = 'ADDRESS_LOW'
        else:
            self.state = 'DATA_LOW'

    def wait_for_sync(self, int_byte):
        if int_byte == 0x55:
            self.__sync_byte_count += 1
        else:
            self.__sync_byte_count = 0

        if self.__sync_byte_count == 4:
            self.state = 'ADDRESS_LOW'
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
