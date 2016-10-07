Qualisys Realtime SDK for Python
================================

Installation
------------

The easiest way to install the qtm package is by using [pip]((https://pip.pypa.io/en/stable/installing/)):

```
python -m pip install pip --upgrade # Upgrade to latest pip
python -m pip install qtm
```

It's also possible to install from github:

```
python -m pip install git+http://url
```

Or just clone the repo and copy the qtm folder into you project folder, 
although this will require you to install the dependencies manually.

Dependencies
------------

* twisted > 16.4.1 (Lower version will probably work fine, but not with python 3)
* enum34 for Python versions lower than 3.4
* pywin32 for windows (can be installed with pip as pypiwin32)

Missing RT features and limitations
-----------------------------------

Implementation only uses little endian, should connect to standard port 22223
Version should be at least 1.13

GetCaptureC3D is not implemented 
GetCaptureQTM is not implemented

No support for selecting analog channel