# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from ..command import ShdlcCommand
from ..types import FirmwareVersion, HardwareVersion, ProtocolVersion, Version

import logging
log = logging.getLogger(__name__)


class ShdlcCmdDeviceVersionBase(ShdlcCommand):
    """
    SHDLC command 0xD1: "Get Version".
    """

    def __init__(self, *args, **kwargs):
        super(ShdlcCmdDeviceVersionBase, self).__init__(0xD1, *args, **kwargs)


class ShdlcCmdGetVersion(ShdlcCmdDeviceVersionBase):
    def __init__(self):
        super(ShdlcCmdGetVersion, self).__init__(
            data=[], max_response_time=0.5,
            min_response_length=7, max_response_length=7
        )

    def interpret_response(self, data):
        data_bytes = bytearray(data)  # Make the [] operator returning a byte
        return Version(
            firmware=FirmwareVersion(
                major=data_bytes[0],
                minor=data_bytes[1],
                debug=bool(data_bytes[2])
            ),
            hardware=HardwareVersion(
                major=data_bytes[3],
                minor=data_bytes[4]
            ),
            protocol=ProtocolVersion(
                major=data_bytes[5],
                minor=data_bytes[6]
            )
        )
