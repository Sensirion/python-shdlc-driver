CHANGELOG
---------

0.1.4
:::::
- Make signature and version offset configurable for ``ShdlcFirmwareImage``

0.1.3
:::::
- Add property ``is_open`` to ``ShdlcPort``, ``ShdlcSerialPort`` and
  ``ShdlcTcpPort``
- Improve/extend documentation

0.1.2
:::::
- Add ``ShdlcTcpPort`` class to communicate with SHDLC devices through TCP/IP
- Add property ``start_received`` to ``ShdlcSerialMisoFrameBuilder``
- Add methods ``open()`` and ``close()`` to the ``ShdlcPort`` interface
- Add parameter ``do_open`` to constructor of ``ShdlcSerialPort`` to allow
  creating ``ShdlcSerialPort`` instances without opening the port yet
- Add property ``additional_response_time`` to ``ShdlcSerialPort``
- Improve timeout calculation of ``ShdlcSerialPort`` to fix possible response
  timeout errors
- Make ``FirmwareUpdate`` failing early if the bitrate cannot be changed

0.1.1
:::::
- Add optional dependency ``intelhex`` for performing firmware updates
- Add bootloader commands: ``ShdlcCmdBootloaderBase``,
  ``ShdlcCmdEnterBootloader``, ``ShdlcCmdFirmwareUpdateStart``,
  ``ShdlcCmdFirmwareUpdateData``, ``ShdlcCmdFirmwareUpdateStop``
- Add exceptions for the firmware updater:
  ``ShdlcFirmwareImageSignatureError``,
  ``ShdlcFirmwareImageIncompatibilityError``
- Add classes to perform firmware updates over SHDLC: ``ShdlcFirmwareImage``,
  ``ShdlcFirmwareUpdate``
- Add property ``lock`` to the ``ShdlcPort`` interface to allow locking the
  port from outside the class

0.1.0
:::::
- Initial release
