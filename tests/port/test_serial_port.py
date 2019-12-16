# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.port import ShdlcSerialPort
from sensirion_shdlc_driver.errors import ShdlcTimeoutError
from serial import SerialException
import pytest


@pytest.mark.needs_serialport
def test_open_multiple_times(serial_port, serial_bitrate):
    """
    Test if open() can be called multiple times without raising an exception.
    """
    with ShdlcSerialPort(serial_port, serial_bitrate) as port:
        port.open()
        port.open()


@pytest.mark.needs_serialport
def test_close_multiple_times(serial_port, serial_bitrate):
    """
    Test if close() can be called multiple times without raising an exception.
    """
    with ShdlcSerialPort(serial_port, serial_bitrate) as port:
        port.close()
        port.close()


@pytest.mark.needs_serialport
def test_change_bitrate(serial_port, serial_bitrate):
    """
    Test if the bitrate can be changed on an opened port.
    """
    with ShdlcSerialPort(serial_port, serial_bitrate) as port:
        port.bitrate = 19200
        assert port.bitrate == 19200
        port.bitrate = 115200
        assert port.bitrate == 115200


@pytest.mark.needs_serialport
def test_transceive_success(serial_port, serial_bitrate, serial_slave_address):
    """
    Test the transceive() method on a valid port. Note that a device must be
    connected when executing this test. We send the "get version" command
    which is supported by every SHDLC device.
    """
    with ShdlcSerialPort(serial_port, serial_bitrate) as port:
        addr, cmd, state, data = port.transceive(
            slave_address=serial_slave_address, command_id=0xD1, data=b'',
            response_timeout=0.1)
        assert type(addr) is int
        assert type(cmd) is int
        assert type(state) is int
        assert type(data) is bytes
        assert addr == serial_slave_address
        assert cmd == 0xD1
        assert state & 0x7F == 0  # ignore error state flag
        assert len(data) == 7


@pytest.mark.needs_serialport
def test_transceive_timeout(serial_port, serial_bitrate):
    """
    Test if the transceive() method raises a timeout exception when using an
    address where no device is connected.
    """
    with ShdlcSerialPort(serial_port, serial_bitrate) as port:
        with pytest.raises(ShdlcTimeoutError):
            addr, cmd, state, data = port.transceive(
                slave_address=42, command_id=0xD1, data=b'',
                response_timeout=0.1)


def test_create_and_open_invalid_port():
    """
    Test if the constructor of ShdlcSerialPort tries to open the port. This
    is tested by trying to open an invalid port, which should raise an
    exception.
    """
    with pytest.raises(SerialException):
        ShdlcSerialPort('/non/existing/port', 115200)


def test_create_without_open_invalid_port():
    """
    Test if we can create an instance of ShdlcSerialPort without already
    opening the serial port. When calling open() afterwards, it should raise
    an exception since the port doesn't exist.
    """
    port = ShdlcSerialPort('/non/existing/port', 115200, do_open=False)
    with pytest.raises(SerialException):
        port.open()


def test_description():
    """
    Test if the type and value of the description property is correct.
    """
    port = ShdlcSerialPort('/non/existing/port', 115200, do_open=False)
    assert type(port.description) is str
    assert port.description == '/non/existing/port@115200'


def test_bitrate():
    """
    Test if the bitrate property can be read and set.
    """
    port = ShdlcSerialPort('/non/existing/port', 115200, do_open=False)
    assert type(port.bitrate) is int
    assert port.bitrate == 115200
    port.bitrate = 19200
    assert port.bitrate == 19200


def test_additional_response_time():
    """
    Test if the additional_response_time property can be read and set.
    """
    port = ShdlcSerialPort('/non/existing/port', 115200,
                           additional_response_time=5, do_open=False)
    assert type(port.additional_response_time) is float
    assert port.additional_response_time == 5.0
    port.additional_response_time = 0.5
    assert port.additional_response_time == 0.5


def test_lock():
    """
    Test if the lock property can be used in a "with"-statement.
    """
    port = ShdlcSerialPort('/non/existing/port', 115200, do_open=False)
    with port.lock:
        port.additional_response_time = 1.0  # access port while locked
