# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.commands.bootloader import \
    ShdlcCmdFirmwareUpdateData
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCmdFirmwareUpdateData(data=b"\x42")
    assert type(cmd.id) is int
    assert cmd.id == 0xF3


@pytest.mark.parametrize("data_input,expected_data_output", [
    (b"", b"\x02"),
    (b"\x11\x22\x33", b"\x02\x11\x22\x33"),
    ([], b"\x02"),
    ([0x11, 0x22, 0x33], b"\x02\x11\x22\x33"),
    (bytearray([]), b"\x02"),
    (bytearray([0x11, 0x22, 0x33]), b"\x02\x11\x22\x33"),
])
def test_data(data_input, expected_data_output):
    """
    Test if the value and type of the "data" property is correct.
    """
    cmd = ShdlcCmdFirmwareUpdateData(data=data_input)
    assert type(cmd.data) is bytes
    assert cmd.data == expected_data_output


def test_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCmdFirmwareUpdateData(data=b"\x42")
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 1.0


def test_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCmdFirmwareUpdateData(data=b"\x42")
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 0.0


@pytest.mark.parametrize("input", [
    b"\x00",  # too long
    b"\x00\x00\x00\x00\x00\x00",  # too long
])
def test_check_response_length_invalid(input):
    """
    Test if "check_response_length()" raises an ShdlcResponseError if the
    response length is wrong.
    """
    cmd = ShdlcCmdFirmwareUpdateData(data=b"\x42")
    with pytest.raises(ShdlcResponseError):
        cmd.check_response_length(input)


def test_interpret_response():
    """
    Test if the return value and type of the "interpret_response()" method is
    correct.
    """
    cmd = ShdlcCmdFirmwareUpdateData(data=b"\x42")
    cmd.check_response_length(b"")
    response = cmd.interpret_response(b"")
    assert response is None
