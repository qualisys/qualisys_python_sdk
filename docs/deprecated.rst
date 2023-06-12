.. _deprecated_version:

3.0.0
-------------------

The package has been renamed to qtm_rt (qtm-rt on pip). Otherwise everything is identical to 2.1.2.
Older versions will remain under the qtm name to avoid breaking existing code. 

To install the old version:

.. code-block:: console

    python -m pip install qtm==2.1.2

2.0.0
-------------------

The basic functionality is the same, but the package now
uses `asyncio <https://docs.python.org/3.5/library/asyncio.html>`_ instead of `twisted <https://twistedmatrix.com/>`_.
This reduces dependencies and simplifies installation but raises the required version of Python to 3.5.
If you cannot use Python 3, stay on the earlier versions of this SDK.

To install the old version:

.. code-block:: console

    python -m pip install qtm==1.0.2