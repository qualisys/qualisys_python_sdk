Qualisys SDK for Python
================================

![PyPI - Version](https://img.shields.io/pypi/v/qtm_rt)

The Qualisys SDK for Python implements our RealTime(RT) protocol and works with Python 3.10 and above.

Installation
------------

The easiest way to install the qtm_rt package is by using [pip]((https://pip.pypa.io/en/stable/installing/)):

```
python -m pip install pip --upgrade # Upgrade to latest pip
python -m pip install qtm-rt
```

It's also possible to install from github:

```
python -m pip install git+https://github.com/qualisys/qualisys_python_sdk.git
```

Or just clone the repo and copy the qtm_rt folder into you project folder,

Documentation
-------------

https://qualisys.github.io/qualisys_python_sdk/index.html

Examples
--------

See the examples folder. Some examples load a `Demo.qtm` recording — it ships
alongside the example scripts in this repo, and is also attached to each
[GitHub Release](https://github.com/qualisys/qualisys_python_sdk/releases)
for users who installed via pip.

Logging
-------

The SDK logs through the standard `logging` module under the `qtm_rt` logger
and does not emit any output on its own. Call `logging.basicConfig()` (or
attach a handler to the `qtm_rt` logger) in your application to see the
messages:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Setting the environment variable `QTM_LOGGING=debug` lowers the `qtm_rt`
logger's threshold to `DEBUG`. It does not, by itself, produce output —
configure a handler as above.

Missing RT features and limitations
-----------------------------------

Implementation only uses little endian, should connect to standard port 22223.
Protocol version must be 1.8 or later.

GetCaptureC3D is not implemented.
GetCaptureQTM is not implemented.

No support for selecting analog channel.

Development
-----------

Use the following `bash` commands in sequence to build the distribution and
documentation:

```
# Setup build environment
python -m venv .venv
source ./.venv/Scripts/activate
pip install -r requirements-dev.txt

# Run tests
pytest test/

# Build source tarball and python wheel in dist/
python -m build

# Check the built distributions
twine check dist/*

# Build sphinx documentation in docs/_build/html/
make -C docs html

# Copy build output to gh-pages branch (checked out in a separate clone of the repository in ../qualisys_python_sdk_gh_pages)
# Make sure to keep v102/, v103/ and v212/ directories with the old documentation.
cp -r docs/_build/html/* ../qualisys_python_sdk_gh_pages
# Commit the changes with a message like "Update documentation to version x.y.z"
git -C ../qualisys_python_sdk_gh_pages add .
git -C ../qualisys_python_sdk_gh_pages commit
git -C ../qualisys_python_sdk_gh_pages push origin gh-pages

# Git tag and make a release on GitHub
git tag vx.y.z
git push --tags
```

Publishing
----------

Releases are published automatically to https://pypi.org/project/qtm-rt/ when a
GitHub release is published.

Before using the release workflow for the first time, configure PyPI Trusted
Publishing for the `qtm-rt` project:

```
Owner: qualisys
Repository name: qualisys_python_sdk
Workflow filename: release.yml
Environment name: pypi
```

The package version is defined in `pyproject.toml`. Update it before tagging
and publishing a GitHub release.
