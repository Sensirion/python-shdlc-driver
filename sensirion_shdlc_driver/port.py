# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function, unicode_literals
from .errors import ShdlcTimeoutError, ShdlcResponseError
from threading import Lock
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

    def transceive(self, slave_address, command, data, response_timeout):
        """
        Send SHDLC frame to port and return received response frame.

        :param byte slave_address: Slave address.
        :param byte command: SHDLC command ID.
        :param bytes-like data: Payload.
        :param float response_timeout: Response timeout in seconds (maximum
                                       time until the first byte is received).
        :return: Received address, command, state, and payload.
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

    _START_STOP_BYTE = 0x7E
    _ESCAPE_BYTE = 0x7D
    _ESCAPE_XOR = 0x20
    _CHARS_TO_ESCAPE = [_START_STOP_BYTE, _ESCAPE_BYTE, 0x11, 0x13]
    _MAX_RAW_FRAME_LENGTH = 516  # All bytes stuffed

    def __init__(self, port, baudrate):
        """
        Open the serial port. Throws an exception if the port cannot be opened.

        :param string port: The serial port (e.g. "COM2" or "/dev/ttyUSB0")
        :param int baudrate: The baudrate in bit/s.
        """
        super(ShdlcSerialPort, self).__init__()
        log.debug("Open ShdlcSerialPort on '{}' with {} bit/s."
                  .format(port, baudrate))
        self._lock = Lock()
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

    def transceive(self, slave_address, command, data, response_timeout):
        """
        Send SHDLC frame to port and return received response frame.

        :param byte slave_address: Slave address.
        :param byte command: SHDLC command ID.
        :param bytes-like data: Payload.
        :param float response_timeout: Response timeout in seconds (maximum
                                       time until the first byte is received).
        :return: Received address, command, state, and payload.
        :rtype: byte, byte, byte, bytes
        :raise ShdlcTimeoutError: If no response received within timeout.
        :raise ShdlcResponseError: If the received response is invalid.
        """
        with self._lock:
            self._serial.flushInput()
            self._set_timeout(response_timeout)
            self._send_frame(slave_address, command, data)
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

    def _send_frame(self, slave_address, command, data):
        """
        Send a frame to the serial port.

        :param byte slave_address: Slave address.
        :param byte command: SHDLC command ID.
        :param bytes-like data: Payload.
        """
        raw_tx_frame = bytearray([slave_address, command, len(data)])
        raw_tx_frame.extend(bytearray(data))
        tx_data = bytearray()
        tx_data.append(self._START_STOP_BYTE)
        tx_data.extend(self._stuff_data_bytes(raw_tx_frame))
        tx_data.append(self._calculate_checksum(raw_tx_frame))
        tx_data.append(self._START_STOP_BYTE)
        log.debug("ShdlcSerialPort send raw: [{}]"
                  .format(", ".join(["0x%.2X" % i for i in tx_data])))
        self._serial.write(tx_data)

    def _receive_frame(self):
        """
        Wait for the response frame and return it.

        :return: Received address, command, state, and payload.
        :rtype: byte, byte, byte, bytes
        """
        data = bytearray()
        while True:
            # Fetch all received bytes at once (to get maximum performance) or
            # wait for at least one byte (with timeout) if the buffer is empty.
            new_data = self._serial.read(max(self._serial.inWaiting(), 1))
            if len(new_data) == 0:
                raise ShdlcTimeoutError()
            data.extend(new_data)
            if data.count(bytearray([self._START_STOP_BYTE])) >= 2:
                log.debug("ShdlcSerialPort received raw: [{}]"
                          .format(", ".join(["0x%.2X" % i for i in data])))
                return self._build_rx_frame(data)
            elif len(data) > self._MAX_RAW_FRAME_LENGTH:
                # Abort condition in case we are receiving endless rubbish.
                raise ShdlcResponseError("Response is too long.", data)

    @staticmethod
    def _build_rx_frame(raw_rx_data):
        """
        Interpret and validate received raw data and return it.

        :param bytearray raw_rx_data: The received (stuffed) raw data.
        :return: Received address, command, state, and payload.
        :rtype: byte, byte, byte, bytes
        """
        separator = bytearray([ShdlcSerialPort._START_STOP_BYTE])
        stuffed = raw_rx_data.split(separator)[1]
        unstuffed = ShdlcSerialPort._unstuff_data_bytes(stuffed)
        if len(unstuffed) < 5:
            raise ShdlcResponseError("Response is too short.", raw_rx_data)
        frame = unstuffed[:-1]
        address = frame[0]
        command = frame[1]
        state = frame[2]
        length = frame[3]
        data = frame[4:]
        checksum = unstuffed[-1]
        if checksum != ShdlcSerialPort._calculate_checksum(frame):
            raise ShdlcResponseError("Wrong checksum.", raw_rx_data)
        if length != len(data):
            raise ShdlcResponseError("Wrong length.", data)
        return int(address), int(command), int(state), bytes(data)

    @staticmethod
    def _stuff_data_bytes(data):
        """
        Perform byte-stuffing (escape reserved bytes).

        :param bytearray data: The data without stuffed bytes.
        :return: The data with stuffed bytes.
        :rtype: bytearray
        """
        result = bytearray()
        for b in data:
            if b in ShdlcSerialPort._CHARS_TO_ESCAPE:
                result.append(ShdlcSerialPort._ESCAPE_BYTE)
                result.append(b ^ ShdlcSerialPort._ESCAPE_XOR)
            else:
                result.append(b)
        return result

    @staticmethod
    def _unstuff_data_bytes(stuffed_data):
        """
        Undo byte-stuffing (replacing stuffed bytes by their original value).

        :param bytearray stuffed_data: The data with stuffed bytes.
        :return: The data without stuffed bytes.
        :rtype: bytearray
        """
        data = bytearray()
        xor = 0x00
        for i in range(0, len(stuffed_data)):
            if stuffed_data[i] == ShdlcSerialPort._ESCAPE_BYTE:
                xor = ShdlcSerialPort._ESCAPE_XOR
            else:
                data.append(stuffed_data[i] ^ xor)
                xor = 0x00
        return data

    @staticmethod
    def _calculate_checksum(frame):
        """
        Calculate the checksum for a frame.

        :param bytearray frame: Input frame.
        :return: Calculated checksum.
        :rtype: byte
        """
        return ~sum(frame) & 0xFF
