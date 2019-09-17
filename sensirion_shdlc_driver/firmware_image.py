# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .errors import ShdlcFirmwareImageSignatureError
from .types import FirmwareVersion
from struct import unpack

import logging
log = logging.getLogger(__name__)


class ShdlcFirmwareImage(object):
    """
    This class represents a firmware image for an SHDLC device. It is used to
    load and verify Intel-Hex files for performing firmware updates over SHDLC.

    Since the different SHDLC devices use different memory layouts, this class
    needs to know the bootloader base address and application base address (see
    constructor parameters). Drivers for specific SHDLC devices should create a
    subclass to provide a new type which already contains the correct
    addresses, so users don't have to care about these details.

    .. note:: This class is intended only for devices which contain the SHDLC
              bootloader. Devices which support firmware updates with another
              system aren't supported by this class.

    .. note:: The package ``intelhex`` must be installed to use this class. See
              :ref:`firmware-updater-dependencies` for details.
    """

    SIGNATURE = 0x4B4F474A  # Signature to identify compatible hexfiles
    PRODUCT_TYPE_OFFSET = 0x04        # Product type address offset
    APP_VERSION_MINOR_OFFSET = 0x08   # Application minor version addr. offset
    APP_VERSION_MAJOR_OFFSET = 0x09   # Application major version addr. offset
    BL_VERSION_MINOR_OFFSET = 0x1004  # Bootloader minor version address offset
    BL_VERSION_MAJOR_OFFSET = 0x1005  # Bootloader major version address offset

    def __init__(self, hexfile, bl_start_addr, app_start_addr):
        """
        Constructor which loads and parses the firmware from a hex file.

        :param str/file hexfile:    The filename or file-like object containing
                                    the firmware in Intel-Hex format (\\*.hex).
        :param int bl_start_addr:   The base address of the bootloader inside
                                    the firmware image.
        :param int app_start_addr:  The base address of the application
                                    inside the firmware image.
        :raise ~sensirion_shdlc_driver.errors.ShdlcFirmwareImageSignatureError:
            If the signature of the image is invalid.
        """
        # Import intelhex here to allow importing the firmware_image module
        # without having the intelhex package installed (it's an optional
        # dependency, so it might be missing).
        from intelhex import IntelHex
        self._bl_start_addr = int(bl_start_addr)
        self._app_start_addr = int(app_start_addr)
        self._app_data_index = 0
        self._data = IntelHex(hexfile)
        self._data.padding = 0xFF  # is returned when reading undefined regions
        log.debug("Loaded hex file: {} [minaddr=0x{:08X}, maxaddr=0x{:08X}]"
                  .format(hexfile, self._data.minaddr(), self._data.maxaddr()))
        self._check_signature()
        log.debug("Signature: OK")
        self._product_type = self._read_product_type()
        log.debug("Product type: 0x{:08X}".format(self._product_type))
        self._bootloader_version = self._read_bootloader_version()
        log.debug("Bootloader version: {}".format(self._bootloader_version))
        self._application_version = self._read_application_version()
        log.debug("Application version: {}".format(self._application_version))
        self._app_data = self._read_application_data()
        log.debug("Application size: {:.2f} kB".format(self.size / 1024))
        self._checksum = self._calc_application_checksum()
        log.debug("Application checksum: 0x{:02X}".format(self._checksum))

    @property
    def product_type(self):
        """
        Get the product type for which the loaded firmware is made.

        :return: Product type as an integer.
        :rtype: int
        """
        return self._product_type

    @property
    def bootloader_version(self):
        """
        Get the bootloader version which is contained in the loaded image.

        :return: Bootloader version (note: debug flag is not supported, it's
                 always False).
        :rtype: ~sensirion_shdlc_driver.types.FirmwareVersion
        """
        return self._bootloader_version

    @property
    def application_version(self):
        """
        Get the application firmware version which is contained in the loaded
        image.

        :return: Application firmware version (note: debug flag is not
                 supported, it's always False).
        :rtype: ~sensirion_shdlc_driver.types.FirmwareVersion
        """
        return self._application_version

    @property
    def checksum(self):
        """
        Get the checksum over the application firmware part of the loaded
        image. This is the checksum which needs to be sent to the product
        bootloader.

        :return: Checksum as a byte.
        :rtype: byte
        """
        return self._checksum

    @property
    def size(self):
        """
        Get the size of the application firmware.

        :return: Size in bytes.
        :rtype: int
        """
        return len(self._app_data)

    @property
    def available_bytes(self):
        """
        Get the count of available bytes left.

        :return: Count of available bytes.
        :rtype: int
        """
        return len(self._app_data) - self._app_data_index

    def read(self, size=-1):
        """
        Read the next bytes of the application firmware.

        :param int size:    Maximum count of bytes to read (-1 reads all
                            available)
        :return:            Firmware data block.
        :rtype: bytes
        """
        if size < 0:
            size = self.available_bytes
        else:
            size = min(size, self.available_bytes)
        data = self._app_data[self._app_data_index:self._app_data_index+size]
        self._app_data_index += len(data)
        return bytes(data)  # immutable type to avoid modifying image data

    def _check_signature(self):
        """
        Check the signature of the loaded image and throw an exception if it's
        invalid.
        """
        signature = self._read_uint32(self._app_start_addr)
        if signature != self.SIGNATURE:
            raise ShdlcFirmwareImageSignatureError(signature)

    def _read_product_type(self):
        """
        Read the product type from the loaded image.

        :return: The read product type.
        :rtype: int
        """
        address = self._app_start_addr + self.PRODUCT_TYPE_OFFSET
        return self._read_uint32(address)

    def _read_bootloader_version(self):
        """
        Read the bootloader version from the loaded image.

        :return: The read bootloader version.
        :rtype: ~sensirion_shdlc_driver.types.FirmwareVersion
        """
        addr_major = self._bl_start_addr + self.BL_VERSION_MAJOR_OFFSET
        addr_minor = self._bl_start_addr + self.BL_VERSION_MINOR_OFFSET
        return FirmwareVersion(major=self._data[addr_major],
                               minor=self._data[addr_minor],
                               debug=False)

    def _read_application_version(self):
        """
        Read the application version from the loaded image.

        :return: The read application version.
        :rtype: ~sensirion_shdlc_driver.types.FirmwareVersion
        """
        addr_major = self._app_start_addr + self.APP_VERSION_MAJOR_OFFSET
        addr_minor = self._app_start_addr + self.APP_VERSION_MINOR_OFFSET
        return FirmwareVersion(major=self._data[addr_major],
                               minor=self._data[addr_minor],
                               debug=False)

    def _read_application_data(self):
        """
        Read the application data block from the loaded image.

        :return: The read application data block.
        :rtype: bytearray
        """
        # Skip the signature because it must not be sent to the bootloader!
        start_addr = self._app_start_addr + 4
        if self._bl_start_addr > self._app_start_addr:
            end_addr = self._bl_start_addr - 1  # Don't include bootloader
        else:
            end_addr = self._data.maxaddr()
        return bytearray(self._data.tobinarray(start=start_addr, end=end_addr))

    def _read_uint32(self, address):
        """
        Read an uint32 at a specific image address.

        :param int address: The address to read from.
        :return: The integer at the specified address.
        :rtype: int
        """
        return unpack("<I", self._data.tobinarray(start=address, size=4))[0]

    def _calc_application_checksum(self):
        """
        Calculate the checksum over the application data, as needed for the
        firmware download command.

        :return: Checksum of application data
        :rtype: byte
        """
        return (sum(self._app_data) % 256) ^ 0xFF
