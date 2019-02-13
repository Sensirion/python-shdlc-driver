# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.serial_frame_builder import \
    ShdlcSerialMosiFrameBuilder
import pytest


@pytest.mark.parametrize("address,command,data,expected", [
    pytest.param(0x00,
                 0x00,
                 [],
                 b"\x7e\x00\x00\x00\xff\x7e",
                 id="all_zeros_nodata"),
    pytest.param(0x00,
                 0x00,
                 [0x00] * 255,
                 b"\x7e\x00\x00\xff" + b"\x00" * 255 + b"\x00\x7e",
                 id="all_zeros_withdata"),
    pytest.param(0xFF,
                 0xFF,
                 [0xFF] * 255,
                 b"\x7e\xff\xff\xff" + b"\xff" * 255 + b"\x01\x7e",
                 id="all_0xFF_withdata"),
    pytest.param(0x7e,
                 0x7d,
                 [0x11, 0x12, 0x13, 0x14],
                 b"\x7e\x7d\x5e\x7d\x5d\x04\x7d\x31\x12\x7d\x33\x14\xb6\x7e",
                 id="byte_stuffing_in_address_command_and_data"),
    pytest.param(0x00,
                 0x01,
                 [0x7E] * 255,
                 b"\x7e\x00\x01\xff" + b"\x7d\x5e" * 255 + b"\x7d\x5d\x7e",
                 id="byte_stuffing_in_data_and_checksum"),
])
def test_to_bytes(address, command, data, expected):
    """
    Test if the value and type of the "to_bytes()" method is correct.
    """
    builder = ShdlcSerialMosiFrameBuilder(address, command, data)
    frame = builder.to_bytes()
    assert type(frame) is bytes
    assert frame == expected
