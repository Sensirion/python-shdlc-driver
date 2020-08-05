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
commands in a new device class. You have two options to create a device class:

* Inherit from :py:class:`~sensirion_shdlc_driver.device_base.ShdlcDeviceBase`
  and add methods for all the supported SHDLC commands of the device, including
  common commands. This is the preferred way since it leads to a device class
  which perfectly fits the particular device, but it requires additional effort
  to also implement all the common SHDLC commands. To reduce effort, you can
  start by copying the needed methods from
  :py:class:`~sensirion_shdlc_driver.device.ShdlcDevice`.
* Inherit from :py:class:`~sensirion_shdlc_driver.device.ShdlcDevice` and add
  only the device-specific commands since the common commands are automatically
  available since the base class already provides them. This is simpler, but
  has the downside that you even inherit methods which the particular device
  might not support, or parameters like response time or post processing time
  might be wrong since they are device specific.

No matter which way you choose, implementing the device class works exactly
the same way:

.. sourcecode:: python

    from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDeviceBase
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


    class MyCustomShdlcDevice(ShdlcDeviceBase):
        def __init__(self, connection, slave_address):
            super(MyCustomShdlcDevice, self).__init__(connection, slave_address)

        def my_custom_command(self, bool_parameter):
            return self.execute(MyCustomCommand(bool_parameter))


    with ShdlcSerialPort(port='COM1', baudrate=115200) as port:
        device = MyCustomShdlcDevice(ShdlcConnection(port), slave_address=0)
        uint32, uint8 = device.my_custom_command(bool_parameter=True)
        print("Response: {}, {}".format(uint32, uint8))


.. _sensirion-shdlc-sensorbridge: https://pypi.org/project/sensirion-shdlc-sensorbridge/
.. _Sensirion SEK-SensorBridge: https://www.sensirion.com/sek-sensorbridge/
