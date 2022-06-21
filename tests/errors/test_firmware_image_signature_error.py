# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.errors import ShdlcFirmwareImageSignatureError


def test_message():
    """
    Test if the message is a non-empty string.
    """
    err = ShdlcFirmwareImageSignatureError(signature=b'\x12\x34\x56\x78')
    msg = str(err)
    assert len(msg) > 0
