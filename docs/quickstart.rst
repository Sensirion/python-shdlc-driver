Quick Start
===========

Following example code shows how the driver is intended to use:

.. sourcecode:: python

    from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection, ShdlcDevice

    with ShdlcSerialPort(port='COM1', baudrate=115200) as port:
        device = ShdlcDevice(ShdlcConnection(port), slave_address=0)
        print("Version: {}".format(device.get_version()))
        print("Product Name: {}".format(device.get_product_name()))
        print("Article Code: {}".format(device.get_article_code()))
        print("Serial Number: {}".format(device.get_serial_number()))


.. note:: Not all commands are supported by every SHDLC device. The methods of
          the corresponding commands will raise an exception if the device
          doesn't support them.
