# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from ..command import ShdlcCommand

import logging
log = logging.getLogger(__name__)


class ShdlcCmdSlaveAddressBase(ShdlcCommand):
    """
    SHDLC command 0x90: "Get/Set Slave Address".
    """

    def __init__(self, *args, **kwargs):
        super(ShdlcCmdSlaveAddressBase, self).__init__(0x90, *args, **kwargs)


class ShdlcCmdSetSlaveAddress(ShdlcCmdSlaveAddressBase):
    def __init__(self, slave_address):
        super(ShdlcCmdSetSlaveAddress, self).__init__(
            data=[int(slave_address)], max_response_time=0.05,
            min_response_length=0, max_response_length=0
        )


class ShdlcCmdGetSlaveAddress(ShdlcCmdSlaveAddressBase):
    def __init__(self):
        super(ShdlcCmdGetSlaveAddress, self).__init__(
            data=[], max_response_time=0.05,
            min_response_length=1, max_response_length=1
        )

    def interpret_response(self, data):
        """
        :return byte: Slave address.
        """
        data_bytes = bytearray(data)  # Make the [] operator returning a byte
        return int(data_bytes[0])
