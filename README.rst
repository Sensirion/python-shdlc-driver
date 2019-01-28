sensirion-shdlc-driver
======================

This package contains the base driver for Sensirion SHDLC devices. It allows to
transmit and receive SHDLC frames over the serial port and provides some
generic commands (e.g. reading the serial number of a device).


Note
----

Normally you shouldn't use this driver directly - instead you should use the
device-specific driver for your actual device as it provides additional
commands. But this driver is still useful if you want to transceive raw SHDLC
frames, or if there is no specific driver available yet for your device.


Installation and Usage
----------------------

The user manual is available at https://sensirion.github.io/python-shdlc-driver/.
