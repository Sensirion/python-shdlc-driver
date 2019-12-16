Installation
============

The package can be installed with pip:

.. sourcecode:: bash

    pip install sensirion-shdlc-driver

Recommended usage is within a virtualenv.


.. _firmware-updater-dependencies:

Firmware Updater Dependencies
-----------------------------

The firmware updater has additional dependencies which are not installed by
default because not all devices support firmware updates. They can be
installed explicitly with the ``fwupdate`` extra:

.. sourcecode:: bash

    pip install sensirion-shdlc-driver[fwupdate]

However, device-specific drivers which support firmware updates will add the
``fwupdate`` extra to their dependencies anyway, so usually you don't have to
care about this.
