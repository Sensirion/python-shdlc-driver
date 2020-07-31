# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .errors import ShdlcDeviceError, SHDLC_DEVICE_ERROR_LIST

import logging
log = logging.getLogger(__name__)


class ShdlcDeviceBase(object):
    """
    Base class for all SHDLC devices, providing only the basic functionality
    without implementing any SHDLC commands. The main purpose of this class
    is to allow derived classes to register their device-specific errors and
    to allow executing SHDLC commands.
    """

    def __init__(self, connection, slave_address):
        """
        Create an SHDLC device instance on an SHDLC connection.

        .. note:: This constructor does not communicate with the device, so
                  it's possible to instantiate an object even if the device is
                  not connected or powered yet.

        :param ~sensirion_shdlc_driver.connection.ShdlcConnection connection:
            The connection used for the communication.
        :param byte slave_address:
            The address of the device.
        """
        super(ShdlcDeviceBase, self).__init__()
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
        :rtype: :py:class:`~sensirion_shdlc_driver.connection.ShdlcConnection`
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
        device. If the flag is True, typically the derived classes provide a
        method to read the exact error reason from the device (the
        corresponding SHDLC command is called "Get Device Status").

        .. note:: When creating an instance of
                  :py:class:`~sensirion_shdlc_driver.device.ShdlcDeviceBase`,
                  this property is initialized with ``False`` and will not be
                  updated until you send the first command to the device.

        :return: True if the device indicated an error, False otherwise.
        :rtype: bool
        """
        return self._last_error_flag

    def execute(self, command):
        """
        Execute an SHDLC command.

        :param ~sensirion_shdlc_driver.command.ShdlcCommand command:
            The command to execute.
        :return:
            The interpreted response of the executed command.
        """
        try:
            data, err = self._connection.execute(self._slave_address, command)
            self._last_error_flag = err  # Memorize error flag
            return data
        except ShdlcDeviceError as exc:
            assert exc.error_code != 0
            raise self._get_device_error(exc.error_code)

    def _register_device_errors(self, errors):
        """
        Register new device errors for the connected device type. This method
        can (and should!) be called by subclasses of
        :py:class:`~sensirion_shdlc_driver.device.ShdlcDeviceBase` to register
        device-specific errors.

        :param list errors:
            A list of
            :py:class:`~sensirion_shdlc_driver.errors.ShdlcDeviceError` (or
            subclass) exception instances.
        """
        for error in errors:
            self._device_errors[error.error_code] = error

    def _get_device_error(self, code):
        """
        Get the device error exception object for a specific device error code.

        :param byte code:
            The device error code received from the device.
        :return:
            The corresponding exception object
            (:py:class:`~sensirion_shdlc_driver.errors.ShdlcDeviceError` or a
            subclass of it), or ``None`` if ``code`` is zero.
        :rtype: ShdlcDeviceError/None
        """
        if code != 0:
            return self._device_errors.get(code, ShdlcDeviceError(code))
        else:
            return None
