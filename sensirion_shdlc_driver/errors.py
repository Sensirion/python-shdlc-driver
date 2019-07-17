# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function

import logging
log = logging.getLogger(__name__)


class ShdlcError(Exception):
    """
    Base class for all SHDLC related exceptions.
    """
    pass


class ShdlcFirmwareImageSignatureError(ShdlcError):
    """
    SHDLC firmware image signature error.
    """
    def __init__(self, signature):
        """
        Constructor.

        :param int signature: Firmware image signature.
        """
        super(ShdlcFirmwareImageSignatureError, self).__init__(
            "Invalid signature in firmware image: 0x{:08X}".format(signature)
        )


class ShdlcFirmwareImageIncompatibilityError(ShdlcError):
    """
    SHDLC firmware image incompatibility error.
    """
    def __init__(self, image_type, device_type):
        """
        Constructor.

        :param int image_type:  Device type of the firmware image.
        :param int device_type: Device type of the connected device.
        """
        super(ShdlcFirmwareImageIncompatibilityError, self).__init__(
            "Firmware image for device 0x{:08X} not compatible with connected "
            "device 0x{:08X}.".format(image_type, device_type)
        )


class ShdlcTimeoutError(ShdlcError):
    """
    SHDLC timeout exception (device did not respond to command).
    """
    def __init__(self):
        super(ShdlcTimeoutError, self).__init__(
            "Timeout while waiting for response from SHDLC device. "
            "Check connection to device and make sure it is powered on."
        )


class ShdlcResponseError(ShdlcError):
    """
    SHDLC response error (slave response contains invalid data)
    """
    def __init__(self, message, received_data=None):
        """
        Constructor.

        :param string message: Error message.
        :param received_data: The received (invalid) raw data.
        """
        super(ShdlcResponseError, self).__init__(
            "Invalid data received from the SHDLC device: " + message
        )
        self._received_data = received_data
        if self._received_data is not None:
            received_data_bytearray = bytearray(self._received_data)
            self._received_data = bytes(received_data_bytearray)
            log.debug("Invalid SHDLC response raw data: [{}]".format(
                ", ".join(["0x%.2X" % i for i in received_data_bytearray])))

    @property
    def received_data(self):
        """
        Get the (invalid) raw data which was received from the device.

        :return: The raw data received from the device.
        :rtype: bytes
        """
        return self._received_data


class ShdlcDeviceError(ShdlcError):
    """
    SHDLC device error (communication was successful, but slave failed to
    execute a command). For each error code a subclass exists to provide the
    corresponding error messages.
    """
    def __init__(self, code, message="Unknown error."):
        """
        Constructor.

        :param byte code: The error code received from the device.
        :param string message: The error description for the given error code.
        """
        super(ShdlcDeviceError, self).__init__(
            "SHDLC device returned error code {}: {}".format(code, message)
        )
        self._error_code = code
        self._error_message = str(message)

    @property
    def error_code(self):
        """
        Get the error code received from the device.

        :return: Received error code.
        :rtype: byte
        """
        return self._error_code

    @property
    def error_message(self):
        """
        Get the description of the received error code.

        :return: Error message.
        :rtype: string
        """
        return self._error_message


class ShdlcCommandDataSizeError(ShdlcDeviceError):
    """
    SHDLC device error for wrong data size.
    """
    def __init__(self):
        super(ShdlcCommandDataSizeError, self).__init__(
            1, "Illegal data size of the MOSI frame. Either a wrong command "
               "was sent, or the device firmware does not support the "
               "requested feature."
        )


class ShdlcUnknownCommandError(ShdlcDeviceError):
    """
    SHDLC device error for unknown command.
    """
    def __init__(self):
        super(ShdlcUnknownCommandError, self).__init__(
            2, "Unknown command. Check if you sent the correct command and if "
               "the firmware on the device supports it."
        )


class ShdlcAccessRightError(ShdlcDeviceError):
    """
    SHDLC device error for wrong access right.
    """
    def __init__(self):
        super(ShdlcAccessRightError, self).__init__(
            3, "No access right for this command. Higher access rights are "
               "required to execute this command."
        )


class ShdlcCommandParameterError(ShdlcDeviceError):
    """
    SHDLC device error for illegal command parameter.
    """
    def __init__(self):
        super(ShdlcCommandParameterError, self).__init__(
            4, "Parameter out of range. Check if you sent the correct command "
               "parameters and if the firmware on the device supports them."
        )


class ShdlcChecksumError(ShdlcDeviceError):
    """
    SHDLC device error for wrong checksum.
    """
    def __init__(self):
        super(ShdlcChecksumError, self).__init__(
            5, "Wrong checksum received."
        )


class ShdlcFirmwareUpdateError(ShdlcDeviceError):
    """
    SHDLC device error for firmware update failure.
    """
    def __init__(self):
        super(ShdlcFirmwareUpdateError, self).__init__(
            6, "Firmware update operation failed. Flash couldn't be written "
               "or flash validation failed."
        )


"""
List containing all device errors specified in this file.
"""
SHDLC_DEVICE_ERROR_LIST = [
    ShdlcCommandDataSizeError(),
    ShdlcUnknownCommandError(),
    ShdlcAccessRightError(),
    ShdlcCommandParameterError(),
    ShdlcChecksumError(),
    ShdlcFirmwareUpdateError(),
]
