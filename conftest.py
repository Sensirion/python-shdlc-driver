# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
import pytest


def pytest_addoption(parser):
    """
    Register command line options
    """
    parser.addoption("--serial-port", action="store", type=str)
    parser.addoption("--serial-bitrate", action="store", type=int,
                     default=115200)
    parser.addoption("--serial-address", action="store", type=int, default=0)
    parser.addoption("--tcp-ip", action="store", type=str)
    parser.addoption("--tcp-port", action="store", type=int)
    parser.addoption("--tcp-address", action="store", type=int, default=0)


def _get_serial_port(config, validate=False):
    """
    Get the serial port to be used for the tests.
    """
    port = config.getoption("--serial-port")
    if (validate is True) and (port is None):
        raise ValueError("Please specify the serial port to be used with "
                         "the '--serial-port' argument.")
    return port


def _get_serial_bitrate(config):
    """
    Get the serial port bitrate to be used for the tests.
    """
    return config.getoption("--serial-bitrate")


def _get_serial_slave_address(config):
    """
    Get the serial port slave address to be used for the tests.
    """
    return config.getoption("--serial-address")


def _get_tcp_ip(config, validate=False):
    """
    Get the TCP IP address to be used for the tests.
    """
    ip = config.getoption("--tcp-ip")
    if (validate is True) and (ip is None):
        raise ValueError("Please specify the IP address to be used with "
                         "the '--tcp-ip' argument.")
    return ip


def _get_tcp_port(config, validate=False):
    """
    Get the TCP port to be used for the tests.
    """
    port = config.getoption("--tcp-port")
    if (validate is True) and (port is None):
        raise ValueError("Please specify the TCP port to be used with "
                         "the '--tcp-port' argument.")
    return port


def _get_tcp_slave_address(config):
    """
    Get the TCP slave address to be used for the tests.
    """
    return config.getoption("--tcp-address")


def pytest_report_header(config):
    """
    Add extra information to test report header
    """
    lines = []
    lines.append("serial port: " + str(_get_serial_port(config)))
    lines.append("serial bitrate: " + str(_get_serial_bitrate(config)))
    lines.append("serial address: " + str(_get_serial_slave_address(config)))
    lines.append("TCP IP: " + str(_get_tcp_ip(config)))
    lines.append("TCP port: " + str(_get_tcp_port(config)))
    lines.append("TCP address: " + str(_get_tcp_slave_address(config)))
    return '\n'.join(lines)


@pytest.fixture(scope="session")
def serial_port(request):
    """
    Fixture to get the serial port to be used for the tests.
    """
    return _get_serial_port(request.config, validate=True)


@pytest.fixture(scope="session")
def serial_bitrate(request):
    """
    Fixture to get the serial port bitrate to be used for the tests.
    """
    return _get_serial_bitrate(request.config)


@pytest.fixture(scope="session")
def serial_slave_address(request):
    """
    Fixture to get the serial port slave address to be used for the tests.
    """
    return _get_serial_slave_address(request.config)


@pytest.fixture(scope="session")
def tcp_ip(request):
    """
    Fixture to get the TCP IP address to be used for the tests.
    """
    return _get_tcp_ip(request.config, validate=True)


@pytest.fixture(scope="session")
def tcp_port(request):
    """
    Fixture to get the TCP port to be used for the tests.
    """
    return _get_tcp_port(request.config, validate=True)


@pytest.fixture(scope="session")
def tcp_slave_address(request):
    """
    Fixture to get the TCP slave address to be used for the tests.
    """
    return _get_tcp_slave_address(request.config)
