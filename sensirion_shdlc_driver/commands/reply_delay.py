# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from ..command import ShdlcCommand
from struct import pack, unpack

import logging
log = logging.getLogger(__name__)


class ShdlcCmdReplyDelayBase(ShdlcCommand):
    """
    SHDLC command 0x95: "Get/Set Reply Delay".
    """

    def __init__(self, *args, **kwargs):
        super(ShdlcCmdReplyDelayBase, self).__init__(0x95, *args, **kwargs)


class ShdlcCmdSetReplyDelay(ShdlcCmdReplyDelayBase):
    def __init__(self, reply_delay):
        super(ShdlcCmdSetReplyDelay, self).__init__(
            data=pack(">H", reply_delay), max_response_time=0.05,
            min_response_length=0, max_response_length=0
        )


class ShdlcCmdGetReplyDelay(ShdlcCmdReplyDelayBase):
    def __init__(self):
        super(ShdlcCmdGetReplyDelay, self).__init__(
            data=[], max_response_time=0.05,
            min_response_length=2, max_response_length=2
        )

    def interpret_response(self, data):
        """
        :return byte: Reply delay [μs].
        """
        return int(unpack(">H", data)[0])
