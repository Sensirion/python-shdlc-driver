# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.commands.slave_address import ShdlcCmdSetSlaveAddress
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCmdSetSlaveAddress(slave_address=0x00)
    assert type(cmd.id) is int
    assert cmd.id == 0x90


@pytest.mark.parametrize("address,data", [
    pytest.param(0x00, b"\x00", id="0x00"),
    pytest.param(0x42, b"\x42", id="0x42"),
    pytest.param(0xFF, b"\xFF", id="0xFF"),
])
def test_data(address, data):
    """
    Test if the value and type of the "data" property is correct.
    """
    cmd = ShdlcCmdSetSlaveAddress(slave_address=address)
    assert type(cmd.data) is bytes
    assert cmd.data == data


def test_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCmdSetSlaveAddress(slave_address=0x00)
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 0.05


def test_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCmdSetSlaveAddress(slave_address=0x00)
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 0.0


@pytest.mark.parametrize("input", [
    b"\x00",  # too long
    b"\x00\x00",  # too long
    b"\x00\x00\x00",  # too long
])
def test_check_response_length_invalid(input):
    """
    Test if "check_response_length()" raises an ShdlcResponseError if the
    response length is wrong.
    """
    cmd = ShdlcCmdSetSlaveAddress(slave_address=0x00)
    with pytest.raises(ShdlcResponseError):
        cmd.check_response_length(input)


def test_interpret_response():
    """
    Test if the return value and type of the "interpret_response()" method is
    correct.
    """
    cmd = ShdlcCmdSetSlaveAddress(slave_address=0x00)
    cmd.check_response_length(b"")
    response = cmd.interpret_response(b"")
    assert response is None
