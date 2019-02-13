# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.types import FirmwareVersion
import pytest


@pytest.mark.parametrize("major,minor,debug,expected_str", [
    pytest.param(0, 0, False, "0.0", id="0.0"),
    pytest.param(255, 255, False, "255.255", id="255.255"),
    pytest.param(0, 0, True, "0.0-debug", id="0.0-debug"),
    pytest.param(13, 37, True, "13.37-debug", id="13.37-debug"),
])
def test_str(major, minor, debug, expected_str):
    """
    Test if the value and type of the "__str__()" method is correct.
    """
    version = FirmwareVersion(major=major, minor=minor, debug=debug)
    version_str = str(version)
    assert type(version_str) is str
    assert version_str == expected_str
