CHANGELOG
---------

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
