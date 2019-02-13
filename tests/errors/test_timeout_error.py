# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.errors import ShdlcTimeoutError


def test_message():
    """
    Test if the message is a non-empty string.
    """
    err = ShdlcTimeoutError()
    msg = str(err)
    assert len(msg) > 0
