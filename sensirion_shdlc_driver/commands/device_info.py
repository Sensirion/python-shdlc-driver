# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from ..command import ShdlcCommand

import logging
log = logging.getLogger(__name__)


class ShdlcCmdDeviceInfoBase(ShdlcCommand):
    """
    SHDLC command 0xD0: "Device Information".
    """

    def __init__(self, *args, **kwargs):
        super(ShdlcCmdDeviceInfoBase, self).__init__(0xD0, *args, **kwargs)


class ShdlcCmdGetProductType(ShdlcCmdDeviceInfoBase):
    def __init__(self):
        super(ShdlcCmdGetProductType, self).__init__(
            data=[0x00], max_response_time=0.5
        )

    def interpret_response(self, data):
        return str(data.decode('utf-8').rstrip('\0'))


class ShdlcCmdGetProductName(ShdlcCmdDeviceInfoBase):
    def __init__(self):
        super(ShdlcCmdGetProductName, self).__init__(
            data=[0x01], max_response_time=0.5
        )

    def interpret_response(self, data):
        return str(data.decode('utf-8').rstrip('\0'))


class ShdlcCmdGetArticleCode(ShdlcCmdDeviceInfoBase):
    def __init__(self):
        super(ShdlcCmdGetArticleCode, self).__init__(
            data=[0x02], max_response_time=0.5
        )

    def interpret_response(self, data):
        return str(data.decode('utf-8').rstrip('\0'))


class ShdlcCmdGetSerialNumber(ShdlcCmdDeviceInfoBase):
    def __init__(self):
        super(ShdlcCmdGetSerialNumber, self).__init__(
            data=[0x03], max_response_time=0.5
        )

    def interpret_response(self, data):
        return str(data.decode('utf-8').rstrip('\0'))


class ShdlcCmdGetProductSubType(ShdlcCmdDeviceInfoBase):
    def __init__(self):
        super(ShdlcCmdGetProductSubType, self).__init__(
            data=[0x04], max_response_time=0.5,
            min_response_length=1, max_response_length=1
        )

    def interpret_response(self, data):
        data_bytes = bytearray(data)  # Make the [] operator returning a byte
        return data_bytes[0]
