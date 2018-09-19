.. _deprecated_version:

Upgrade information
-------------------

The basic functionality is the same, but the package now
uses `asyncio <https://docs.python.org/3.5/library/asyncio.html>`_ instead of `twisted <https://twistedmatrix.com/>`_.
This reduces dependencies and simplifies installation but raises the required version of Python to 3.5.
If you cannot use Python 3, stay on the earlier versions of this SDK.

QRest is still not implemented in 2.0.

To install the old version:

.. code-block:: console

    python -m pip install qtm==1.0.2