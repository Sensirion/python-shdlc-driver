# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function

import logging
log = logging.getLogger(__name__)


class FirmwareVersion(object):
    """
    Class representing the firmware version of an SHDLC device.
    """

    def __init__(self, major, minor, debug):
        """
        Constructor.

        :param byte major: Major version (0..255).
        :param byte minor: Minor version (0..99).
        :param bool debug: Debug flag (False for official releases).
        """
        super(FirmwareVersion, self).__init__()
        self.major = major
        self.minor = minor
        self.debug = debug

    def __str__(self):
        return '{}.{}{}'.format(self.major, self.minor,
                                self.debug and '-debug' or '')


class HardwareVersion(object):
    """
    Class representing the hardware version of an SHDLC device.
    """

    def __init__(self, major, minor):
        """
        Constructor.

        :param byte major: Major version (0..255).
        :param byte minor: Minor version (0..99).
        """
        super(HardwareVersion, self).__init__()
        self.major = major
        self.minor = minor

    def __str__(self):
        return '{}.{}'.format(self.major, self.minor)


class ProtocolVersion(object):
    """
    Class representing the SHDLC protocol version of an SHDLC device.
    """

    def __init__(self, major, minor):
        """
        Constructor.

        :param byte major: Major version (0..255).
        :param byte minor: Minor version (0..99).
        """
        super(ProtocolVersion, self).__init__()
        self.major = major
        self.minor = minor

    def __str__(self):
        return '{}.{}'.format(self.major, self.minor)


class Version(object):
    """
    Class representing all version numbers of an SHDLC device. This is used
    for the "Get Version" command.
    """

    def __init__(self, firmware, hardware, protocol):
        """
        Constructor.

        :param ~sensirion_shdlc_driver.types.FirmwareVersion firmware:
            Firmware version.
        :param ~sensirion_shdlc_driver.types.HardwareVersion hardware:
            Hardware version.
        :param ~sensirion_shdlc_driver.types.ProtocolVersion protocol:
            SHDLC protocol version.
        """
        super(Version, self).__init__()
        self.firmware = firmware
        self.hardware = hardware
        self.protocol = protocol

    def __str__(self):
        return 'Firmware {}, Hardware {}, Protocol {}'.format(
            self.firmware, self.hardware, self.protocol
        )
