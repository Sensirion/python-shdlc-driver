# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_shdlc_driver.firmware_image import ShdlcFirmwareImage
from sensirion_shdlc_driver.types import FirmwareVersion
from sensirion_shdlc_driver.errors import ShdlcFirmwareImageSignatureError
from intelhex import IntelHex
import os
import pytest


TESTS_ROOT = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(TESTS_ROOT, 'data')

EKS2_HEXFILE = os.path.join(DATA_DIR, 'Eks2_combined_V5.2.hex')
EKS2_PRODUCTTYPE = 0x00060000
EKS2_BL_ADDR = 0x08000000
EKS2_BL_MAJOR = 0
EKS2_BL_MINOR = 4
EKS2_APP_ADDR = 0x08004000
EKS2_APP_MAJOR = 5
EKS2_APP_MINOR = 2
EKS2_APP_SIZE = 75096
EKS2_APP_CHECKSUM = 0x88


def test_load_by_file_path():
    """
    Test if the image can be loaded by passing a filepath as string.
    """
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    assert image.size > 0


def test_load_by_file_object():
    """
    Test if the image can be loaded by passing a file-like object.
    """
    with open(EKS2_HEXFILE, mode='r') as f:
        image = ShdlcFirmwareImage(f, EKS2_BL_ADDR, EKS2_APP_ADDR)
        assert image.size > 0


def test_invalid_signature_raises_exception():
    """
    Test if a hexfile with invalid signature raises the proper exception. The
    wrong signature is simulated by passing a wrong application start address.
    """
    with pytest.raises(ShdlcFirmwareImageSignatureError):
        ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR + 1)


def test_property_product_type():
    """
    Test if the value and type of the "product_type" property is correct.
    """
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    assert type(image.product_type) is int
    assert image.product_type == EKS2_PRODUCTTYPE


def test_property_bootloader_version():
    """
    Test if the value and type of the "bootloader_version" property is correct.
    """
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    assert type(image.bootloader_version) is FirmwareVersion
    assert image.bootloader_version.major == EKS2_BL_MAJOR
    assert image.bootloader_version.minor == EKS2_BL_MINOR
    assert image.bootloader_version.debug is False


def test_property_application_version():
    """
    Test if the value and type of the "application_version" property is
    correct.
    """
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    assert type(image.application_version) is FirmwareVersion
    assert image.application_version.major == EKS2_APP_MAJOR
    assert image.application_version.minor == EKS2_APP_MINOR
    assert image.application_version.debug is False


def test_property_checksum():
    """
    Test if the value and type of the "checksum" property is correct.
    """
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    assert type(image.checksum) is int
    assert image.checksum == EKS2_APP_CHECKSUM


def test_property_size():
    """
    Test if the value and type of the "size" property is correct.
    """
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    assert type(image.size) is int
    assert image.size == EKS2_APP_SIZE


def test_property_available_bytes():
    """
    Test if the value and type of the "available_bytes" property is correct.
    """
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    assert type(image.available_bytes) is int
    assert image.available_bytes == image.size


def test_read_all():
    """
    Test if the return value and type of the "read()" method is correct.
    """
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    data = image.read()
    assert type(data) is bytes
    assert len(data) == image.size


def test_read_blocks():
    """
    Test reading data in multiple blocks.
    """
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    data_read_all = image.read()

    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    data_read_blocks = bytes()
    available_bytes = image.available_bytes
    while image.available_bytes > 0:
        block = image.read(42)
        data_read_blocks += block
        available_bytes -= len(block)
        assert type(block) is bytes
        assert 0 <= len(block) <= 42
        assert image.available_bytes == available_bytes

    assert data_read_blocks == data_read_all


def test_read_skips_bootloader_and_signature():
    """
    Test if the "read()" method does not return the bootloader content and the
    signature. This is important to keep the bootloader working after a failed
    firmware update, so it's not possible to break devices.
    """
    hexfile = IntelHex(EKS2_HEXFILE)
    image = ShdlcFirmwareImage(EKS2_HEXFILE, EKS2_BL_ADDR, EKS2_APP_ADDR)
    data = image.read()
    assert len(data) == hexfile.maxaddr() - EKS2_APP_ADDR - 4 + 1
