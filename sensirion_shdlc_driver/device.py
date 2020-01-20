# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .errors import ShdlcDeviceError, SHDLC_DEVICE_ERROR_LIST
from .commands.device_info import ShdlcCmdGetProductType, \
    ShdlcCmdGetProductName, ShdlcCmdGetArticleCode, ShdlcCmdGetSerialNumber, \
    ShdlcCmdGetProductSubType
from .commands.device_version import ShdlcCmdGetVersion
from .commands.error_state import ShdlcCmdGetErrorState
from .commands.device_reset import ShdlcCmdDeviceReset
from .commands.slave_address import ShdlcCmdGetSlaveAddress, \
    ShdlcCmdSetSlaveAddress
from .commands.baudrate import ShdlcCmdGetBaudrate, ShdlcCmdSetBaudrate
from .commands.reply_delay import ShdlcCmdGetReplyDelay, ShdlcCmdSetReplyDelay
from .commands.system_up_time import ShdlcCmdGetSystemUpTime
from .commands.factory_reset import ShdlcCmdFactoryReset

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
    if you call
    :py:meth:`~sensirion_shdlc_driver.device.ShdlcDevice.get_serial_number()`
    100 times, it will send the command 100 times over the SHDLC interface to
    the device. This makes the driver (nearly) stateless.
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
        device. If the flag is True, the exact error reason can be read with
        the method
        :py:meth:`~sensirion_shdlc_driver.device.ShdlcDevice.get_error_state()`.

        .. note:: When creating an instance of
                  :py:class:`~sensirion_shdlc_driver.device.ShdlcDevice`, this
                  property is initialized with ``False`` and will not be
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

    def get_product_type(self, as_int=False):
        """
        Get the product type. The product type (sometimes also called "device
        type") can be used to detect what kind of SHDLC product is connected.

        :param bool as_int: If ``True``, the product type is returned as an
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

        .. note:: This command is not supported by every product type.

        :return: The product subtype as a byte (the interpretation depends on
                 the connected product type).
        :rtype: byte
        """
        return self.execute(ShdlcCmdGetProductSubType())

    def get_product_name(self):
        """
        Get the product name of the device.

        .. note:: This command is not supported by every product type.

        :return: The product name as an ASCII string.
        :rtype: string
        """
        return self.execute(ShdlcCmdGetProductName())

    def get_article_code(self):
        """
        Get the article code of the device.

        .. note:: This command is not supported by every product type.

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

        :param bool clear:
            If ``True``, the error state on the device gets cleared.
        :param bool as_exception:
            If ``True``, the error state is returned as an
            :py:class:`~sensirion_shdlc_driver.errors.ShdlcDeviceError`
            object instead of a byte.
        :return: The device state as a 32-bit unsigned integer containing all
                 error flags, and the last error which occurred on the device.
                 If ``as_exception`` is ``True``, it's returned as an
                 :py:class:`~sensirion_shdlc_driver.errors.ShdlcDeviceError`
                 object or ``None``, otherwise as a byte.
        :rtype: int, byte/ShdlcDeviceError/None
        """
        state, error = self.execute(ShdlcCmdGetErrorState(clear=clear))
        if as_exception:
            error = self._get_device_error(error)
        return state, error

    def get_slave_address(self):
        """
        Get the SHDLC slave address of the device.

        .. note:: See also the property
                  :py:attr:`~sensirion_shdlc_driver.device.ShdlcDevice.slave_address`
                  which returns the device's slave address without sending a
                  command. This method really sends a command to the device,
                  even though the slave address is actually already known by
                  this object.

        :return: The slave address of the device.
        :rtype: byte
        """
        return self.execute(ShdlcCmdGetSlaveAddress())

    def set_slave_address(self, slave_address, update_driver=True):
        """
        Set the SHDLC slave address of the device.

        .. note:: The slave address is stored in non-volatile memory of the
                  device and thus persists after a device reset. So the next
                  time connecting to the device, you have to use the new
                  address.

        .. warning:: When changing the address of a slave, make sure there
                     isn't already a slave with that address on the same bus!
                     In that case you would get communication issues which can
                     only be fixed by disconnecting one of the slaves.

        :param byte slave_address:
            The new slave address [0..254]. The address 255 is reserved for
            broadcasts.
        :param bool update_driver:
            If ``True``, the property
            :py:attr:`~sensirion_shdlc_driver.device.ShdlcDevice.slave_address`
            of this object is also updated with the new address. This is
            needed to allow further communication with the device, as its
            address has changed.
        """
        self.execute(ShdlcCmdSetSlaveAddress(slave_address))
        if update_driver:
            self._slave_address = slave_address

    def get_baudrate(self):
        """
        Get the SHDLC baudrate of the device.

        .. note:: This method really sends a command to the device, even though
                  the baudrate is already known by the used
                  :py:class:`~sensirion_shdlc_driver.port.ShdlcPort` object.

        :return: The baudrate of the device [bit/s].
        :rtype: int
        """
        return self.execute(ShdlcCmdGetBaudrate())

    def set_baudrate(self, baudrate, update_driver=True):
        """
        Set the SHDLC baudrate of the device.

        .. note:: The baudrate is stored in non-volatile memory of the
                  device and thus persists after a device reset. So the next
                  time connecting to the device, you have to use the new
                  baudrate.

        .. warning:: If you pass ``True`` to the argument ``update_driver``,
                     the baudrate of the underlaying
                     :py:class:`~sensirion_shdlc_driver.port.ShdlcPort` object
                     is changed. As the baudrate applies to the whole bus (with
                     all its slaves), you might no longer be able to
                     communicate with other slaves. Generally you should change
                     the baudrate of all slaves consecutively, and only set
                     ``update_driver`` to ``True`` the last time.

        :param int baudrate:
            The new baudrate. See device documentation for a list of supported
            baudrates. Many devices support the baudrates 9600, 19200 and
            115200.
        :param bool update_driver:
            If true, the baudrate of the
            :py:class:`~sensirion_shdlc_driver.port.ShdlcPort` object is also
            updated with the baudrate. This is needed to allow further
            communication with the device, as its baudrate has changed.
        """
        self.execute(ShdlcCmdSetBaudrate(baudrate))
        if update_driver:
            self._connection.port.bitrate = baudrate

    def get_reply_delay(self):
        """
        Get the SHDLC reply delay of the device.

        See
        :py:meth:`~sensirion_shdlc_driver.device.ShdlcDevice.set_reply_delay()`
        for details.

        :return: The reply delay of the device [μs].
        :rtype: byte
        """
        return self.execute(ShdlcCmdGetReplyDelay())

    def set_reply_delay(self, reply_delay):
        """
        Set the SHDLC reply delay of the device.

        The reply delay allows to increase the minimum response time of the
        slave to a given value in Microseconds. This is needed for RS485
        masters which require some time to switch from sending to receiving.
        If the slave starts sending the response while the master is still
        driving the bus lines, a conflict on the bus occurs and communication
        fails. If you use such a slow RS485 master, you can increase the reply
        delay of all slaves to avoid this issue.

        :param byte reply_delay: The new reply delay [μs].
        """
        self.execute(ShdlcCmdSetReplyDelay(reply_delay))

    def get_system_up_time(self):
        """
        Get the system up time of the device.

        :return: The time since the last power-on or device reset [s].
        :rtype: int
        """
        return self.execute(ShdlcCmdGetSystemUpTime())

    def device_reset(self):
        """
        Execute a device reset (reboot firmware, similar to power cycle).
        """
        self.execute(ShdlcCmdDeviceReset())
        self._last_error_flag = False  # Reset "cache"

    def factory_reset(self):
        """
        Perform a factory reset (restore the off-the-shelf factory
        configuration).

        .. warning:: This resets any configuration done after leaving the
                     factory! Keep in mind that this command might also change
                     communication parameters (i.e. baudrate and slave address)
                     and thus you might have to adjust the driver's parameters
                     to allow further communication with the device.
        """
        self.execute(ShdlcCmdFactoryReset())
        self._last_error_flag = False  # Reset "cache"

    def _register_device_errors(self, errors):
        """
        Register new device errors for the connected device type. This method
        can (and should!) be called by subclasses of ShdlcDevice to register
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
