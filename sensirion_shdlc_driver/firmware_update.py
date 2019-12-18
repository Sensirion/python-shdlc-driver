# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .commands.bootloader import ShdlcCmdEnterBootloader, \
    ShdlcCmdFirmwareUpdateStart, ShdlcCmdFirmwareUpdateData, \
    ShdlcCmdFirmwareUpdateStop
from .errors import ShdlcFirmwareImageIncompatibilityError

import logging
log = logging.getLogger(__name__)


class ShdlcFirmwareUpdate(object):
    """
    Helper class to perform firmware updates over SHDLC.

    .. note:: Device-specific drivers should provide a simple wrapper method
              to easily perform firmware updates. So usually you don't have to
              use this class directly.
    """

    # The SHDLC bootloader has a fixed bitrate and slave address, independent
    # of the actual device settings or rotary switches.
    BOOTLOADER_BITRATE = 115200
    BOOTLOADER_SLAVE_ADDRESS = 0

    def __init__(self, device, image, status_callback=None,
                 progress_callback=None):
        """
        Constructor.

        :param ~sensirion_shdlc_driver.device.ShdlcDevice device:
            The device to update.
        :param ~sensirion_shdlc_driver.firmware_image.ShdlcFirmwareImage image:
            The image to flash.
        :param callable status_callback: Optional callback for status report,
                                         taking a string as parameter.
        :param callable progress_callback: Optional callback for progress
                                           report, taking a float (progress in
                                           percent) as parameter.
        """
        self._device = device
        self._image = image
        self._status_callback = status_callback
        self._progress_callback = progress_callback

    def execute(self, emergency=False):
        """
        Perform the firmware update.

        .. note:: This can take several minutes, don't abort it! If aborted,
                  the device stays in the bootloader and you need to restart
                  the update with ``emergency=True`` to recover.

        :param bool emergency: Must be set to ``True`` if the device is already
                               in bootloader mode, ``False`` otherwise.
        :raises ~sensirion_shdlc_driver.errors.ShdlcFirmwareImageIncompatibilityError:
            If the image is not compatible with the connected device.
        :raises Exception: On other errors.
        """  # noqa: E501
        # Lock the port during the whole firmware update procedure.
        with self._device.connection.port.lock:
            # Check if the underlying port supports changing the bitrate. If it
            # doesn't support changing the bitrate (e.g. like ShdlcTcpPort), we
            # must raise an exception *before* the "enter bootloader" command
            # is sent to the device. Otherwise the device enters the bootloader
            # but the user will not be able to update the firmware, which would
            # be a bad situation. Thus we just read and set the bitrate to
            # check if the underlying port has a bitrate getter and setter.
            try:
                old_bitrate = self._device.connection.port.bitrate
                self._device.connection.port.bitrate = old_bitrate
            except NotImplementedError:
                raise NotImplementedError(
                    "The used port '{}' does not support changing the bitrate,"
                    " therefore it's not possible to update the firmware."
                    .format(self._device.connection.port.__class__.__name__))

            # Only check product type and enter the bootloader if it's not an
            # emergency update, i.e. the application firmware is still running.
            if not emergency:
                self._check_product_type(progress=4.0)
                self._enter_bootloader(progress=7.0)

            # Switch to the bootloader bitrate and send the update commands.
            self._device.connection.port.bitrate = self.BOOTLOADER_BITRATE
            try:
                self._send_start(progress=10.0)
                self._send_data(progress_start=10.0, progress_end=90.0)
                self._send_stop(progress=100.0)
            finally:
                self._device.connection.port.bitrate = old_bitrate
        self._status("Finished!")

    def _check_product_type(self, progress):
        """
        Check the product type.

        Checks if the product type of the loaded firmware image corresponds to
        the product type of the connected device. Raises an exception if it
        doesn't match.
        """
        self._status("Check compatibility...")
        actual = self._device.get_product_type(as_int=True)
        expected = self._image.product_type
        if actual != expected:
            raise ShdlcFirmwareImageIncompatibilityError(expected, actual)
        self._progress(progress)

    def _enter_bootloader(self, progress):
        """
        Enter the bootloaded on the device.
        """
        self._status("Enter bootloader...")
        self._execute(self._device.slave_address, ShdlcCmdEnterBootloader())
        self._progress(progress)

    def _send_start(self, progress):
        """
        Send the update start command to the bootloader.

        :param float progress: The progress after executing this command.
        """
        self._status("Clear flash...")
        self._execute(self.BOOTLOADER_SLAVE_ADDRESS,
                      ShdlcCmdFirmwareUpdateStart())
        self._progress(progress)

    def _send_data(self, progress_start, progress_end):
        """
        Send the new firmware to the bootloader.

        :param float progress_start: The progress before sending the data.
        :param float progress_end: The progress after sending the data.
        """
        self._status("Write new firmware...")
        progress_diff = progress_end - progress_start
        while self._image.available_bytes > 0:
            cmd = ShdlcCmdFirmwareUpdateData(data=self._image.read(254))
            self._execute(self.BOOTLOADER_SLAVE_ADDRESS, cmd)
            count = self._image.size - self._image.available_bytes
            ratio = count / float(self._image.size)
            percent = progress_start + (ratio * progress_diff)
            self._status("Write new firmware: {:.2f} kB of {:.2f} kB".format(
                count / 1024.0, self._image.size / 1024.0))
            self._progress(percent)

    def _send_stop(self, progress):
        """
        Send the update stop command to the bootloader.

        :param float progress: The progress after executing this command.
        """
        self._status("Verify checksum...")
        cmd = ShdlcCmdFirmwareUpdateStop(checksum=self._image.checksum)
        self._execute(self.BOOTLOADER_SLAVE_ADDRESS, cmd)
        self._progress(progress)

    def _execute(self, slave_address, command):
        """
        Execute an SHDLC command.

        :param int slave_address: The slave address where to send the command.
        :param ~sensirion_shdlc_driver.command.ShdlcCommand command:
            The command to execute.
        """
        self._device.connection.execute(slave_address, command)

    def _status(self, status):
        """
        Update the status message.

        :param string status: The new status message.
        """
        log.debug("SHDLC firmware update: {}".format(status))
        if self._status_callback:
            self._status_callback(status)

    def _progress(self, percent):
        """
        Update the progress position.

        :param float percent: The new progress in percent.
        """
        if self._progress_callback:
            self._progress_callback(percent)
