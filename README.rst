sensirion-shdlc-driver
======================

This package contains the base driver for Sensirion SHDLC devices. It allows to
transmit and receive SHDLC frames over the serial port and provides some
generic commands (e.g. reading the serial number of a device).

SHDLC Protocol
--------------

SHDLC (Sensirion High-Level Data Link Control) is a byte-oriented master-slave
communication protocol based on `ISO HDLC`_. It is used to control some of
Sensirion's devices (for example mass flow controllers). The detailed protocol
documentation is not publicly available (yet). If you need it, please contact
our `customer support`_.

.. _ISO HDLC: https://en.wikipedia.org/wiki/High-Level_Data_Link_Control
.. _customer support: https://www.sensirion.com/en/about-us/contact/

Note
----

Normally you shouldn't use this driver directly - instead you should use the
device-specific driver for your actual device as it provides additional
commands. But this driver is still useful if you want to transceive raw SHDLC
frames, or if there is no specific driver available yet for your device.

Install
-------
.. sourcecode:: bash
    
    pip install sensirion-shdlc-driver

Recommended usage is within a virtualenv.

Usage
-----
.. sourcecode:: python
    
    import sensirion_shdlc_driver
