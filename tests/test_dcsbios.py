from pytest import mark


def test_process_byte_wait_for_sync_to_address_low(protocol_parser):
    assert protocol_parser.state == 'WAIT_FOR_SYNC'
    for _ in range(4):
        protocol_parser.process_byte(0x55)
    assert protocol_parser.state == 'ADDRESS_LOW'


def test_process_byte_address_low_to_address_high(protocol_parser):
    protocol_parser.state = 'ADDRESS_LOW'
    data_sent = 0x0f
    protocol_parser.process_byte(data_sent)
    assert protocol_parser.state == 'ADDRESS_HIGH'
    assert protocol_parser.address == data_sent


def test_process_byte_address_high_to_wait_to_sync(protocol_parser):
    protocol_parser.state = 'ADDRESS_HIGH'
    protocol_parser.address = 0x5355
    protocol_parser.process_byte(0x02)
    assert protocol_parser.address == 0x5555
    assert protocol_parser.state == 'WAIT_FOR_SYNC'


def test_process_byte_address_high_to_wait_to_count_low(protocol_parser):
    protocol_parser.state = 'ADDRESS_HIGH'
    protocol_parser.process_byte(0x02)
    assert protocol_parser.address != 0x5555
    assert protocol_parser.state == 'COUNT_LOW'


def test_process_byte_count_low_to_count_high(protocol_parser):
    protocol_parser.state = 'COUNT_LOW'
    data_sent = 0x0f
    protocol_parser.process_byte(data_sent)
    assert protocol_parser.state == 'COUNT_HIGH'
    assert protocol_parser.count == data_sent


def test_process_byte_count_high_to_data_low(protocol_parser):
    protocol_parser.state = 'COUNT_HIGH'
    protocol_parser.process_byte(0x0f)
    assert protocol_parser.state == 'DATA_LOW'
    assert protocol_parser.count == 0xf00


def test_process_byte_data_low_to_data_high(protocol_parser):
    protocol_parser.state = 'DATA_LOW'
    protocol_parser.count = 2
    data_sent = 0x0f
    protocol_parser.process_byte(data_sent)
    assert protocol_parser.state == 'DATA_HIGH'
    assert protocol_parser.count == 1
    assert protocol_parser.data == data_sent


def test_process_byte_data_high_to_data_low(protocol_parser):
    protocol_parser.state = 'DATA_HIGH'
    protocol_parser.count = 3
    data_sent = 0x0f
    protocol_parser.process_byte(data_sent)
    assert protocol_parser.state == 'DATA_LOW'
    assert protocol_parser.count == 2
    assert protocol_parser.data == 0xf00


def test_process_byte_data_high_to_address_low(protocol_parser):
    protocol_parser.state = 'DATA_HIGH'
    protocol_parser.count = 1
    data_sent = 0x0f
    protocol_parser.process_byte(data_sent)
    assert protocol_parser.state == 'ADDRESS_LOW'
    assert protocol_parser.count == 0
    assert protocol_parser.data == 0xf00
    assert protocol_parser.address == 2


def test_process_byte_data_high_callback(protocol_parser):
    from functools import partial

    def _callback(addr, data):
        assert addr == 2
        assert data == 0xa00

    protocol_parser.write_callbacks.add(partial(_callback))
    protocol_parser.state = 'DATA_HIGH'
    protocol_parser.address = 2
    protocol_parser.process_byte(0x0a)


def test_process_byte_wait_for_sync_callback(protocol_parser):
    from functools import partial

    def _callback(*args, **kwargs):
        assert args == tuple()
        assert kwargs == dict()

    protocol_parser.frame_sync_callbacks.add(partial(_callback))
    protocol_parser.sync_byte_count = 3
    protocol_parser.process_byte(bytes([0x55]))


@mark.parametrize('class_name, params', [('StringBuffer', {'address': 0x192a, 'length': 6}),
                                         ('IntegerBuffer', {'address': 0x1936, 'mask': 0x8000, 'shift_by': 0xf})])
def test_simple_instance_of_buffers(class_name, params, protocol_parser):
    from dcspy import dcsbios

    buff = getattr(dcsbios, class_name)(parser=protocol_parser, callback=lambda x: x, **params)
    assert 'on_dcsbios_write' in dir(buff)


def test_integer_buffer_callback(protocol_parser):
    from functools import partial
    from dcspy.dcsbios import IntegerBuffer

    def _callback(*args, **kwargs):
        assert args == (1,)
        assert kwargs == dict()

    IntegerBuffer(parser=protocol_parser, address=0x1938, mask=0x200, shift_by=0x9, callback=partial(_callback))
    protocol_parser.state = 'DATA_HIGH'
    protocol_parser.count = 1
    protocol_parser.address = 0x1938
    protocol_parser.data = 0x927  # 0x827
    protocol_parser.process_byte(0x1)
