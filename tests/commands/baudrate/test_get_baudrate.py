# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.commands.baudrate import ShdlcCmdGetBaudrate
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCmdGetBaudrate()
    assert type(cmd.id) is int
    assert cmd.id == 0x91


def test_data():
    """
    Test if the value and type of the "data" property is correct.
    """
    cmd = ShdlcCmdGetBaudrate()
    assert type(cmd.data) is bytes
    assert cmd.data == b""


def test_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCmdGetBaudrate()
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 0.05


def test_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCmdGetBaudrate()
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 0.0


@pytest.mark.parametrize("input", [
    b"",  # too short
    b"\x00\x00\x00",  # too short
    b"\x00\x00\x00\x00\x00",  # too long
    b"\x00\x00\x00\x00\x00\x00",  # too long
])
def test_check_response_length_invalid(input):
    """
    Test if "check_response_length()" raises an ShdlcResponseError if the
    response length is wrong.
    """
    cmd = ShdlcCmdGetBaudrate()
    with pytest.raises(ShdlcResponseError):
        cmd.check_response_length(input)


@pytest.mark.parametrize("input,expected_baudrate", [
    pytest.param(b"\x00\x00\x00\x00", 0, id="0"),
    pytest.param(b"\x00\x01\xc2\x00", 115200, id="115200"),
    pytest.param(b"\xff\xff\xff\xff", 0xFFFFFFFF, id="0xFFFFFFFF"),
])
def test_interpret_response(input, expected_baudrate):
    """
    Test if the return value and type of the "interpret_response()" method is
    correct.
    """
    cmd = ShdlcCmdGetBaudrate()
    cmd.check_response_length(input)
    address = cmd.interpret_response(input)
    assert type(address) is type(expected_baudrate)
    assert address == expected_baudrate
