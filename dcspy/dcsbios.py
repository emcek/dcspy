from enum import Enum, auto
from functools import partial
from struct import pack
from typing import Callable, Set


class ParserState(Enum):
    """Protocol parser states."""
    ADDRESS_LOW = auto()
    ADDRESS_HIGH = auto()
    COUNT_LOW = auto()
    COUNT_HIGH = auto()
    DATA_LOW = auto()
    DATA_HIGH = auto()
    WAIT_FOR_SYNC = auto()


class ProtocolParser:
    """DCS_BIOS protocol parser."""
    def __init__(self) -> None:
        """Basic constructor."""
        self.state = ParserState.WAIT_FOR_SYNC
        self.sync_byte_count = 0
        self.address = 0
        self.count = 0
        self.data = 0
        self.write_callbacks: Set[Callable] = set()
        self.frame_sync_callbacks: Set[Callable] = set()

    def process_byte(self, int_byte: int) -> None:
        """
        State machine - processing of byte.

        Allowed states are: ParserState
        :param int_byte:
        """
        state_handling = getattr(self, f'_{self.state.name.lower()}')
        if self.state == ParserState.WAIT_FOR_SYNC:
            state_handling()
        else:
            state_handling(int_byte)

        if int_byte == 0x55:
            self.sync_byte_count += 1
        else:
            self.sync_byte_count = 0

        self._wait_for_sync()

    def _address_low(self, int_byte: int) -> None:
        """
        Handling of ADDRESS_LOW state.

        :param int_byte: data to process
        """
        self.address = int_byte
        self.state = ParserState.ADDRESS_HIGH

    def _address_high(self, int_byte: int) -> None:
        """
        Handling of ADDRESS_HIGH state.

        :param int_byte: data to process
        """
        self.address += int_byte * 256
        if self.address != 0x5555:
            self.state = ParserState.COUNT_LOW
        else:
            self.state = ParserState.WAIT_FOR_SYNC

    def _count_low(self, int_byte: int) -> None:
        """
        Handling of COUNT_LOW state.

        :param int_byte: data to process
        """
        self.count = int_byte
        self.state = ParserState.COUNT_HIGH

    def _count_high(self, int_byte: int) -> None:
        """
        Handling of COUNT_HIGH state.

        :param int_byte: data to process
        """
        self.count += 256 * int_byte
        self.state = ParserState.DATA_LOW

    def _data_low(self, int_byte: int) -> None:
        """
        Handling of DATA_LOW state.

        :param int_byte: data to process
        """
        self.data = int_byte
        self.count -= 1
        self.state = ParserState.DATA_HIGH

    def _data_high(self, int_byte: int) -> None:
        """
        Handling of DATA_HIGH state.

        :param int_byte: data to process
        """
        self.data += 256 * int_byte
        self.count -= 1
        for callback in self.write_callbacks:
            callback(self.address, self.data)
        self.address += 2
        if self.count == 0:
            self.state = ParserState.ADDRESS_LOW
        else:
            self.state = ParserState.DATA_LOW

    def _wait_for_sync(self) -> None:
        """Handling of WAIT_FOR_SYNC state."""
        if self.sync_byte_count == 4:
            self.state = ParserState.ADDRESS_LOW
            self.sync_byte_count = 0
            for callback in self.frame_sync_callbacks:
                callback()


class StringBuffer:
    """String buffer for DCS-BIOS protocol."""
    def __init__(self, parser: ProtocolParser, address: int, max_length: int, callback: Callable) -> None:
        """
        Basic constructor.

        :param parser:
        :param address:
        :param max_length:
        :param callback:
        """
        self.__address = address
        self.__length = max_length
        self.__dirty = False
        self.buffer = bytearray(max_length)
        self.callbacks: Set[Callable] = set()
        self.callbacks.add(callback)
        parser.write_callbacks.add(partial(self.on_dcsbios_write))

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
            str_buff = self.buffer.split(sep=b'\x00', maxsplit=1)[0].decode('latin-1')
            for callback in self.callbacks:
                callback(str_buff)


class IntegerBuffer:
    """Integer buffer for DCS-BIOS protocol."""
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
        self.__value = int()
        self.callbacks: Set[Callable] = set()
        self.callbacks.add(callback)
        parser.write_callbacks.add(partial(self.on_dcsbios_write))

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
