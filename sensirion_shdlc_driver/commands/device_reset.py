# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from ..command import ShdlcCommand

import logging
log = logging.getLogger(__name__)


class ShdlcCmdDeviceResetBase(ShdlcCommand):
    """
    SHDLC command 0xD3: "Device Reset".
    """

    def __init__(self, *args, **kwargs):
        super(ShdlcCmdDeviceResetBase, self).__init__(0xD3, *args, **kwargs)


class ShdlcCmdDeviceReset(ShdlcCmdDeviceResetBase):
    def __init__(self):
        super(ShdlcCmdDeviceReset, self).__init__(
            data=[], max_response_time=0.5, max_response_length=0,
            post_processing_time=2.0
        )
