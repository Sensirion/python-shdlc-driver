# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function, unicode_literals
from .errors import ShdlcDeviceError, SHDLC_DEVICE_ERROR_LIST
from .commands.device_info import ShdlcCmdGetProductType, \
    ShdlcCmdGetProductName, ShdlcCmdGetArticleCode, ShdlcCmdGetSerialNumber, \
    ShdlcCmdGetProductSubType
from .commands.device_version import ShdlcCmdGetVersion
from .commands.error_state import ShdlcCmdGetErrorState
from .commands.device_reset import ShdlcCmdDeviceReset

import logging
log = logging.getLogger(__name__)


class ShdlcDevice(object):
    """
    Base class for all SHDLC devices, providing only common SHDLC commands.
    For device-specific commands, there are derived classes available.

    This is a low-level driver which just provides all SHDLC commands as Python
    methods. Typically, calling a method sends one SHDLC request to the device
    and interprets its response. There is no higher level functionality
    available, please look for other drivers if you need a higher level
    interface.

    There is no (or very few) caching functionality in this driver. For example
    if you call get_serial_number() 100 times, it will send the command 100
    times over the SHDLC interface to the device. This makes the driver
    (nearly) stateless.
    """

    def __init__(self, connection, slave_address):
        """
        Create an SHDLC device instance on an SHDLC connection.

        .. note:: This constructor does not communicate with the device, so
                  it's possible to instantiate an object even if the device is
                  not connected or powered yet.

        :param ShdlcConnection connection: The connection used for the
                                           communication (must be an
                                           ShdlcConnection object)
        :param byte slave_address: The address of the device.
        """
        super(ShdlcDevice, self).__init__()
        self._connection = connection
        self._slave_address = slave_address
        self._last_error_flag = False
        self._device_errors = dict()
        self._register_device_errors(SHDLC_DEVICE_ERROR_LIST)

    @property
    def connection(self):
        """
        Get the used SHDLC connection.

        :return: The used SHDLC connection.
        :rtype: ShdlcConnection
        """
        return self._connection

    @property
    def slave_address(self):
        """
        Get the slave address (not read from the device!).

        :return: The slave address.
        :rtype: byte
        """
        return self._slave_address

    @property
    def last_error_flag(self):
        """
        Get the error flag which was received with the last response of the
        device. So this flag gets updated with every command sent to the
        device. If the flag is True, the exact error reason can be read with
        the method get_error_state().

        .. note:: When creating an instance of the ShdlcDevice, this property
                  is initialized with False and will not be updated until you
                  send the first command to the device.

        :return: True if the device indicated an error, False otherwise.
        :rtype: bool
        """
        return self._last_error_flag

    def execute(self, command):
        """
        Execute an SHDLC command.

        :param ShdlcCommand command: The command to execute.
        :return: The interpreted response of the executed command.
        """
        try:
            data, err = self._connection.execute(self._slave_address, command)
            self._last_error_flag = err  # Memorize error flag
            return data
        except ShdlcDeviceError as exc:
            assert exc.error_code != 0
            raise self._get_device_error(exc.error_code)

    def get_product_type(self, as_int=False):
        """
        Get the product type. The product type (sometimes also called "device
        type") can be used to detect what kind of SHDLC product is connected.

        :param bool as_int: If True, the product type is returned as an
                            integer, otherwise as a string of hexadecimal
                            digits (default).
        :return: The product type as an integer or string of hexadecimal
                 digits.
        :rtype: string/int
        """
        product_type = self.execute(ShdlcCmdGetProductType())
        if as_int:
            product_type = int(product_type, 16)
        return product_type

    def get_product_subtype(self):
        """
        Get the product subtype. Some product types exist in multiple slightly
        different variants, this command allows to determine the exact variant
        of the connected device. Sometimes this is called "device subtype".

        Note: This command is not supported by every product type.

        :return: The product subtype as a byte (the interpretation depends on
                 the connected product type).
        :rtype: byte
        """
        return self.execute(ShdlcCmdGetProductSubType())

    def get_product_name(self):
        """
        Get the product name of the device.

        Note: This command is not supported by every product type.

        :return: The product name as an ASCII string.
        :rtype: string
        """
        return self.execute(ShdlcCmdGetProductName())

    def get_article_code(self):
        """
        Get the article code of the device.

        Note: This command is not supported by every product type.

        :return: The article code as an ASCII string.
        :rtype: string
        """
        return self.execute(ShdlcCmdGetArticleCode())

    def get_serial_number(self):
        """
        Get the serial number of the device.

        :return: The serial number as an ASCII string.
        :rtype: string
        """
        return self.execute(ShdlcCmdGetSerialNumber())

    def get_version(self):
        """
        Get the version of the device firmware, hardware and SHDLC protocol.

        :return: The device version as a Version object.
        :rtype: Version
        """
        return self.execute(ShdlcCmdGetVersion())

    def get_error_state(self, clear=True, as_exception=False):
        """
        Get and optionally clear the device error state and the last error. The
        state and error code interpretation depends on the connected device
        type.

        :param bool clear: If true, the error state on the device gets cleared.
        :param bool as_exception: If true, the error state is returned as an
                                  ShdlcDeviceError object instead of a byte.
        :return: The device_state as a 32bit unsigned integer containing all
                 error flags, and the last error which occurred on the device.
                 If as_exception is True, it's returned as an ShdlcDeviceError
                 object or None, otherwise as a byte.
        :rtype: int, byte/ShdlcDeviceError/None
        """
        state, error = self.execute(ShdlcCmdGetErrorState(clear=clear))
        if as_exception:
            error = self._get_device_error(error)
        return state, error

    def device_reset(self):
        """
        Execute a device reset (reboot firmware, similar to power cycle).
        """
        self.execute(ShdlcCmdDeviceReset())
        self._last_error_flag = False  # Reset "cache"

    def _register_device_errors(self, errors):
        """
        Register new device errors for the connected device type. This method
        can (and should!) be called by subclasses of ShdlcDevice to register
        device-specific errors.

        :param list errors: A list of ShdlcDeviceError (or subclass) exception
                            instances.
        """
        for error in errors:
            self._device_errors[error.error_code] = error

    def _get_device_error(self, code):
        """
        Get the device error exception object for a specific device error code.

        :param byte code: The device error code received from the device.
        :return: The corresponding exception object (ShdlcDeviceError or a
                 subclass of it), or None if code is zero.
        :rtype: ShdlcDeviceError/None
        """
        if code != 0:
            return self._device_errors.get(code, ShdlcDeviceError(code))
        else:
            return None
