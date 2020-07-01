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

EKS2 = {
    'HEXFILE': os.path.join(DATA_DIR, 'Eks2_combined_V5.2.hex'),
    'PRODUCTTYPE': 0x00060000,
    'BL_ADDR': 0x08000000,
    'BL_MAJOR': 0,
    'BL_MINOR': 4,
    'APP_ADDR': 0x08004000,
    'APP_MAJOR': 5,
    'APP_MINOR': 2,
    'APP_SIZE': 75096,
    'APP_CHECKSUM': 0x88,
}

STM32G0 = {
    'HEXFILE': os.path.join(DATA_DIR, 'Stm32g0Firmware.hex'),
    'PRODUCTTYPE': 0x00140000,
    'BL_ADDR': 0x08000000,
    'BL_MAJOR': 1,
    'BL_MINOR': 0,
    'APP_ADDR': 0x08001000,
    'APP_MAJOR': 0,
    'APP_MINOR': 1,
    'APP_SIZE': 1600,
    'APP_CHECKSUM': 0x3A,
    'BL_VERSION_OFFSET': 0x200,
    'SIGNATURE': b'\x4b\x4f\x47\x4a\xa4\x74\xf4\xb4',
}


@pytest.fixture(params=[EKS2, STM32G0])
def fw(request):
    config = request.param
    image = ShdlcFirmwareImage(
        hexfile=config.get('HEXFILE'),
        bl_start_addr=config.get('BL_ADDR'),
        app_start_addr=config.get('APP_ADDR'),
        signature=config.get('SIGNATURE', b'\x4A\x47\x4F\x4B'),
        bl_version_offset=config.get('BL_VERSION_OFFSET', 0x1004))
    config['IMAGE'] = image
    yield config


def test_load_by_file_path():
    """
    Test if the image can be loaded by passing a filepath as string.
    """
    image = ShdlcFirmwareImage(
        EKS2.get('HEXFILE'), EKS2.get('BL_ADDR'), EKS2.get('APP_ADDR'))
    assert image.size > 0


def test_load_by_file_object():
    """
    Test if the image can be loaded by passing a file-like object.
    """
    with open(EKS2.get('HEXFILE'), mode='r') as f:
        image = ShdlcFirmwareImage(f, EKS2.get('BL_ADDR'),
                                   EKS2.get('APP_ADDR'))
        assert image.size > 0


@pytest.mark.parametrize("config", [EKS2, STM32G0])
def test_load_by_file_object_with_all_parameters(config):
    """
    Test if the image can be loaded by passing a file-like object.
    """
    with open(config.get('HEXFILE'), mode='r') as f:
        image = ShdlcFirmwareImage(
            hexfile=f, bl_start_addr=config.get('BL_ADDR'),
            app_start_addr=config.get('APP_ADDR'),
            signature=config.get('SIGNATURE', b'\x4A\x47\x4F\x4B'),
            bl_version_offset=config.get('BL_VERSION_OFFSET', 0x1004))
        assert image.size > 0


def test_invalid_signature_raises_exception(fw):
    """
    Test if a hexfile with invalid signature raises the proper exception. The
    wrong signature is simulated by passing a wrong application start address.
    """
    with pytest.raises(ShdlcFirmwareImageSignatureError):
        ShdlcFirmwareImage(
            hexfile=fw.get('HEXFILE'),
            bl_start_addr=fw.get('BL_ADDR'),
            app_start_addr=fw.get('APP_ADDR') + 1,
            signature=fw.get('SIGNATURE', b'\x4A\x47\x4F\x4B'),
            bl_version_offset=fw.get('BL_VERSION_OFFSET', 0x1004))


def test_property_product_type(fw):
    """
    Test if the value and type of the "product_type" property is correct.
    """
    assert type(fw.get('IMAGE').product_type) is int
    assert fw.get('IMAGE').product_type == fw.get('PRODUCTTYPE')


def test_property_bootloader_version(fw):
    """
    Test if the value and type of the "bootloader_version" property is correct.
    """
    assert type(fw.get('IMAGE').bootloader_version) is FirmwareVersion
    assert fw.get('IMAGE').bootloader_version.major == fw.get('BL_MAJOR')
    assert fw.get('IMAGE').bootloader_version.minor == fw.get('BL_MINOR')
    assert fw.get('IMAGE').bootloader_version.debug is False


def test_property_application_version(fw):
    """
    Test if the value and type of the "application_version" property is
    correct.
    """
    assert type(fw.get('IMAGE').application_version) is FirmwareVersion
    assert fw.get('IMAGE').application_version.major == fw.get('APP_MAJOR')
    assert fw.get('IMAGE').application_version.minor == fw.get('APP_MINOR')
    assert fw.get('IMAGE').application_version.debug is False


def test_property_checksum(fw):
    """
    Test if the value and type of the "checksum" property is correct.
    """
    assert type(fw.get('IMAGE').checksum) is int
    assert fw.get('IMAGE').checksum == fw.get('APP_CHECKSUM')


def test_property_size(fw):
    """
    Test if the value and type of the "size" property is correct.
    """
    assert type(fw.get('IMAGE').size) is int
    assert fw.get('IMAGE').size == fw.get('APP_SIZE')


def test_property_available_bytes(fw):
    """
    Test if the value and type of the "available_bytes" property is correct.
    """
    assert type(fw.get('IMAGE').available_bytes) is int
    assert fw.get('IMAGE').available_bytes == fw.get('IMAGE').size


def test_read_all(fw):
    """
    Test if the return value and type of the "read()" method is correct.
    """
    data = fw.get('IMAGE').read()
    assert type(data) is bytes
    assert len(data) == fw.get('IMAGE').size


def test_read_blocks(fw):
    """
    Test reading data in multiple blocks.
    """
    image = ShdlcFirmwareImage(
            hexfile=fw.get('HEXFILE'),
            bl_start_addr=fw.get('BL_ADDR'),
            app_start_addr=fw.get('APP_ADDR'),
            signature=fw.get('SIGNATURE', b'\x4A\x47\x4F\x4B'),
            bl_version_offset=fw.get('BL_VERSION_OFFSET', 0x1004))
    data_read_all = image.read()

    image = ShdlcFirmwareImage(
            hexfile=fw.get('HEXFILE'),
            bl_start_addr=fw.get('BL_ADDR'),
            app_start_addr=fw.get('APP_ADDR'),
            signature=fw.get('SIGNATURE', b'\x4A\x47\x4F\x4B'),
            bl_version_offset=fw.get('BL_VERSION_OFFSET', 0x1004))
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


def test_read_skips_bootloader_and_signature(fw):
    """
    Test if the "read()" method does not return the bootloader content and the
    signature. This is important to keep the bootloader working after a failed
    firmware update, so it's not possible to break devices.
    """
    hexfile = IntelHex(fw.get('HEXFILE'))
    data = fw.get('IMAGE').read()
    assert len(data) == hexfile.maxaddr() - fw.get('APP_ADDR') - \
        len(fw.get('SIGNATURE', b'\x4A\x47\x4F\x4B')) + 1
