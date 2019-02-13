# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from ..command import ShdlcCommand
from struct import pack, unpack

import logging
log = logging.getLogger(__name__)


class ShdlcCmdBaudrateBase(ShdlcCommand):
    """
    SHDLC command 0x91: "Get/Set Baudrate".
    """

    def __init__(self, *args, **kwargs):
        super(ShdlcCmdBaudrateBase, self).__init__(0x91, *args, **kwargs)


class ShdlcCmdSetBaudrate(ShdlcCmdBaudrateBase):
    def __init__(self, baudrate):
        super(ShdlcCmdSetBaudrate, self).__init__(
            data=pack(">I", baudrate), max_response_time=0.05,
            min_response_length=0, max_response_length=0
        )


class ShdlcCmdGetBaudrate(ShdlcCmdBaudrateBase):
    def __init__(self):
        super(ShdlcCmdGetBaudrate, self).__init__(
            data=[], max_response_time=0.05,
            min_response_length=4, max_response_length=4
        )

    def interpret_response(self, data):
        """
        :return int: Baudrate [bit/s].
        """
        return int(unpack(">I", data)[0])
