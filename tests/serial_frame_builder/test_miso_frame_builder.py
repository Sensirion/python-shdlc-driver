# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.serial_frame_builder import ShdlcSerialMisoFrameBuilder
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_initial_data_empty():
    """
    Test if the initial value and type of the "data" property is correct.
    """
    builder = ShdlcSerialMisoFrameBuilder()
    assert type(builder.data) is bytearray
    assert len(builder.data) == 0


def test_add_data_appends():
    """
    Test if the "add_data()" method appends the passed data to the object.
    """
    builder = ShdlcSerialMisoFrameBuilder()
    builder.add_data(b"\x00\x01\x02")
    assert builder.data == b"\x00\x01\x02"
    builder.add_data(b"\x03\x04\x05")
    assert builder.data == b"\x00\x01\x02\x03\x04\x05"
    builder.add_data(b"\xfd\xfe\xff")
    assert builder.data == b"\x00\x01\x02\x03\x04\x05\xfd\xfe\xff"


def test_add_data_raises_if_max_length_reached():
    """
    Test if the "add_data()" method raises an ShdlcResponseError if no valid
    frame is contained and the maximum frame length is reached.
    """
    builder = ShdlcSerialMisoFrameBuilder()
    builder.add_data(b"\x00" * 500)
    with pytest.raises(ShdlcResponseError):
        builder.add_data(b"\x00" * 23)


def test_add_data():
    """
    Test if return type and value of the "add_data()" method is correct.
    """
    builder = ShdlcSerialMisoFrameBuilder()
    assert type(builder.add_data(b"")) is bool
    assert builder.add_data(b"") is False
    assert builder.add_data(b"\x00\x01\x02") is False  # some rubbish
    assert builder.add_data(b"\x7e\x00\x00") is False  # frame START
    assert builder.add_data(b"\x00\x00\x7e") is True  # frame STOP
    assert builder.add_data(b"\x00\x01\x02") is True  # some rubbish


@pytest.mark.parametrize("raw,exp_addr,exp_cmd,exp_state,exp_data", [
    pytest.param(b"\x7e\x00\x00\x00\x00\xff\x7e",
                 0x00,
                 0x00,
                 0x00,
                 b"",
                 id="all_zeros_nodata"),
    pytest.param(b"\x7e\x00\x00\x00\xff" + b"\x00" * 255 + b"\x00\x7e",
                 0x00,
                 0x00,
                 0x00,
                 b"\x00" * 255,
                 id="all_zeros_withdata"),
    pytest.param(b"\x7e\xff\xff\xff\xff" + b"\xff" * 255 + b"\x02\x7e",
                 0xFF,
                 0xFF,
                 0xFF,
                 b"\xff" * 255,
                 id="all_0xFF_withdata"),
    pytest.param(b"\x7e\x7d\x5e\x7d\x5d\x7d\x31\x03\x12\x7d\x33\x14\xb7\x7e",
                 0x7e,
                 0x7d,
                 0x11,
                 b"\x12\x13\x14",
                 id="byte_stuffing_in_address_command_state_and_data"),
    pytest.param(b"\x7e\x00\x01\x00\xff" + b"\x7d\x5e" * 255 + b"\x7d\x5d\x7e",
                 0x00,
                 0x01,
                 0x00,
                 b"\x7e" * 255,
                 id="byte_stuffing_in_data_and_checksum"),
])
def test_interpret_data_valid(raw, exp_addr, exp_cmd, exp_state, exp_data):
    """
    Test if return type and value of the "interpret_data()" method is correct.
    """
    builder = ShdlcSerialMisoFrameBuilder()
    assert builder.add_data(raw) is True
    recv_addr, recv_cmd, recv_state, recv_data = builder.interpret_data()
    assert type(recv_addr) is int
    assert type(recv_cmd) is int
    assert type(recv_state) is int
    assert type(recv_data) is bytes
    assert recv_addr == exp_addr
    assert recv_cmd == exp_cmd
    assert recv_state == exp_state
    assert recv_data == exp_data


@pytest.mark.parametrize("raw", [
    pytest.param(b"\x7e\x7e",
                 id="empty"),
    pytest.param(b"\x7e\x00\x00\x00\xff\x7e",
                 id="too_short"),
    pytest.param(b"\x7e\x00\x00\x00\xff" + b"\x00" * 256 + b"\x00\x7e",
                 id="too_long"),
    pytest.param(b"\x7e\x00\x00\x00\x01\xfe\x7e",
                 id="too_less_data"),
    pytest.param(b"\x7e\x00\x00\x00\x00\x00\xff\x7e",
                 id="too_much_data"),
    pytest.param(b"\x7e\x00\x00\x00\x00\xfe\x7e",
                 id="nodata_wrong_checksum"),
    pytest.param(b"\x7e\xff\xff\xff\xff" + b"\xff" * 255 + b"\x00\x7e",
                 id="all_0xFF_wrong_checksum"),
])
def test_interpret_data_invalid(raw):
    """
    Test if "interpret_data()" raises an ShdlcResponseError on invalid data.
    """
    builder = ShdlcSerialMisoFrameBuilder()
    assert builder.add_data(raw) is True
    with pytest.raises(ShdlcResponseError):
        builder.interpret_data()
