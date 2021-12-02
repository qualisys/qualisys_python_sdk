Welcome to Qualisys SDK for Python's documentation!
===================================================

This document describes the Qualisys SDK for Python version 2.1.1

**NOTE:** Version 2.0.0 introduces breaking changes. :ref:`More info...<deprecated_version>`

.. contents::
    :depth: 2
    :local:

.. toctree::
    :hidden:

    deprecated.rst


Installation:
-------------

This package is a pure python package and requires at least Python 3.5.3, the easiest way to install it is:

.. code-block:: console

    python -m pip install qtm

Example usage:
--------------

The following code demonstrates how to stream 3D markers from QTM. To keep the code short, it assumes that QTM is
already streaming data, either live or RT from file.

.. literalinclude:: ../examples/basic_example.py


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

