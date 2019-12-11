# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.port import ShdlcTcpPort
from sensirion_shdlc_driver.errors import ShdlcTimeoutError
import pytest


@pytest.mark.needs_tcp
def test_open_multiple_times(tcp_ip, tcp_port):
    """
    Test if open() can be called multiple times without raising an exception.
    """
    with ShdlcTcpPort(tcp_ip, tcp_port) as port:
        port.open()
        port.open()


@pytest.mark.needs_tcp
def test_close_multiple_times(tcp_ip, tcp_port):
    """
    Test if close() can be called multiple times without raising an exception.
    """
    with ShdlcTcpPort(tcp_ip, tcp_port) as port:
        port.close()
        port.close()


@pytest.mark.needs_tcp
def test_transceive_success(tcp_ip, tcp_port, tcp_slave_address):
    """
    Test the transceive() method on a valid IP and port. Note that a device
    must be connected when executing this test. We send the "get version"
    command which is supported by every SHDLC device.
    """
    with ShdlcTcpPort(tcp_ip, tcp_port) as port:
        addr, cmd, state, data = port.transceive(
            slave_address=tcp_slave_address, command_id=0xD1, data=b'',
            response_timeout=0.1)
        assert type(addr) is int
        assert type(cmd) is int
        assert type(state) is int
        assert type(data) is bytes
        assert addr == tcp_slave_address
        assert cmd == 0xD1
        assert state & 0x7F == 0  # ignore error state flag
        assert len(data) == 7


@pytest.mark.needs_tcp
def test_transceive_timeout(tcp_ip, tcp_port):
    """
    Test if the transceive() method raises a timeout exception when using an
    address where no device is connected.
    """
    with ShdlcTcpPort(tcp_ip, tcp_port) as port:
        with pytest.raises(ShdlcTimeoutError):
            addr, cmd, state, data = port.transceive(
                slave_address=42, command_id=0xD1, data=b'',
                response_timeout=0.1)


def test_create_and_open_invalid_port():
    """
    Test if the constructor of ShdlcTcpPort tries to open the port. This
    is tested by trying to open an invalid port, which should raise an
    exception.
    """
    with pytest.raises(IOError):
        ShdlcTcpPort('localhost', 0)


def test_create_without_open_invalid_port():
    """
    Test if we can create an instance of ShdlcTcpPort without already
    opening the port. When calling open() afterwards, it should raise
    an exception since the port doesn't exist.
    """
    port = ShdlcTcpPort('localhost', 0, do_open=False)
    with pytest.raises(IOError):
        port.open()


def test_description():
    """
    Test if the type and value of the description property is correct.
    """
    port = ShdlcTcpPort('localhost', 42, do_open=False)
    assert type(port.description) is str
    assert port.description == 'localhost:42'


def test_socket_timeout():
    """
    Test if the socket_timeout property can be read and set.
    """
    port = ShdlcTcpPort('localhost', 0, socket_timeout=5, do_open=False)
    assert type(port.socket_timeout) is float
    assert port.socket_timeout == 5.0
    port.socket_timeout = 0.5
    assert port.socket_timeout == 0.5


def test_lock():
    """
    Test if the lock property can be used in a "with"-statement.
    """
    port = ShdlcTcpPort('localhost', 0, do_open=False)
    with port.lock:
        port.socket_timeout = 1.0  # access port while locked
