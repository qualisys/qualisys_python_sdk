Qualisys SDK for Python
================================

The Qualisys SDK for Python implements our RealTime(RT) protocol and works with Python 3.5 and above.

Installation
------------

The easiest way to install the qtm package is by using [pip]((https://pip.pypa.io/en/stable/installing/)):

```
python -m pip install pip --upgrade # Upgrade to latest pip
python -m pip install qtm
```

It's also possible to install from github:

```
python -m pip install git+https://github.com/qualisys/qualisys_python_sdk.git
```

Or just clone the repo and copy the qtm folder into you project folder,

Documentation
-------------

https://qualisys.github.io/qualisys_python_sdk/index.html

Examples
--------

See the examples folder.

Missing RT features and limitations
-----------------------------------

Implementation only uses little endian, should connect to standard port 22223.
Protocol version must be 1.8 or later.

GetCaptureC3D is not implemented.
GetCaptureQTM is not implemented.

No support for selecting analog channel.
