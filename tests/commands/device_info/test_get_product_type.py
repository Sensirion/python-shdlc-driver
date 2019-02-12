# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function, unicode_literals
from sensirion_shdlc_driver.commands.device_info import ShdlcCmdGetProductType
import pytest


def test_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCmdGetProductType()
    assert type(cmd.id) is int
    assert cmd.id == 0xD0


def test_data():
    """
    Test if the value and type of the "data" property is correct.
    """
    cmd = ShdlcCmdGetProductType()
    assert type(cmd.data) is bytes
    assert cmd.data == b"\x00"


def test_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCmdGetProductType()
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 0.5


def test_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCmdGetProductType()
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 0.0


@pytest.mark.parametrize("input,output", [
    pytest.param(b"", "", id=""),
    pytest.param(b"\x00", "", id="0x00"),
    pytest.param(b"01234567", "01234567", id="01234567"),
    pytest.param(b"01234567\x00", "01234567", id="012345670x00"),
    pytest.param(b"Hello World!", "Hello World!", id="Hello World!"),
    pytest.param(b"Hello World!\x00", "Hello World!", id="Hello World!0x00"),
])
def test_interpret_response(input, output):
    """
    Test if the return value and type of the "interpret_response()" method is
    correct.
    """
    cmd = ShdlcCmdGetProductType()
    cmd.check_response_length(input)
    response = cmd.interpret_response(input)
    assert type(response) is str
    assert response == str(output)
