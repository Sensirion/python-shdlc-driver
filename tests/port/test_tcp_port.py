# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.port import ShdlcTcpPort
from sensirion_shdlc_driver.errors import ShdlcResponseError, ShdlcTimeoutError
import pytest
import socket
import threading


class ShdlcTcpServer(object):
    """
    Helper class to run a virtual SHDLC TCP server on localhost. The
    constructor starts a TCP server which listens for an incoming connection.
    The connection parameters can be obtained with the properties `ip` and
    `port`. Then you can prepare raw responses by assigning the property
    `response_data`. These responses will be sent every time the server
    received some data. The received data can be read back with the property
    `received_data`.
    """

    def __init__(self):
        super(ShdlcTcpServer, self).__init__()
        self._stop = False
        self._exception = None
        self.response_data = []
        self.received_data = []

        # open server socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('localhost', 0))  # Automatically choose a free port
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket_timeout = 1.0
        self._socket.listen(0)
        self.ip, self.port = self._socket.getsockname()

        # start thread
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True  # Avoid blocking tests caused by threads
        self._thread.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop = True
        self._thread.join(2.0)
        # Make sure the tests fail if there was an error in the thread!
        if self._exception is not None:
            raise self._exception

    def _run(self):
        try:
            sock, addr = self._socket.accept()
            while self._stop is not True:
                data = sock.recv(1024)
                if data is not None:
                    self.received_data.append(data)
                    for response in self.response_data:
                        sock.send(response)
            self._socket.close()
        except IOError:
            pass  # Probably client disconnected, which is fine
        except Exception as e:
            self._exception = e


@pytest.fixture
def tcp_server():
    """
    Virtual SHDLC TCP server which will be running during test execution.
    """
    with ShdlcTcpServer() as server:
        yield server


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
def test_is_open(tcp_ip, tcp_port):
    """
    Test if the property is_open is updated when opening and closing the port.
    """
    with ShdlcTcpPort(tcp_ip, tcp_port, do_open=False) as port:
        assert port.is_open is False
        port.open()
        assert port.is_open is True
        port.close()
        assert port.is_open is False


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


def test_transceive_segmented(tcp_server):
    """
    Test if the transceive() method reads the data multiple times from the
    TCP server until the whole frame is received.
    """
    with ShdlcTcpPort(tcp_server.ip, tcp_server.port) as port:
        tcp_server.response_data = [
            b"\x7E\x00\xD1",
            b"\x00",
            b"\x07\x05\x08\x00\x03\x00\x01\x00",
            b"\x16\x7E"
        ]
        addr, cmd, state, data = port.transceive(
            slave_address=42, command_id=0xD1, data=b'',
            response_timeout=10.0)
        assert tcp_server.received_data == [b"\x7E\x2A\xD1\x00\x04\x7E"]
        assert addr == 0x00
        assert cmd == 0xD1
        assert state == 0x00
        assert data == b"\x05\x08\x00\x03\x00\x01\x00"


def test_transceive_checksum_error(tcp_server):
    """
    Test if the transceive() method raises a ShdlcResponseError exception if
    the response contains a wrong checksum.
    """
    with ShdlcTcpPort(tcp_server.ip, tcp_server.port) as port:
        tcp_server.response_data = [b"\x7E\x00\xD1\x00\x00\x00\x7E"]
        with pytest.raises(ShdlcResponseError):
            addr, cmd, state, data = port.transceive(
                slave_address=42, command_id=0xD1, data=b'',
                response_timeout=10.0)


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


def test_is_open_on_closed_port():
    """
    Test if the property is_open returns False on a port which is not open.
    """
    with ShdlcTcpPort('localhost', 0, do_open=False) as port:
        assert type(port.is_open) is bool
        assert port.is_open is False


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
