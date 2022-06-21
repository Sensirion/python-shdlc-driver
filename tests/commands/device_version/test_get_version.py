# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.commands.device_version import ShdlcCmdGetVersion
from sensirion_shdlc_driver.errors import ShdlcResponseError
from sensirion_shdlc_driver.types import Version
import pytest


def test_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCmdGetVersion()
    assert type(cmd.id) is int
    assert cmd.id == 0xD1


def test_data():
    """
    Test if the value and type of the "data" property is correct.
    """
    cmd = ShdlcCmdGetVersion()
    assert type(cmd.data) is bytes
    assert cmd.data == b""


def test_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCmdGetVersion()
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 0.5


def test_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCmdGetVersion()
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 0.0


@pytest.mark.parametrize("input", [
    b"",  # too short
    b"\x00\x00\x00",  # too short
    b"\x00\x00\x00\x00\x00\x00",  # too short
    b"\x00\x00\x00\x00\x00\x00\x00\x00",  # too long
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",  # too long
])
def test_check_response_length_invalid(input):
    """
    Test if "check_response_length()" raises an ShdlcResponseError if the
    response length is wrong.
    """
    cmd = ShdlcCmdGetVersion()
    with pytest.raises(ShdlcResponseError):
        cmd.check_response_length(input)


@pytest.mark.parametrize("input,output", [
    pytest.param(b"\x00\x00\x00\x00\x00\x00\x00",
                 "Firmware 0.0, Hardware 0.0, Protocol 0.0",
                 id="all_zeros"),
    pytest.param(b"\x00\x01\x02\x03\x04\x05\x06",
                 "Firmware 0.1-debug, Hardware 3.4, Protocol 5.6",
                 id="incrementing"),
    pytest.param(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF",
                 "Firmware 255.255-debug, Hardware 255.255, Protocol 255.255",
                 id="all_0xFF"),
])
def test_interpret_response(input, output):
    """
    Test if the return value and type of the "interpret_response()" method is
    correct.
    """
    cmd = ShdlcCmdGetVersion()
    cmd.check_response_length(input)
    response = cmd.interpret_response(input)
    assert type(response) is Version
    assert str(response) == output
