# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .errors import ShdlcResponseError, ShdlcDeviceError
import time

import logging
log = logging.getLogger(__name__)


class ShdlcConnection(object):
    """
    This class represents the connection to an SHDLC bus. So you need to
    instantiate one object per bus, no matter how many devices are connected
    to that bus system.

    The basic functionality of the class is to send SHDLC frames to devices and
    receive their response. Handling of communication errors (e.g. timeout or
    checksum errors) and device errors is done in this class.
    """

    def __init__(self, port):
        """
        Open an SHDLC connection on a specific port.

        .. note:: This constructor does not send or receive any data to resp.
                  from the specified port.

        :param ~sensirion_shdlc_driver.port.ShdlcPort port:
            The port used for communication (must implement the
            :py:class:`~sensirion_shdlc_driver.port.ShdlcPort` interface)
        """
        super(ShdlcConnection, self).__init__()
        self._port = port
        log.debug("Opened ShdlcConnection on '{}'.".format(port.description))

    @property
    def port(self):
        """
        Get the underlying port.

        :return: An :py:class:`~sensirion_shdlc_driver.port.ShdlcPort` object.
        :rtype: ~sensirion_shdlc_driver.port.ShdlcPort
        """
        return self._port

    def execute(self, slave_address, command, wait_post_process=True):
        """
        Execute an ShdlcCommand and return the interpreted response. Executing
        a command means:

        - Send request (MOSI) frame
        - Receive response (MISO) frame
        - Validate and interpret response data
        - Wait until post processing is done (optional, and only if needed)

        :param byte slave_address:
            Slave address.
        :param ~sensirion_shdlc_driver.command.ShdlcCommand command:
            SHDLC command to execute.
        :param bool wait_post_process:
            If true and the command needs some time for post processing, this
            thread blocks until post processing is done.
        :return: Received response (interpreted) and error state flag.
        :rtype: object, bool
        """
        data, error = self.transceive(slave_address, command.id, command.data,
                                      command.max_response_time)
        if wait_post_process and command.post_processing_time > 0.0:
            # Wait for post processing in the device (to be sure the device is
            # ready for receiving the next command).
            time.sleep(command.post_processing_time)
        command.check_response_length(data)  # Raises if length was wrong
        return command.interpret_response(data), error

    def transceive(self, slave_address, command_id, data, response_timeout):
        """
        Send a raw SHDLC command and return the received raw response.

        :param byte slave_address: Slave address.
        :param byte command_id: SHDLC command ID.
        :param bytes-like data: Payload (may be empty).
        :param float response_timeout: Response timeout in seconds (maximum
                                       time until the first byte is received).
        :return: Received response payload and error state flag.
        :rtype: bytes, bool
        """
        rx_addr, rx_cmd, rx_state, rx_data = self._port.transceive(
            slave_address, command_id, data, response_timeout)
        if rx_addr != slave_address:
            raise ShdlcResponseError("Received slave address {} instead of {}."
                                     .format(rx_addr, slave_address))
        if rx_cmd != command_id:
            raise ShdlcResponseError("Received command ID 0x{:02X} instead of "
                                     "0x{:02X}.".format(rx_cmd, command_id))
        error_state = True if rx_state & 0x80 else False
        if error_state:
            log.warning("SHDLC device with address {} is in error state."
                        .format(slave_address))
        error_code = rx_state & 0x7F
        if error_code:
            log.warning("SHDLC device with address {} returned error {}."
                        .format(slave_address, error_code))
            raise ShdlcDeviceError(error_code)  # Command failed to execute
        return rx_data, error_state
