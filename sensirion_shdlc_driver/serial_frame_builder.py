# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .errors import ShdlcResponseError

import logging
log = logging.getLogger(__name__)


class ShdlcSerialFrameBuilder(object):
    """
    Base class for
    :py:class:`~sensirion_shdlc_driver.serial_frame_builder.ShdlcSerialMosiFrameBuilder`
    and
    :py:class:`~sensirion_shdlc_driver.serial_frame_builder.ShdlcSerialMisoFrameBuilder`.
    """

    _START_STOP_BYTE = 0x7E
    _ESCAPE_BYTE = 0x7D
    _ESCAPE_XOR = 0x20
    _CHARS_TO_ESCAPE = [_START_STOP_BYTE, _ESCAPE_BYTE, 0x11, 0x13]

    # Maximum raw frame length when all bytes are stuffed:
    # START + 2 * (ADDRESS + COMMAND + STATE + LENGTH + DATA + CHECKSUM) + STOP
    # = 1 + 2 * (1 + 1 + 1 + 1 + 255 + 1) + 1
    # = 522
    _MAX_RAW_FRAME_LENGTH = 522

    def __init__(self):
        """
        Constructor.
        """
        super(ShdlcSerialFrameBuilder, self).__init__()

    @staticmethod
    def _calculate_checksum(frame):
        """
        Calculate the checksum for a frame.

        :param bytearray frame: Input frame.
        :return: Calculated checksum.
        :rtype: byte
        """
        return ~sum(frame) & 0xFF


class ShdlcSerialMosiFrameBuilder(ShdlcSerialFrameBuilder):
    """
    Serial MOSI (master out, slave in) frame builder.

    This class allows to convert structured data (slave address, command ID
    etc.) into the raw bytes which are then sent to the serial port.
    """

    def __init__(self, slave_address, command_id, data):
        """
        Constructor.

        :param byte slave_address: Slave address.
        :param byte command_id: Command ID.
        :param bytes-like data: Payload (can be empty).
        """
        super(ShdlcSerialMosiFrameBuilder, self).__init__()
        self._slave_address = int(slave_address)
        self._command_id = int(command_id)
        self._data = bytes(bytearray(data))  # Allow arbitrary iterables

    def to_bytes(self):
        """
        Convert the structured data from the constructor to raw bytes.

        :return: The raw data which can be sent to the serial port.
        :rtype: bytes
        """
        frame_content = bytearray([self._slave_address, self._command_id,
                                   len(self._data)]) + bytearray(self._data)
        frame_content.append(self._calculate_checksum(frame_content))
        raw_frame = bytearray()
        raw_frame.append(self._START_STOP_BYTE)
        raw_frame.extend(self._stuff_data_bytes(frame_content))
        raw_frame.append(self._START_STOP_BYTE)
        return bytes(raw_frame)

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
            if b in ShdlcSerialFrameBuilder._CHARS_TO_ESCAPE:
                result.append(ShdlcSerialFrameBuilder._ESCAPE_BYTE)
                result.append(b ^ ShdlcSerialFrameBuilder._ESCAPE_XOR)
            else:
                result.append(b)
        return result


class ShdlcSerialMisoFrameBuilder(ShdlcSerialFrameBuilder):
    """
    Serial MISO (master in, slave sout) frame builder.

    This class allows to convert raw bytes received from the serial port into
    structured data (slave address, command ID etc.).
    """

    def __init__(self):
        """
        Constructor.
        """
        super(ShdlcSerialMisoFrameBuilder, self).__init__()
        self._data = bytearray()

    @property
    def data(self):
        """
        Get the received data.

        :return: The received data.
        :rtype: bytearray
        """
        return self._data

    @property
    def start_received(self):
        """
        Check if the start byte was already received.

        :return: Whether the start byte was already received or not.
        :rtype: bool
        """
        return self._START_STOP_BYTE in self._data

    def add_data(self, data):
        """
        Add more data (received from the serial port) and check if a complete
        frame is received.

        :param bytes-like data: The bytes received from the serial port.
        :return: Whether the received data contains a complete frame or not.
        :rtype: bool
        """
        self._data.extend(bytearray(data))

        if self._data.count(bytearray([self._START_STOP_BYTE])) >= 2:
            # Complete frame received.
            return True
        elif len(self._data) > self._MAX_RAW_FRAME_LENGTH:
            # Abort condition in case we are receiving endless rubbish.
            raise ShdlcResponseError("Response is too long.", self._data)
        else:
            # Frame is incomplete.
            return False

    def interpret_data(self):
        """
        Interpret and validate received raw data and return it.

        :return: Received address, command_id, state, and payload.
        :rtype: byte, byte, byte, bytes
        """
        separator = bytearray([self._START_STOP_BYTE])
        stuffed = self._data.split(separator)[1]
        unstuffed = self._unstuff_data_bytes(stuffed)
        if len(unstuffed) < 5:
            raise ShdlcResponseError("Response is too short.", self._data)
        frame = unstuffed[:-1]
        address = int(frame[0])
        command_id = int(frame[1])
        state = int(frame[2])
        length = int(frame[3])
        data = bytes(frame[4:])
        checksum = int(unstuffed[-1])
        if length != len(data):
            raise ShdlcResponseError("Wrong length.", self._data)
        if checksum != self._calculate_checksum(frame):
            raise ShdlcResponseError("Wrong checksum.", self._data)
        return address, command_id, state, data

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
            if stuffed_data[i] == ShdlcSerialFrameBuilder._ESCAPE_BYTE:
                xor = ShdlcSerialFrameBuilder._ESCAPE_XOR
            else:
                data.append(stuffed_data[i] ^ xor)
                xor = 0x00
        return data
