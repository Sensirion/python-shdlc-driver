# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.commands.system_up_time import \
    ShdlcCmdGetSystemUpTime
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCmdGetSystemUpTime()
    assert type(cmd.id) is int
    assert cmd.id == 0x93


def test_data():
    """
    Test if the value and type of the "data" property is correct.
    """
    cmd = ShdlcCmdGetSystemUpTime()
    assert type(cmd.data) is bytes
    assert cmd.data == b""


def test_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCmdGetSystemUpTime()
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 0.05


def test_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCmdGetSystemUpTime()
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 0.0


@pytest.mark.parametrize("input", [
    b"",  # too short
    b"\x00\x00\x00",  # too short
    b"\x00\x00\x00\x00\x00",  # too long
    b"\x00\x00\x00\x00\x00\x00\x00",  # too long
])
def test_check_response_length_invalid(input):
    """
    Test if "check_response_length()" raises an ShdlcResponseError if the
    response length is wrong.
    """
    cmd = ShdlcCmdGetSystemUpTime()
    with pytest.raises(ShdlcResponseError):
        cmd.check_response_length(input)


@pytest.mark.parametrize("input,expected_time", [
    pytest.param(b"\x00\x00\x00\x00", 0x00000000, id="0x00000000"),
    pytest.param(b"\x00\x01\x02\x03", 0x00010203, id="0x00010203"),
    pytest.param(b"\xFF\xFF\xFF\xFF", 0xFFFFFFFF, id="0xFFFFFFFF"),
])
def test_interpret_response(input, expected_time):
    """
    Test if the return value and type of the "interpret_response()" method is
    correct.
    """
    cmd = ShdlcCmdGetSystemUpTime()
    cmd.check_response_length(input)
    time = cmd.interpret_response(input)
    assert type(time) == type(expected_time)
    assert time == expected_time
