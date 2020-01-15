def test_process_byte_wait_for_sync_to_address_low():
    from dcspy.dcsbios import ProtocolParser
    p = ProtocolParser()
    assert p._ProtocolParser__state == 'WAIT_FOR_SYNC'
    for _ in range(4):
        p.process_byte(bytes([0x55]))
    assert p._ProtocolParser__state == 'ADDRESS_LOW'
