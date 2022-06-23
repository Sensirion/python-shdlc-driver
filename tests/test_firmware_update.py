# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.errors import ShdlcTimeoutError, \
    ShdlcFirmwareImageIncompatibilityError
from sensirion_shdlc_driver.connection import ShdlcConnection
from sensirion_shdlc_driver.device import ShdlcDevice
from sensirion_shdlc_driver.commands.device_info import ShdlcCmdGetProductType
from sensirion_shdlc_driver.commands.bootloader import \
    ShdlcCmdEnterBootloader, ShdlcCmdFirmwareUpdateStart, \
    ShdlcCmdFirmwareUpdateData, ShdlcCmdFirmwareUpdateStop
from sensirion_shdlc_driver.firmware_image import ShdlcFirmwareImage
from sensirion_shdlc_driver.firmware_update import ShdlcFirmwareUpdate
from mock import MagicMock, PropertyMock
import os
import pytest


TESTS_ROOT = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(TESTS_ROOT, 'data')

EKS2_HEXFILE = os.path.join(DATA_DIR, 'Eks2_combined_V5.2.hex')
EKS2_PRODUCTTYPE = 0x00060000
EKS2_BL_ADDR = 0x08000000
EKS2_APP_ADDR = 0x08004000


def test_timeout():
    """
    Test if execute() raises a timeout error if no device is connected.
    """
    port = MagicMock()
    port.transceive.side_effect = ShdlcTimeoutError()
    device = ShdlcDevice(ShdlcConnection(port), 0)
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    update = ShdlcFirmwareUpdate(device, image)
    with pytest.raises(ShdlcTimeoutError):
        update.execute(emergency=False)


def test_wrong_device_type():
    """
    Test if execute() raises a ShdlcFirmwareImageIncompatibilityError if
    the wrong firmware image is loaded.
    """
    connection = MagicMock()
    connection.execute.return_value = ("1234", False)
    device = ShdlcDevice(connection, 0)
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    update = ShdlcFirmwareUpdate(device, image)
    with pytest.raises(ShdlcFirmwareImageIncompatibilityError):
        update.execute(emergency=False)


def test_execute_normal():
    """
    Test if execute(emergency=False) sends the correct commands to the device.
    """
    connection = MagicMock()
    connection.execute.return_value = (hex(EKS2_PRODUCTTYPE), False)
    device = ShdlcDevice(connection, 0)
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    update = ShdlcFirmwareUpdate(device, image)
    update.execute(emergency=False)
    commands = [c[0][1] for c in device.connection.execute.call_args_list]
    assert type(commands[0]) is ShdlcCmdGetProductType
    assert type(commands[1]) is ShdlcCmdEnterBootloader
    assert type(commands[2]) is ShdlcCmdFirmwareUpdateStart
    for i in range(3, len(commands) - 1):
        assert type(commands[i]) is ShdlcCmdFirmwareUpdateData
    assert type(commands[-1]) is ShdlcCmdFirmwareUpdateStop


def test_execute_emergency():
    """
    Test if execute(emergency=True) skips the device check and enter bootloader
    command.
    """
    connection = MagicMock()
    device = ShdlcDevice(connection, 0)
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    update = ShdlcFirmwareUpdate(device, image)
    update.execute(emergency=True)
    commands = [c[0][1] for c in device.connection.execute.call_args_list]
    assert type(commands[0]) is ShdlcCmdFirmwareUpdateStart
    for i in range(1, len(commands) - 1):
        assert type(commands[i]) is ShdlcCmdFirmwareUpdateData
    assert type(commands[-1]) is ShdlcCmdFirmwareUpdateStop


def test_execute_without_bitrate_getter():
    """
    Test if execute() fails before sending the "enter bootloader" command (to
    avoid bricking the device) if the underlying port has not implemented the
    bitrate getter property.
    """
    connection = MagicMock()
    type(connection.port).bitrate = PropertyMock(
        side_effect=NotImplementedError)
    device = ShdlcDevice(connection, 0)
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    update = ShdlcFirmwareUpdate(device, image)
    with pytest.raises(NotImplementedError):
        update.execute(emergency=False)
    commands = [c[0][1] for c in device.connection.execute.call_args_list]
    assert len(commands) == 0  # no commands sent


def test_status_callback():
    """
    Test if the status callback is properly called.
    """
    connection = MagicMock()
    connection.execute.return_value = (hex(EKS2_PRODUCTTYPE), False)
    device = ShdlcDevice(connection, 0)
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    callback = MagicMock().callback
    update = ShdlcFirmwareUpdate(device, image, status_callback=callback)
    update.execute(emergency=False)
    assert callback.call_count > 0
    for args, kwargs in callback.call_args_list:
        assert len(args) == 1
        assert len(kwargs) == 0
        msg = args[0]
        assert type(msg) is str
        assert len(msg) > 0


def test_progress_callback():
    """
    Test if the progress callback is properly called.
    """
    connection = MagicMock()
    connection.execute.return_value = (hex(EKS2_PRODUCTTYPE), False)
    device = ShdlcDevice(connection, 0)
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    callback = MagicMock().callback
    update = ShdlcFirmwareUpdate(device, image, progress_callback=callback)
    update.execute(emergency=False)
    assert callback.call_count > 0
    for args, kwargs in callback.call_args_list:
        assert len(args) == 1
        assert len(kwargs) == 0
        progress = args[0]
        assert type(progress) is float
        assert 0.0 <= progress <= 100.0
