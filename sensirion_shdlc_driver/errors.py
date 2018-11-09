# -*- coding: utf-8 -*-
"""
(c) Copyright 2019 Sensirion AG, Switzerland
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
log = logging.getLogger(__name__)


class ShdlcError(Exception):
    """
    Base class for all SHDLC related exceptions.
    """
    pass


class ShdlcTimeoutError(ShdlcError):
    """
    SHDLC timeout exception (device did not respond to command).
    """
    def __init__(self):
        super(ShdlcTimeoutError, self).__init__(
            "Timeout while waiting for response from SHDLC device. "
            "Check connection to device and make sure it is powered on."
        )


class ShdlcResponseError(ShdlcError):
    """
    SHDLC response error (slave response contains invalid data)
    """
    def __init__(self, message, received_data=None):
        """
        Constructor.

        :param string message: Error message.
        :param received_data: The received (invalid) raw data.
        """
        super(ShdlcResponseError, self).__init__(
            "Invalid data received from the SHDLC device: " + message
        )
        if received_data:
            self._received_data = bytes(bytearray(received_data))
            log.debug("Invalid SHDLC response raw data: [{}]".format(
                ", ".join(["0x%.2X" % i for i in self._received_data])))

    @property
    def received_data(self):
        """
        Get the (invalid) raw data which was received from the device.

        :return: The raw data received from the device.
        :rtype: bytes
        """
        return self._received_data
