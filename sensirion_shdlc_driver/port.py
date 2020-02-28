# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .errors import ShdlcTimeoutError
from .serial_frame_builder import ShdlcSerialMosiFrameBuilder, \
    ShdlcSerialMisoFrameBuilder
from threading import RLock
import serial
import socket
import time

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
        The current bitrate in bit/s.

        :type: int
        """
        raise NotImplementedError()

    @bitrate.setter
    def bitrate(self, bitrate):
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

    @property
    def is_open(self):
        """
        Indicates whether the port is open.

        :return: If ``True`` the port is open, if ``False`` the port is closed.
        :rtype: bool
        """
        raise NotImplementedError()

    def open(self):
        """
        Open the port. Only needs to be called if the port is not already
        opened. Does nothing if the port is already opened.
        """
        raise NotImplementedError()

    def close(self):
        """
        Close the port to release the underlying resources. Does nothing if
        the port is already closed.
        """
        raise NotImplementedError()

    def transceive(self, slave_address, command_id, data, response_timeout):
        """
        Send SHDLC frame to port and return received response frame.

        .. note:: The specified response timeout defines the maximum time the
                  device needs until it starts to send the response after
                  receiving the last byte from the master request. The time
                  needed for the transmission itself and other possible
                  overhead or delays depends on hardware, drivers, bitrate etc.
                  and must be taken into account in the implementation of this
                  method.

        :param byte slave_address: Slave address.
        :param byte command_id: SHDLC command ID.
        :param bytes-like data: Payload.
        :param float response_timeout: Response timeout in seconds (maximum
                                       time until the first byte is received).
        :return: Received address, command_id, state, and payload.
        :rtype: byte, byte, byte, bytes
        :raise ~sensirion_shdlc_driver.errors.ShdlcTimeoutError:
            If no response received within timeout.
        :raise ~sensirion_shdlc_driver.errors.ShdlcResponseError:
            If the received response is invalid.
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

    def __init__(self, port, baudrate, additional_response_time=0.1,
                 do_open=True):
        """
        Create and optionally open a serial port. Throws an exception if the
        port cannot be opened.

        :param string port: The serial port (e.g. "COM2" or "/dev/ttyUSB0")
        :param int baudrate: The baudrate in bit/s.
        :param float additional_response_time: Additional response time (in
            Seconds) used when receiving frames. See property
            :py:attr:`~sensirion_shdlc_driver.port.ShdlcSerialPort.additional_response_time`
            for details. Defaults to 0.1 (i.e. 100ms) which should be enough
            in most cases.
        :param bool do_open:
            Whether the serial port should be opened immediately or not.
            If ``False``, you will have to call
            :py:meth:`~sensirion_shdlc_driver.port.ShdlcSerialPort.open`
            manually before using this object. Defaults to ``True``.
        """
        super(ShdlcSerialPort, self).__init__()
        log.debug("Open ShdlcSerialPort on '{}' with {} bit/s."
                  .format(port, baudrate))
        self._additional_response_time = float(additional_response_time)
        self._lock = RLock()
        self._serial = serial.Serial(port=None, baudrate=baudrate,
                                     bytesize=serial.EIGHTBITS,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=0.01, xonxoff=False)
        self._serial.port = port
        if do_open:
            self.open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

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
        The current bitrate in bit/s.

        :type: int
        """
        with self._lock:
            return self._serial.baudrate

    @bitrate.setter
    def bitrate(self, bitrate):
        with self._lock:
            self._serial.baudrate = bitrate

    @property
    def additional_response_time(self):
        """
        The additional response time (in Seconds) used when receiving frames.

        Since the timeout measurement of serial communication is typically
        very inaccurate (e.g. USB-UART converter drivers often buffer I/O
        data for 16ms), this class adds some extra time to the specified
        response timeout to avoid timeout errors even if the device responded
        within the given timeout. If needed, this extra time can be changed
        either with this property, or with the parameter
        ``additional_response_time`` of
        :py:meth:`~sensirion_shdlc_driver.port.ShdlcSerialPort.__init__`.

        :type: float
        """
        with self._lock:
            return self._additional_response_time

    @additional_response_time.setter
    def additional_response_time(self, additional_response_time):
        with self._lock:
            self._additional_response_time = float(additional_response_time)

    @property
    def lock(self):
        """
        Get the lock object of the port to allow locking it, i.e. to get
        exclusive access across multiple method calls.

        :return: The lock object.
        :rtype: threading.RLock
        """
        return self._lock

    @property
    def is_open(self):
        """
        Indicates whether the port is open.

        :return: If ``True`` the port is open, if ``False`` the port is closed.
        :rtype: bool
        """
        return self._serial.is_open

    def open(self):
        """
        Open the serial port (only needs to be called if ``do_open`` in
        :py:meth:`~sensirion_shdlc_driver.port.ShdlcSerialPort.__init__`
        was set to ``False``). Does nothing if the port is already opened.
        """
        if self._serial.is_open is False:
            self._serial.open()

    def close(self):
        """
        Close (release) the serial port. Does nothing if the port is already
        closed.
        """
        if self._serial.is_open is True:
            self._serial.close()

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
        :raise ~sensirion_shdlc_driver.errors.ShdlcTimeoutError:
            If no response received within timeout.
        :raise ~sensirion_shdlc_driver.errors.ShdlcResponseError:
            If the received response is invalid.
        """
        with self._lock:
            self._serial.flushInput()
            self._send_frame(slave_address, command_id, data)
            self._serial.flush()
            return self._receive_frame(response_timeout)

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

    def _receive_frame(self, response_timeout):
        """
        Wait for the response frame and return it.

        :param float response_timeout: Response timeout in seconds (maximum
                                       time until the first byte is received).
        :return: Received address, command_id, state, and payload.
        :rtype: byte, byte, byte, bytes
        """
        start_time = time.time()
        response_timeout += self._additional_response_time  # add extra time
        total_timeout = response_timeout + self._calculate_maximum_frame_time()
        builder = ShdlcSerialMisoFrameBuilder()
        while True:
            # Fetch all received bytes at once (to get maximum performance) or
            # wait for at least one byte (with timeout) if the buffer is empty.
            new_data = self._serial.read(max(self._serial.inWaiting(), 1))

            # Process received data and return if the frame is complete.
            if builder.add_data(new_data):
                log.debug("ShdlcSerialPort received raw: [{}]".format(
                          ", ".join(["0x%.2X" % i for i in builder.data])))
                return builder.interpret_data()

            # Frame not (completely) received yet, check timeout conditions.
            elapsed_time = time.time() - start_time
            timeout = \
                total_timeout if builder.start_received else response_timeout
            if elapsed_time > timeout:
                log.warning("ShdlcSerialPort timed out while waiting for "
                            "response after {:.0f} ms.".format(
                                elapsed_time * 1000.0))
                log.debug("ShdlcSerialPort received raw until timeout: [{}]"
                          .format(", ".join(["0x%.2X" % i
                                             for i in builder.data])))
                raise ShdlcTimeoutError()

    def _calculate_maximum_frame_time(self):
        """
        Calculate the time required for receiving the longest possible frame,
        respecting the used bitrate and with some extra time for inter-byte
        spaces etc.

        :return: Maximum frame time in Seconds
        :rtype: float
        """
        # Calculate theoretical transmission time of longest possible frame:
        #   600 bytes * (start bit + 8 data bits + stop bit) / bitrate
        max_frame_time = (600.0 * 10.0) / self.bitrate
        # Add 200ms extra, e.g. for inter-byte spaces.
        return max_frame_time + 0.2


class ShdlcTcpPort(ShdlcPort):
    """
    SHDLC transceiver for a TCP/IP port in client connection mode.

    This class implements the ShdlcPort interface for a client connection on a
    TCP/IP port.

    .. note:: This class can be used in a "with"-statement, and it's
              recommended to do so as it automatically closes the port after
              using it.
    """

    def __init__(self, ip, port, socket_timeout=5.0, do_open=True):
        """
        Create and optionally open a TCP socket. Throws an exception if the
        socket cannot be opened.

        :param string ip: The IP address (e.g. "192.168.100.200").
        :param int port: The TCP port.
        :param float socket_timeout: General TCP socket base timeout. Upon data
            transmission, the socket timeout is adjusted for each command, i.e.
            the timeout is increased with the parameter ``response_timeout`` of
            :py:meth:`~sensirion_shdlc_driver.port.ShdlcTcpPort.transceive`.
        :param bool do_open:
            Whether the port should be opened immediately or not. If ``False``,
            you will have to call
            :py:meth:`~sensirion_shdlc_driver.port.ShdlcTcpPort.open`
            manually before using this object. Defaults to ``True``.
        """
        super(ShdlcTcpPort, self).__init__()
        log.debug("Open ShdlcTcpPort as TCP client to '{}' on port {}."
                  .format(ip, port))
        self._ip = str(ip)
        self._port = int(port)
        self._socket_timeout = float(socket_timeout)
        self._is_open = False
        self._lock = RLock()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._socket_timeout)
        if do_open:
            self.open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def description(self):
        """
        Get the description of the TCP socket (address and port).

        :return: Description string.
        :rtype: string
        """
        with self._lock:
            return '{}:{}'.format(self._ip, self._port)

    @property
    def socket_timeout(self):
        """
        The base timeout of the TCP socket (in seconds) during transmission.

        The actual socket timeout is adjusted for each command. There are
        commands (e.g. flash erase) which require several seconds to be
        successfully executed. Therefore, the actual socket timeout value
        is calculated by the sum of the base timeout, plus the parameter
        ``response_timeout`` of
        :py:meth:`~sensirion_shdlc_driver.port.ShdlcTcpPort.transceive`.

        :type: float
        """
        with self._lock:
            return self._socket_timeout

    @socket_timeout.setter
    def socket_timeout(self, socket_timeout):
        with self._lock:
            self._socket_timeout = float(socket_timeout)

    @property
    def lock(self):
        """
        Get the lock object of the port to allow locking it, i.e. to get
        exclusive access across multiple method calls.

        :return: The lock object.
        :rtype: threading.RLock
        """
        return self._lock

    @property
    def is_open(self):
        """
        Indicates whether the port is open.

        :return: If ``True`` the port is open, if ``False`` the port is closed.
        :rtype: bool
        """
        return self._is_open

    def open(self):
        """
        Open the TCP socket (only needs to be called if ``do_open`` in
        :py:meth:`~sensirion_shdlc_driver.port.ShdlcSerialPort.__init__`
        was set to ``False``). Does nothing if the socket is already opened.
        """
        if self._is_open is False:
            self._socket.connect((self._ip, self._port))
            self._is_open = True

    def close(self):
        """
        Close the TCP socket. Does nothing if the socket is already closed.
        """
        if self._is_open is True:
            self._socket.close()
            self._is_open = False

    def transceive(self, slave_address, command_id, data, response_timeout):
        """
        Send SHDLC frame to the TCP socket and return received response frame.

        :param byte slave_address: Slave address.
        :param byte command_id: SHDLC command ID.
        :param bytes-like data: Payload.
        :param float response_timeout: Response timeout in seconds. The actual
            command response timeout is defined by the sum of this parameter
            and the socket base timeout.
        :return: Received address, command_id, state, and payload.
        :rtype: byte, byte, byte, bytes
        :raise ~sensirion_shdlc_driver.errors.ShdlcTimeoutError:
            If no response received within timeout.
        :raise ~sensirion_shdlc_driver.errors.ShdlcResponseError:
            If the received response is invalid.
        """
        with self._lock:
            self._socket.settimeout(self._socket_timeout + response_timeout)
            self._send_frame(slave_address, command_id, data)
            return self._receive_frame()

    def _send_frame(self, slave_address, command_id, data):
        """
        Send a frame to the TCP socket.

        :param byte slave_address: Slave address.
        :param byte command_id: SHDLC command ID.
        :param bytes-like data: Payload.
        """
        builder = ShdlcSerialMosiFrameBuilder(slave_address, command_id, data)
        tx_data = builder.to_bytes()
        log.debug("ShdlcTcpPort send raw: [{}]".format(
                  ", ".join(["0x%.2X" % i for i in bytearray(tx_data)])))
        self._socket.send(tx_data)

    def _receive_frame(self):
        """
        Wait for the response frame and return it.

        :return: Received address, command_id, state, and payload.
        :rtype: byte, byte, byte, bytes
        """
        builder = ShdlcSerialMisoFrameBuilder()

        try:
            while True:
                # Receive data from socket
                # Note: recv buffer size should be a relatively small power
                # of 2. See: https://docs.python.org/3/library/socket.html
                new_data = self._socket.recv(1024)
                if len(new_data) == 0:
                    raise ShdlcTimeoutError()
                # Process received data and return if the frame is complete
                if builder.add_data(new_data):
                    log.debug("ShdlcTcpPort received raw: [{}]".format(
                              ", ".join(["0x%.2X" % i for i in builder.data])))
                    return builder.interpret_data()
        except socket.timeout:
            raise ShdlcTimeoutError()
