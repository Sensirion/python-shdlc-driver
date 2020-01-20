# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .errors import ShdlcResponseError

import logging
log = logging.getLogger(__name__)


class ShdlcCommand(object):
    """
    Base class for all SHDLC commands.
    """

    def __init__(self, id, data, max_response_time,
                 min_response_length=0, max_response_length=255,
                 post_processing_time=0.0):
        """
        Constructor.

        :param byte id:  Command ID (0..255).
        :param bytes-like/list data: MOSI data (0..255 bytes).
        :param float max_response_time: Maximum time the device needs to
                                        response (used as timeout).
        :param byte min_response_length: Minimum expected response length.
        :param byte max_response_length: Maximum expected response length.
        :param float post_processing_time: Maximum time in seconds the device
                                           needs for post processing
                                           (typically 0.0s).
        """
        super(ShdlcCommand, self).__init__()
        self._id = id
        self._data = bytes(bytearray(data))  # Allow arbitrary iterables
        self._max_response_time = max_response_time
        self._min_rx_len = min_response_length
        self._max_rx_len = max_response_length
        self._post_processing_time = post_processing_time

    @property
    def id(self):
        """
        Get the command ID.

        :return: Command ID (0..255).
        :rtype: byte
        """
        return self._id

    @property
    def data(self):
        """
        Get the command data (payload).

        :return: Command data (length 0..255).
        :rtype: bytes
        """
        return self._data

    @property
    def max_response_time(self):
        """
        Get the maximum response time for this command.

        :return: Maximum response time in seconds.
        :rtype: float
        """
        return self._max_response_time

    @property
    def post_processing_time(self):
        """
        Get the post processing time for this command. The post processing time
        defines how long a device needs to execute a command *after* responding
        to the SHDLC command. Most devices don't need post processing (command
        is executed *before* the response is sent). Only special commands (e.g.
        a device reset) are executed after the response is sent.

        :return: Maximum response time in seconds.
        :rtype: float
        """
        return self._post_processing_time

    def check_response_length(self, data):
        """
        Check if the response length is correct.

        :param bytes data: Raw data (payload) received from the device.
        :raise ~sensirion_shdlc_driver.errors.ShdlcResponseError:
            If length is wrong.
        """
        if not (self._min_rx_len <= len(data) <= self._max_rx_len):
            raise ShdlcResponseError(
                "Wrong response length (expected {}..{} bytes, got {})."
                .format(self._min_rx_len, self._max_rx_len, len(data)), data)

    def interpret_response(self, data):
        """
        Interpret the response to this command received from the device. This
        converts the raw byte array to the actual data type(s) depending on the
        sent command.

        :param bytes data: Raw data (payload) received from the device.
        :return: Interpreted response. Data type and meaning depends on the
                 sent command. None for commands without response data. See the
                 actual command implementation for details.
        """
        return data if len(data) > 0 else None
