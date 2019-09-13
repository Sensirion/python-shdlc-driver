# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .errors import ShdlcTimeoutError
from .serial_frame_builder import ShdlcSerialMosiFrameBuilder, \
    ShdlcSerialMisoFrameBuilder
from threading import RLock
import serial

import logging
log = logging.getLogger(__name__)


class ShdlcPort(object):
    """
    Common interface for all communication ports for transceiving SHDLC frames.

    Concrete implementations may use the serial port or another interface for
    transceiving SHDLC frames. All methods must be implemented thread-safe,
    i.e. allowing them to be called from multiple threads at the same time.
    """

    @property
    def description(self):
        """
        Get a description of the port.

        :return: Description string.
        :rtype: string
        """
        raise NotImplementedError()

    @property
    def bitrate(self):
        """
        Get the current bitrate.

        :return: Bitrate in bit/s.
        :rtype: int
        """
        raise NotImplementedError()

    @bitrate.setter
    def bitrate(self, bitrate):
        """
        Set the bitrate.

        :param int bitrate: Bitrate in bit/s.
        """
        raise NotImplementedError()

    @property
    def lock(self):
        """
        Get the lock object of the port to allow locking it, i.e. to get
        exclusive access across multiple method calls.

        :return: The lock object.
        :rtype: threading.RLock
        """
        raise NotImplementedError()

    def transceive(self, slave_address, command_id, data, response_timeout):
        """
        Send SHDLC frame to port and return received response frame.

        :param byte slave_address: Slave address.
        :param byte command_id: SHDLC command ID.
        :param bytes-like data: Payload.
        :param float response_timeout: Response timeout in seconds (maximum
                                       time until the first byte is received).
        :return: Received address, command_id, state, and payload.
        :rtype: byte, byte, byte, bytes
        :raise ShdlcTimeoutError: If no response received within timeout.
        :raise ShdlcResponseError: If the received response is invalid.
        """
        raise NotImplementedError()


class ShdlcSerialPort(ShdlcPort):
    """
    SHDLC transceiver for the serial port (e.g. UART/RS232/RS485).

    This class implements the ShdlcPort interface for the serial port.

    .. note:: This class can be used in a "with"-statement, and it's
              recommended to do so as it automatically closes the port after
              using it.
    """

    def __init__(self, port, baudrate):
        """
        Open the serial port. Throws an exception if the port cannot be opened.

        :param string port: The serial port (e.g. "COM2" or "/dev/ttyUSB0")
        :param int baudrate: The baudrate in bit/s.
        """
        super(ShdlcSerialPort, self).__init__()
        log.debug("Open ShdlcSerialPort on '{}' with {} bit/s."
                  .format(port, baudrate))
        self._lock = RLock()
        self._serial = serial.Serial(port=port, baudrate=baudrate,
                                     bytesize=serial.EIGHTBITS,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=1.0, xonxoff=False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._serial.close()

    @property
    def description(self):
        """
        Get a description of the port.

        :return: Description string.
        :rtype: string
        """
        with self._lock:
            return self._serial.name + '@' + str(self._serial.baudrate)

    @property
    def bitrate(self):
        """
        Get the current bitrate.

        :return: Bitrate in bit/s.
        :rtype: int
        """
        with self._lock:
            return self._serial.baudrate

    @bitrate.setter
    def bitrate(self, bitrate):
        """
        Set the bitrate.

        :param int bitrate: Bitrate in bit/s.
        """
        with self._lock:
            self._serial.baudrate = bitrate

    @property
    def lock(self):
        """
        Get the lock object of the port to allow locking it, i.e. to get
        exclusive access across multiple method calls.

        :return: The lock object.
        :rtype: threading.RLock
        """
        return self._lock

    def transceive(self, slave_address, command_id, data, response_timeout):
        """
        Send SHDLC frame to port and return received response frame.

        :param byte slave_address: Slave address.
        :param byte command_id: SHDLC command ID.
        :param bytes-like data: Payload.
        :param float response_timeout: Response timeout in seconds (maximum
                                       time until the first byte is received).
        :return: Received address, command_id, state, and payload.
        :rtype: byte, byte, byte, bytes
        :raise ShdlcTimeoutError: If no response received within timeout.
        :raise ShdlcResponseError: If the received response is invalid.
        """
        with self._lock:
            self._serial.flushInput()
            self._set_timeout(response_timeout)
            self._send_frame(slave_address, command_id, data)
            self._serial.flush()
            return self._receive_frame()

    def close(self):
        """
        Close (release) the serial port.
        """
        self._serial.close()

    def _set_timeout(self, timeout):
        """
        Set the timeout of the serial port.

        :param float timeout: The new timeout in seconds.
        """
        # Only change timeout if needed because at least under Windows
        # it leads to strange errors when writing it too often.
        if self._serial.timeout != timeout:
            self._serial.timeout = timeout

    def _send_frame(self, slave_address, command_id, data):
        """
        Send a frame to the serial port.

        :param byte slave_address: Slave address.
        :param byte command_id: SHDLC command ID.
        :param bytes-like data: Payload.
        """
        builder = ShdlcSerialMosiFrameBuilder(slave_address, command_id, data)
        tx_data = builder.to_bytes()
        log.debug("ShdlcSerialPort send raw: [{}]".format(
                  ", ".join(["0x%.2X" % i for i in bytearray(tx_data)])))
        self._serial.write(tx_data)

    def _receive_frame(self):
        """
        Wait for the response frame and return it.

        :return: Received address, command_id, state, and payload.
        :rtype: byte, byte, byte, bytes
        """
        builder = ShdlcSerialMisoFrameBuilder()
        while True:
            # Fetch all received bytes at once (to get maximum performance) or
            # wait for at least one byte (with timeout) if the buffer is empty.
            new_data = self._serial.read(max(self._serial.inWaiting(), 1))
            if len(new_data) == 0:
                raise ShdlcTimeoutError()
            if builder.add_data(new_data):
                log.debug("ShdlcSerialPort received raw: [{}]".format(
                          ", ".join(["0x%.2X" % i for i in builder.data])))
                return builder.interpret_data()
