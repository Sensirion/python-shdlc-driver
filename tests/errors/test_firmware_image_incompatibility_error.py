# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.errors import \
    ShdlcFirmwareImageIncompatibilityError


def test_message():
    """
    Test if the message is a non-empty string.
    """
    err = ShdlcFirmwareImageIncompatibilityError(image_type=13, device_type=37)
    msg = str(err)
    assert len(msg) > 0
