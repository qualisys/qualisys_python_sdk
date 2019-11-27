.. Qualisys Realtime SDK for Python documentation master file, created by
   sphinx-quickstart on Mon Oct  3 09:58:46 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Qualisys SDK for Python's documentation!
===================================================

This document describes the Qualisys SDK for python. There are two parts:

   * `QTM RT Protocol`_
   * `QTM REST`_


.. toctree::
   :maxdepth: 2

.. module:: qtm

QTM RT Protocol
---------------

Implementation of the Qualisys RT protocol. For more information please see the RT document shipped with QTM.

QRT
~~~

.. autoclass:: qtm.QRT
    :members:

QRTConnection
~~~~~~~~~~~~~
.. _deferred: https://twistedmatrix.com/documents/current/core/howto/defer.html

All calls are asynchronous and return a deferred_.
Most methods also take two callback, on_ok and on_error, each receives one parameter, the result/error.

::

   def success(result):
      print(result)

   def fail(error):
      print(error)

   connection.qtm_version(on_ok=success, on_error=fail)



.. autoclass:: qtm.QRTConnection
    :members:

QRTPacket
~~~~~~~~~

.. autoclass:: qtm.QRTPacket
    :members:

QTM REST
--------

Implementation of the QTM REST interface. For more information see the REST document shipped with QTM.
PAF endpoints are not yet implemented.

QRest
~~~~~

All REST calls are asynchronous and return a deferred_.
All methods also take two callback, on_ok and on_error, each receives one parameter, the result/error.

::

   def success(settings):
      parse_settings(settings)

   def fail(error):
      print(error)

   qtm_rest.get_settings(on_ok=success, on_error=fail)


.. autoclass:: qtm.QRest
    :members:

\* Experimental endpoints. Behaviour might change without notice.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

