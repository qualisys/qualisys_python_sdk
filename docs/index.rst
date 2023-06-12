Welcome to Qualisys SDK for Python's documentation!
===================================================

This document describes the Qualisys SDK for Python version 3.0.0

**NOTE:** Major versions introduces breaking changes. :ref:`More info...<deprecated_version>`

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

    python -m pip install qtm-rt

Example usage:
--------------

The following code demonstrates how to stream 3D markers from QTM. To keep the code short, it assumes that QTM is
already streaming data, either live or RT from file.

.. literalinclude:: ../examples/basic_example.py


QTM RT Protocol
---------------

An instance of QRTConnection is returned when qtm_rt.connect_ successfully connects to QTM.

Functions marked as coroutines need to be run in a async function and awaited, please see example above.

.. autocofunction:: qtm_rt.connect

QRTConnection
~~~~~~~~~~~~~

.. autoclass:: qtm_rt.QRTConnection
    :members:

QRTPacket
~~~~~~~~~

.. autoclass:: qtm_rt.QRTPacket
    :members:

QRTEvent
~~~~~~~~~

.. autoclass:: qtm_rt.QRTEvent
    :members:
    :undoc-members:

QRTComponentType
~~~~~~~~~~~~~~~~

.. autoclass:: qtm_rt.packet.QRTComponentType
    :members:
    :undoc-members:

Exceptions
~~~~~~~~~~

.. autoclass:: qtm_rt.QRTCommandException

