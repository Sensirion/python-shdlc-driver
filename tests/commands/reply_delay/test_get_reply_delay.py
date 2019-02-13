# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function, unicode_literals
from sensirion_shdlc_driver.commands.reply_delay import ShdlcCmdGetReplyDelay
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCmdGetReplyDelay()
    assert type(cmd.id) is int
    assert cmd.id == 0x95


def test_data():
    """
    Test if the value and type of the "data" property is correct.
    """
    cmd = ShdlcCmdGetReplyDelay()
    assert type(cmd.data) is bytes
    assert cmd.data == b""


def test_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCmdGetReplyDelay()
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 0.05


def test_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCmdGetReplyDelay()
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 0.0


@pytest.mark.parametrize("input", [
    b"",  # too short
    b"\x00",  # too short
    b"\x00\x00\x00",  # too long
    b"\x00\x00\x00\x00",  # too long
])
def test_check_response_length_invalid(input):
    """
    Test if "check_response_length()" raises an ShdlcResponseError if the
    response length is wrong.
    """
    cmd = ShdlcCmdGetReplyDelay()
    with pytest.raises(ShdlcResponseError):
        cmd.check_response_length(input)


@pytest.mark.parametrize("input,expected_address", [
    pytest.param(b"\x00\x00", 0x0000, id="0x0000"),
    pytest.param(b"\x13\x37", 0x1337, id="0x1337"),
    pytest.param(b"\xFF\xFF", 0xFFFF, id="0xFFFF"),
])
def test_interpret_response(input, expected_address):
    """
    Test if the return value and type of the "interpret_response()" method is
    correct.
    """
    cmd = ShdlcCmdGetReplyDelay()
    cmd.check_response_length(input)
    address = cmd.interpret_response(input)
    assert type(address) == type(expected_address)
    assert address == expected_address
