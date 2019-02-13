# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from ..command import ShdlcCommand
from struct import unpack

import logging
log = logging.getLogger(__name__)


class ShdlcCmdErrorStateBase(ShdlcCommand):
    """
    SHDLC command 0xD2: "Device Error State".
    """

    def __init__(self, *args, **kwargs):
        super(ShdlcCmdErrorStateBase, self).__init__(0xD2, *args, **kwargs)


class ShdlcCmdGetErrorState(ShdlcCmdErrorStateBase):
    def __init__(self, clear):
        super(ShdlcCmdGetErrorState, self).__init__(
            data=[0x01 if clear else 0x00], max_response_time=0.5,
            min_response_length=5, max_response_length=5
        )

    def interpret_response(self, data):
        """
        :return int, byte: Device state (32 flags as integer) and the last
                           error (byte) which occurred on the device.
        """
        device_state, last_error = unpack('>IB', data)
        return device_state, last_error
