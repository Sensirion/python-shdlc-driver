# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from ..command import ShdlcCommand

import logging
log = logging.getLogger(__name__)


class ShdlcCmdBootloaderBase(ShdlcCommand):
    """
    SHDLC command 0xF3: "Bootloader".
    """

    def __init__(self, *args, **kwargs):
        super(ShdlcCmdBootloaderBase, self).__init__(0xF3, *args, **kwargs)


class ShdlcCmdEnterBootloader(ShdlcCmdBootloaderBase):
    def __init__(self):
        super(ShdlcCmdEnterBootloader, self).__init__(
            data=[], max_response_time=0.1,
            min_response_length=0, max_response_length=0,
            post_processing_time=2.0
        )


class ShdlcCmdFirmwareUpdateStart(ShdlcCmdBootloaderBase):
    def __init__(self):
        # This clears the flash on the device --> very high timeout is
        # required, let's use 20 seconds to be really safe.
        super(ShdlcCmdFirmwareUpdateStart, self).__init__(
            data=[0x01], max_response_time=20.0,
            min_response_length=0, max_response_length=0
        )


class ShdlcCmdFirmwareUpdateData(ShdlcCmdBootloaderBase):
    def __init__(self, data):
        super(ShdlcCmdFirmwareUpdateData, self).__init__(
            data=[0x02] + list(bytearray(data)), max_response_time=1.0,
            min_response_length=0, max_response_length=0
        )


class ShdlcCmdFirmwareUpdateStop(ShdlcCmdBootloaderBase):
    def __init__(self, checksum):
        super(ShdlcCmdFirmwareUpdateStop, self).__init__(
            data=[0x03, int(checksum)], max_response_time=1.0,
            min_response_length=0, max_response_length=0,
            post_processing_time=2.0
        )
