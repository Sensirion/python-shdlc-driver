# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from ..command import ShdlcCommand

import logging
log = logging.getLogger(__name__)


class ShdlcCmdFactoryResetBase(ShdlcCommand):
    """
    SHDLC command 0x92: "Factory Reset".
    """

    def __init__(self, *args, **kwargs):
        super(ShdlcCmdFactoryResetBase, self).__init__(0x92, *args, **kwargs)


class ShdlcCmdFactoryReset(ShdlcCmdFactoryResetBase):
    def __init__(self):
        super(ShdlcCmdFactoryReset, self).__init__(
            data=[], max_response_time=2.0, max_response_length=0,
            post_processing_time=2.0
        )
