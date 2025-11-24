# Python Driver for Sensirion SHDLC Devices

This repository contains the base driver for Sensirion SHDLC devices as a Python
package. For details, please read the package description in
[README.rst](https://github.com/Sensirion/python-shdlc-driver/blob/master/README.rst).

## Usage

See package description in [README.rst](https://github.com/Sensirion/python-shdlc-driver/blob/master/README.rst) and user manual at
https://sensirion.github.io/python-shdlc-driver/.

## Development

We develop and test this driver using our company internal tools (version
control, continuous integration, code review etc.) and automatically
synchronize the `master` branch with GitHub. But this doesn't mean that we
don't respond to issues or don't accept pull requests on GitHub. In fact,
you're very welcome to open issues or create pull requests :)

### Check coding style

The coding style can be checked with [`flake8`](http://flake8.pycqa.org/):

```bash
pip install -e .[test]  # Install requirements
flake8                  # Run style check
```

In addition, we check the formatting of files with
[`editorconfig-checker`](https://editorconfig-checker.github.io/):

```bash
pip install editorconfig-checker==2.0.3   # Install requirements
editorconfig-checker                      # Run check
```

### Run tests

Unit tests can be run with [`pytest`](https://pytest.org/):

```bash
pip install -e .[test]                          # Install requirements
pytest -m "not (needs_serialport or needs_tcp)" # Run tests without hardware
pytest                                          # Run all tests
```

To run the tests which access connected hardware, you need to pass following
arguments to `pytest`:

- `--serial-port`: The serial port where a device is connected (e.g. `COM7`)
- `--serial-bitrate`: The bitrate of the device connected to the serial port
  (e.g. `460800`)
- `--serial-address`: The slave address of the device connected to the serial
  port (e.g. `0`)
- `--tcp-port`: The TCP IP address where a device is connected (e.g.
  `192.168.100.209`)
- `--tcp-port`: The port of the device connected via TCP (e.g. `10001`)
- `--tcp-address`: The slave address of the device connected via TCP (e.g. `0`)


### Build documentation

The documentation can be built with [Sphinx](http://www.sphinx-doc.org/):

```bash
python setup.py install                        # Install package
pip install -r docs/requirements.txt           # Install requirements
sphinx-versioning build docs docs/_build/html  # Build documentation
```

## License

See [LICENSE](https://github.com/Sensirion/python-shdlc-driver/blob/master/LICENSE).
