# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.command import ShdlcCommand
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_property_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCommand(id=42, data=[], max_response_time=0.5)
    assert type(cmd.id) is int
    assert cmd.id == 42


@pytest.mark.parametrize("data", [
    pytest.param([0x00, 0x55, 0xFF], id="list"),
    pytest.param(b"\x00U\xff", id="bytes"),
    pytest.param(bytearray(b"\x00U\xff"), id="bytearray"),
])
def test_property_data(data):
    """
    Test if the value and type of the "data" property is correct. Note: The
    type must always be "bytes", no matter what type was passed to the
    constructor!
    """
    cmd = ShdlcCommand(id=42, data=data, max_response_time=0.5)
    assert type(cmd.data) is bytes
    assert cmd.data == b"\x00U\xff"


def test_property_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCommand(id=42, data=[], max_response_time=42.0)
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 42.0


def test_property_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCommand(id=42, data=[], max_response_time=0.5,
                       post_processing_time=42.0)
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 42.0


@pytest.mark.parametrize("data,min_length,max_length", [
    pytest.param(b"", 0, 0, id="0[0-0]"),
    pytest.param(b"", 0, 1, id="0[0-1]"),
    pytest.param(b"", 0, 255, id="0[0-255]"),
    pytest.param(b"\x00", 0, 1, id="1[0-1]"),
    pytest.param(b"\x00", 1, 1, id="1[1-1]"),
    pytest.param(b"\x00\x00\x00\x00\x00\x00", 0, 255, id="6[0-255]"),
    pytest.param(b"\x00\x00\x00\x00\x00\x00", 6, 6, id="6[6-6]"),
])
def test_check_response_length(data, min_length, max_length):
    """
    Test if "check_response_length()" doesn't raise an exception if the
    response length is valid.
    """
    cmd = ShdlcCommand(id=42, data=[], max_response_time=0.5,
                       min_response_length=min_length,
                       max_response_length=max_length)
    cmd.check_response_length(data)


@pytest.mark.parametrize("data,min_length,max_length", [
    pytest.param(b"", 1, 1, id="0[1-1]"),
    pytest.param(b"", 1, 255, id="0[1-255]"),
    pytest.param(b"\x00", 0, 0, id="1[0-0]"),
    pytest.param(b"\x00", 2, 255, id="1[2-255]"),
    pytest.param(b"\x00\x00\x00\x00\x00\x00", 0, 5, id="6[0-5]"),
    pytest.param(b"\x00\x00\x00\x00\x00\x00", 7, 7, id="6[7-7]"),
])
def test_check_response_length_raises(data, min_length, max_length):
    """
    Test if "check_response_length()" raises an ShdlcResponseError if the
    response length is wrong.
    """
    cmd = ShdlcCommand(id=42, data=[], max_response_time=0.5,
                       min_response_length=min_length,
                       max_response_length=max_length)
    with pytest.raises(ShdlcResponseError):
        cmd.check_response_length(data)


def test_interpret_response():
    """
    Test if the return value and type of the "interpret_response()" method is
    correct.
    """
    cmd = ShdlcCommand(id=42, data=[], max_response_time=0.5)
    input = b"\x00\x55\x00"
    cmd.check_response_length(input)
    response = cmd.interpret_response(input)
    assert type(response) is bytes
    assert response == input
