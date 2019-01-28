# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function, unicode_literals
from sensirion_shdlc_driver.types import ProtocolVersion
import pytest


@pytest.mark.parametrize("major,minor,expected_str", [
    pytest.param(0, 0, "0.0", id="0.0"),
    pytest.param(13, 37, "13.37", id="13.37"),
    pytest.param(255, 255, "255.255", id="255.255"),
])
def test_str(major, minor, expected_str):
    """
    Test if the value and type of the "__str__()" method is correct.
    """
    version = ProtocolVersion(major=major, minor=minor)
    version_str = str(version)
    assert type(version_str) is str
    assert version_str == expected_str
