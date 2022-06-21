# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.commands.device_info import \
    ShdlcCmdGetProductSubType
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCmdGetProductSubType()
    assert type(cmd.id) is int
    assert cmd.id == 0xD0


def test_data():
    """
    Test if the value and type of the "data" property is correct.
    """
    cmd = ShdlcCmdGetProductSubType()
    assert type(cmd.data) is bytes
    assert cmd.data == b"\x04"


def test_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCmdGetProductSubType()
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 0.5


def test_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCmdGetProductSubType()
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 0.0


@pytest.mark.parametrize("input", [
    b"",  # too short
    b"\x00\x00",  # too long
    b"\xFF\xFF\xFF",  # too long
])
def test_check_response_length_invalid(input):
    """
    Test if "check_response_length()" raises an ShdlcResponseError if the
    response length is wrong.
    """
    cmd = ShdlcCmdGetProductSubType()
    with pytest.raises(ShdlcResponseError):
        cmd.check_response_length(input)


@pytest.mark.parametrize("input,output", [
    pytest.param(b"\x00", 0x00, id="0x00"),
    pytest.param(b"\x05", 0x05, id="0x05"),
    pytest.param(b"\xFF", 0xFF, id="0xFF"),
])
def test_interpret_response(input, output):
    """
    Test if the value and type of the "interpret_response()" method is correct.
    """
    cmd = ShdlcCmdGetProductSubType()
    cmd.check_response_length(input)
    response = cmd.interpret_response(input)
    assert type(response) is int
    assert response == output
