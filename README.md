# Qualisys SDK for Python

The Qualisys SDK for Python implements our real-time (RT) and REST protocols, and works with both Python 2.7 and 3+.

## Installation

The Qualisys SDK for Python is available as a package named *qtm* that can be installed using [pip](https://pip.pypa.io/en/stable/installing/):

    python -m pip install pip --upgrade # Upgrade to latest pip
    python -m pip install qtm

The package can also be installed from the source on GitHub:

    python -m pip install git+https://github.com/qualisys/qualisys_python_sdk.git

You can also clone the repo on your local machine and copy the *qtm* folder into you project folder. (This will require that you install  dependencies manually.)

## Dependencies

* twisted > 16.4.1 (Lower version will probably work fine, but not with python 3)
* enum34 for Python versions lower than 3.4
* pywin32 for windows (can be installed with pip as pypiwin32)

## Documentation

Documentation is available at: https://qualisys.github.io/qualisys_python_sdk/v103/index.html

## Examples

Example scripts can be found in the *examples* folder.

## Caveats

- Implementation only uses little endian, should connect to standard port 22223.  
- Version should be at least 1.13.
- GetCaptureC3D is not implemented.  
- GetCaptureQTM is not implemented.
- No support for selecting analog channel.
