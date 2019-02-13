# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from ..command import ShdlcCommand
from struct import unpack

import logging
log = logging.getLogger(__name__)


class ShdlcCmdSystemUpTimeBase(ShdlcCommand):
    """
    SHDLC command 0x93: "System Up Time".
    """

    def __init__(self, *args, **kwargs):
        super(ShdlcCmdSystemUpTimeBase, self).__init__(0x93, *args, **kwargs)


class ShdlcCmdGetSystemUpTime(ShdlcCmdSystemUpTimeBase):
    def __init__(self):
        super(ShdlcCmdGetSystemUpTime, self).__init__(
            data=[], max_response_time=0.05,
            min_response_length=4, max_response_length=4
        )

    def interpret_response(self, data):
        """
        :return int: System up time [s].
        """
        return unpack('>I', data)[0]
