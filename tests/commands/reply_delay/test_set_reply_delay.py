# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function, unicode_literals
from sensirion_shdlc_driver.commands.reply_delay import ShdlcCmdSetReplyDelay
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_id():
    """
    Test if the value and type of the "id" property is correct.
    """
    cmd = ShdlcCmdSetReplyDelay(reply_delay=0)
    assert type(cmd.id) is int
    assert cmd.id == 0x95


@pytest.mark.parametrize("reply_delay,data", [
    pytest.param(0x0000, b"\x00\x00", id="0x0000"),
    pytest.param(0x1337, b"\x13\x37", id="0x1337"),
    pytest.param(0xFFFF, b"\xFF\xFF", id="0xFFFF"),
])
def test_data(reply_delay, data):
    """
    Test if the value and type of the "data" property is correct.
    """
    cmd = ShdlcCmdSetReplyDelay(reply_delay=reply_delay)
    assert type(cmd.data) is bytes
    assert cmd.data == data


def test_max_response_time():
    """
    Test if the value and type of the "max_response_time" property is correct.
    """
    cmd = ShdlcCmdSetReplyDelay(reply_delay=0x00)
    assert type(cmd.max_response_time) is float
    assert cmd.max_response_time == 0.05


def test_post_processing_time():
    """
    Test if the value and type of the "post_processing_time" property is
    correct.
    """
    cmd = ShdlcCmdSetReplyDelay(reply_delay=0x00)
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
    cmd = ShdlcCmdSetReplyDelay(reply_delay=0)
    with pytest.raises(ShdlcResponseError):
        cmd.check_response_length(input)


def test_interpret_response():
    """
    Test if the return value and type of the "interpret_response()" method is
    correct.
    """
    cmd = ShdlcCmdSetReplyDelay(reply_delay=0)
    cmd.check_response_length(b"")
    response = cmd.interpret_response(b"")
    assert response is None
