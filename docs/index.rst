.. Qualisys Realtime SDK for Python documentation master file, created by
   sphinx-quickstart on Mon Oct  3 09:58:46 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Qualisys SDK for Python's documentation!
===================================================

This document describes the Qualisys SDK for Python 2.0.

**Version 2.0 introduces breaking changes**. The basic functionality is the same, but the package now 
uses `asyncio <https://docs.python.org/3.5/library/asyncio.html>`_ instead of `twisted <https://twistedmatrix.com/>`_. 
This reduces dependencies and simplifies installation but raises the required version of Python to 3.5.
If you cannot use Python 3, stay on the earlier versions of this SDK.


Example usage:
--------------

The following code demonstrates how to stream 3D markers from QTM. To keep the code short, it assumes that QTM is
already streaming data, either live or RT from file.

.. literalinclude:: ../examples/basic_example.py

.. toctree::
   :maxdepth: 2

QTM RT Protocol
---------------

An instance of QRTConnection is returned when qtm.connect_ successfully connects to QTM.

Functions marked as coroutines need to be run in a async function and awaited, please see example above.

.. autocofunction:: qtm.connect

QRTConnection
~~~~~~~~~~~~~

.. autoclass:: qtm.QRTConnection
    :members:

QRTPacket
~~~~~~~~~

.. autoclass:: qtm.QRTPacket
    :members:

QRTEvent
~~~~~~~~~

.. autoclass:: qtm.QRTEvent
    :members:
    :undoc-members:

QRTComponentType
~~~~~~~~~~~~~~~~

.. autoclass:: qtm.packet.QRTComponentType
    :members:
    :undoc-members:    

Exceptions
~~~~~~~~~~

.. autoclass:: qtm.QRTCommandException

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

