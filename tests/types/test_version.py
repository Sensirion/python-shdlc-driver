# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.types import FirmwareVersion, HardwareVersion, \
    ProtocolVersion, Version
import pytest


@pytest.mark.parametrize("version,expected_str", [
    pytest.param(
        Version(
            firmware=FirmwareVersion(major=0, minor=0, debug=False),
            hardware=HardwareVersion(major=0, minor=0),
            protocol=ProtocolVersion(major=0, minor=0),
        ),
        "Firmware 0.0, Hardware 0.0, Protocol 0.0",
        id="zeros"
    ),
    pytest.param(
        Version(
            firmware=FirmwareVersion(major=1, minor=2, debug=True),
            hardware=HardwareVersion(major=3, minor=4),
            protocol=ProtocolVersion(major=5, minor=6),
        ),
        "Firmware 1.2-debug, Hardware 3.4, Protocol 5.6",
        id="incrementing"
    ),
])
def test_str(version, expected_str):
    """
    Test if the value and type of the "__str__()" method is correct.
    """
    version_str = str(version)
    assert type(version_str) is str
    assert version_str == expected_str
