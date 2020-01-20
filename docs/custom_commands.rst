Executing Custom Commands
=========================

To communicate with SHDLC devices, usually you won't use this base driver
directly since it doesn't provide device specific commands. Instead, you
use a dedicated Python driver created for a specific device type, like
`sensirion-shdlc-sensorbridge`_ for the `Sensirion SEK-SensorBridge`_.

But if there is no Python driver available (yet) for a particular SHDLC device,
this base driver could still be used to communicate with that device. There
are two different ways how to execute custom SHDLC commands with this driver.


Using ShdlcCommand Directly
---------------------------

The simplest way is to pass an
:py:class:`~sensirion_shdlc_driver.command.ShdlcCommand` object to the
:py:meth:`~sensirion_shdlc_driver.device.ShdlcDevice.execute` method of the
device:

.. sourcecode:: python

    from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDevice
    from sensirion_shdlc_driver.command import ShdlcCommand
    from struct import unpack

    with ShdlcSerialPort(port='COM1', baudrate=115200) as port:
        device = ShdlcDevice(ShdlcConnection(port), slave_address=0)

        # Execute custom command
        raw_response = device.execute(ShdlcCommand(
            id=0xD2,  # The command ID as specified in the device documentation
            data=b"\x01",  # The payload data to send
            max_response_time=0.2,  # Maximum response time in Seconds
        ))
        print("Raw Response: {}".format(raw_response))

        # Convert raw response to proper data types
        uint32, uint8 = unpack('>IB', raw_response)
        print("Response: {}, {}".format(uint32, uint8))


For more options and detailed information, please take a look at the
documentation of :py:class:`~sensirion_shdlc_driver.command.ShdlcCommand`.


Deriving from ShdlcCommand
--------------------------

Another, more powerful way to implement custom commands is to create separate
classes for each command. Especially if the raw response bytes need to be
converted to other data types this is handy since it will make the
:py:meth:`~sensirion_shdlc_driver.device.ShdlcDevice.execute` method
returning the converted response.

.. sourcecode:: python

    from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDevice
    from sensirion_shdlc_driver.command import ShdlcCommand
    from struct import pack, unpack

    class MyCustomCommand(ShdlcCommand):
        def __init__(self, bool_parameter):
            super(MyCustomCommand, self).__init__(
                id=0xD2,  # Command ID as specified in the device documentation
                data=pack(">B", bool_parameter),  # Payload data
                max_response_time=0.2,  # Maximum response time in Seconds
            )

        def interpret_response(self, data):
            # Convert the received raw bytes to the proper data types
            uint32, uint8 = unpack('>IB', data)
            return uint32, uint8


    with ShdlcSerialPort(port='COM1', baudrate=115200) as port:
        device = ShdlcDevice(ShdlcConnection(port), slave_address=0)
        uint32, uint8 = device.execute(MyCustomCommand(bool_parameter=True))
        print("Response: {}, {}".format(uint32, uint8))


Creating a Device Class
-----------------------

To create a more convenient API, it might make sense to wrap the custom
commands in a new device class. When inheriting from
:py:class:`~sensirion_shdlc_driver.device.ShdlcDevice`, you even get a class
providing all the common SHDLC commands in addition to your custom commands:

.. sourcecode:: python

    from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDevice
    from sensirion_shdlc_driver.command import ShdlcCommand
    from struct import pack, unpack

    class MyCustomCommand(ShdlcCommand):
        def __init__(self, bool_parameter):
            super(MyCustomCommand, self).__init__(
                id=0xD2,  # Command ID as specified in the device documentation
                data=pack(">B", bool_parameter),  # Payload data
                max_response_time=0.2,  # Maximum response time in Seconds
            )

        def interpret_response(self, data):
            # Convert the received raw bytes to the proper data types
            uint32, uint8 = unpack('>IB', data)
            return uint32, uint8


    class MyCustomShdlcDevice(ShdlcDevice):
        def __init__(self, connection, slave_address):
            super(MyCustomShdlcDevice, self).__init__(connection, slave_address)

        def my_custom_command(self, bool_parameter):
            return self.execute(MyCustomCommand(bool_parameter))


    with ShdlcSerialPort(port='COM1', baudrate=115200) as port:
        device = MyCustomShdlcDevice(ShdlcConnection(port), slave_address=0)
        print("Version: {}".format(device.get_version()))
        uint32, uint8 = device.my_custom_command(bool_parameter=True)
        print("Response: {}, {}".format(uint32, uint8))


.. _sensirion-shdlc-sensorbridge: https://pypi.org/project/sensirion-shdlc-sensorbridge/
.. _Sensirion SEK-SensorBridge: https://www.sensirion.com/sek-sensorbridge/
