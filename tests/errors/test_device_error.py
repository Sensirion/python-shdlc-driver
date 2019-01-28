# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function, unicode_literals
from sensirion_shdlc_driver.errors import ShdlcDeviceError, \
    ShdlcCommandDataSizeError, ShdlcUnknownCommandError, \
    ShdlcAccessRightError, ShdlcCommandParameterError, ShdlcChecksumError, \
    ShdlcFirmwareUpdateError


def test_message():
    """
    Test if the message is a non-empty string.
    """
    err = ShdlcDeviceError(code=42, message="Foo")
    msg = str(err)
    assert len(msg) > 0


def test_error_code():
    """
    Test if the type and value of the "error_code" property is correct.
    """
    err = ShdlcDeviceError(code=42, message="Foo")
    code = err.error_code
    assert type(code) is int
    assert code == 42


def test_error_message():
    """
    Test if the type and value of the "error_message" property is correct.
    """
    err = ShdlcDeviceError(code=42, message="Hello World!")
    message = err.error_message
    assert type(message) is str
    assert message == "Hello World!"


def test_command_data_size_error():
    """
    Test if the id and message of ShdlcCommandDataSizeError is correct.
    """
    err = ShdlcCommandDataSizeError()
    assert err.error_code == 0x01
    assert len(str(err)) > 0


def test_unknown_command_error():
    """
    Test if the id and message of ShdlcUnknownCommandError is correct.
    """
    err = ShdlcUnknownCommandError()
    assert err.error_code == 0x02
    assert len(str(err)) > 0


def test_access_right_error():
    """
    Test if the id and message of ShdlcAccessRightError is correct.
    """
    err = ShdlcAccessRightError()
    assert err.error_code == 0x03
    assert len(str(err)) > 0


def test_command_parameter_error():
    """
    Test if the id and message of ShdlcCommandParameterError is correct.
    """
    err = ShdlcCommandParameterError()
    assert err.error_code == 0x04
    assert len(str(err)) > 0


def test_checksum_error():
    """
    Test if the id and message of ShdlcChecksumError is correct.
    """
    err = ShdlcChecksumError()
    assert err.error_code == 0x05
    assert len(str(err)) > 0


def test_firmware_update_error():
    """
    Test if the id and message of ShdlcFirmwareUpdateError is correct.
    """
    err = ShdlcFirmwareUpdateError()
    assert err.error_code == 0x06
    assert len(str(err)) > 0
