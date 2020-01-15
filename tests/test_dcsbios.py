def test_process_byte_wait_for_sync_to_address_low():
    from dcspy.dcsbios import ProtocolParser
    p = ProtocolParser()
    assert p.state == 'WAIT_FOR_SYNC'
    for _ in range(4):
        p.process_byte(bytes([0x55]))
    assert p.state == 'ADDRESS_LOW'


def test_process_byte_address_low_to_address_high():
    from dcspy.dcsbios import ProtocolParser
    p = ProtocolParser()
    p.state = 'ADDRESS_LOW'
    data_sent = 0x0f
    p.process_byte(bytes([data_sent]))
    assert p.state == 'ADDRESS_HIGH'
    assert p.address == data_sent
