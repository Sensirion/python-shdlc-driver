Logging / Debugging
===================

Every module of this package uses the `Python Logging Facility`_ to log debug
messages, warnings etc. This page gives a quick overview how it works.

Usage
-----

To enable the logging facility in your project, just add the following lines
to the top of your main Python script:

.. sourcecode:: python

    import logging
    logging.basicConfig()


Log Raw Transmitted/Received Data
---------------------------------

When debugging issues on a lower layer, it might be useful to see what data
(raw bytes) is actually sent to the underlying port, and what data is received
from the connected device. This data can be shown by changing the logging
level to ``DEBUG``:

.. sourcecode:: python

    from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDevice

    import logging
    logging.basicConfig(level=logging.DEBUG)  # <- logging level set here

    with ShdlcSerialPort(port='COM1', baudrate=115200) as port:
        device = ShdlcDevice(ShdlcConnection(port), slave_address=0)
        print("Version: {}".format(device.get_version()))


This way the raw data is printed to the console:

.. sourcecode:: console

    DEBUG:sensirion_shdlc_driver.port:Open ShdlcSerialPort on 'COM1' with 115200 bit/s.
    DEBUG:sensirion_shdlc_driver.connection:Opened ShdlcConnection on 'COM1@115200'.
    DEBUG:sensirion_shdlc_driver.port:ShdlcSerialPort send raw: [0x7E, 0x00, 0xD1, 0x00, 0x2E, 0x7E]
    DEBUG:sensirion_shdlc_driver.port:ShdlcSerialPort received raw: [0x7E, 0x00, 0xD1, 0x00, 0x07, 0x05, 0x08, 0x00, 0x03, 0x00, 0x01, 0x00, 0x16, 0x7E]
    Version: Firmware 5.8, Hardware 3.0, Protocol 1.0


Change Logging Verbosity of Modules
-----------------------------------

Since every module contains its own logging object ``log``, it's even possible
to set the logging level of each module independently. For example, the
verbosity of the :py:class:`~sensirion_shdlc_driver.port.ShdlcPort` classes
could be reduced by changing their logging level to ``CRITICAL`` (i.e. only
critical messages will be logged):

.. sourcecode:: python

    import sensirion_shdlc_driver
    from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDevice

    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Make port less verbose
    sensirion_shdlc_driver.port.log.setLevel(level=logging.CRITICAL)

    with ShdlcSerialPort(port='COM1', baudrate=115200) as port:
        device = ShdlcDevice(ShdlcConnection(port), slave_address=0)
        print("Version: {}".format(device.get_version()))


This way you won't see the raw transmitted data:

.. sourcecode:: console

    DEBUG:sensirion_shdlc_driver.connection:Opened ShdlcConnection on 'COM1@115200'.
    Version: Firmware 5.8, Hardware 3.0, Protocol 1.0


.. _Python Logging Facility: https://docs.python.org/3/library/logging.html
