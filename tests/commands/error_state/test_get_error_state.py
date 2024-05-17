# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.commands.error_state import ShdlcCmdGetErrorState
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCmdGetErrorState(clear=False)
    assert type(cmd.id) is int
    assert cmd.id == 0xD2


@pytest.mark.parametrize("clear,data", [
    pytest.param(False, b"\x00", id="noclear"),
    pytest.param(True, b"\x01", id="clear"),
])
def test_data(clear, data):
    """
    Test if the value and type of the "data" property is correct.
    """
    cmd = ShdlcCmdGetErrorState(clear=clear)
    assert type(cmd.data) is bytes
    assert cmd.data == data


def test_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCmdGetErrorState(clear=False)
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 0.5


def test_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCmdGetErrorState(clear=False)
    assert type(cmd.post_processing_time) is float
    assert cmd.post_processing_time == 0.0


@pytest.mark.parametrize("input", [
    b"",  # too short
    b"\x00\x00\x00\x00",  # too short
    b"\x00\x00\x00\x00\x00\x00",  # too long
    b"\x00\x00\x00\x00\x00\x00\x00\x00",  # too long
])
def test_check_response_length_invalid(input):
    """
    Test if "check_response_length()" raises an ShdlcResponseError if the
    response length is wrong.
    """
    cmd = ShdlcCmdGetErrorState(clear=False)
    with pytest.raises(ShdlcResponseError):
        cmd.check_response_length(input)


@pytest.mark.parametrize("input,expected_state,expected_last_error", [
    pytest.param(b"\x00\x00\x00\x00\x00", 0x00000000, 0x00, id="all_zeros"),
    pytest.param(b"\x00\x01\x02\x03\x04", 0x00010203, 0x04, id="incrementing"),
    pytest.param(b"\xFF\xFF\xFF\xFF\xFF", 0xFFFFFFFF, 0xFF, id="all_0xFF"),
])
def test_interpret_response(input, expected_state, expected_last_error):
    """
    Test if the return value and type of the "interpret_response()" method is
    correct.
    """
    cmd = ShdlcCmdGetErrorState(clear=False)
    cmd.check_response_length(input)
    state, last_error = cmd.interpret_response(input)
    assert type(state) is type(expected_state)
    assert type(last_error) is type(expected_last_error)
    assert state == expected_state
    assert last_error == expected_last_error
