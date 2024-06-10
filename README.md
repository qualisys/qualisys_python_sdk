Qualisys SDK for Python
================================

The Qualisys SDK for Python implements our RealTime(RT) protocol and works with Python 3.5 and above.

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

See the examples folder.

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
pytest tests

# Build source tarball and python wheel in dist/
python -m build

# Build sphinx documentation in docs/_build/html/
make -C docs html

# Copy build output to gh-pages branch (checkout in separate repository)
cp -r docs/_build/html/* ../qualisys_python_sdk_gh_pages
git -C ../qualisys_python_sdk_gh_pages commit -m "Update documentation to version x.y.z"
git push origin gh-pages

# Upload new version to pypi.org (needs API key)
twine upload dist/*

# Git tag and manually make release on github
git tag vx.y.z
git push --tags
```
