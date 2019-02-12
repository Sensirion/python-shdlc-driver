# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function, unicode_literals
from sensirion_shdlc_driver.errors import ShdlcResponseError
import pytest


def test_message():
    """
    Test if the message is a non-empty string.
    """
    err = ShdlcResponseError(message="Foo")
    msg = str(err)
    assert len(msg) > 0


@pytest.mark.parametrize("input, output", [
    pytest.param(None, None, id="none"),
    pytest.param(b"", b"", id="bytes_empty"),
    pytest.param(b"\x00\xFF", b"\x00\xFF", id="bytes_nonempty"),
    pytest.param(bytearray([]), b"", id="bytearray_empty"),
    pytest.param(bytearray([0x00, 0xFF]), b"\x00\xFF", id="bytearray_nonempty"),
    pytest.param([], b"", id="list_empty"),
    pytest.param([0x00, 0xFF], b"\x00\xFF", id="list_nonempty"),
])
def test_received_data(input, output):
    """
    Test if the type and value of the "received_data" is correct.
    """
    err = ShdlcResponseError(message="Foo", received_data=input)
    received_data = err.received_data
    assert type(received_data) is type(output)
    assert err.received_data == output
