""" Python SDK for QTM """

import logging
import os

from .control import TakeControl as TakeControl
from .discovery import Discover as Discover
from .packet import QRTEvent as QRTEvent
from .packet import QRTPacket as QRTPacket
from .protocol import QRTCommandException as QRTCommandException
from .qrt import QRTConnection as QRTConnection
from .qrt import connect as connect
from .reboot import reboot as reboot
from .receiver import Receiver as Receiver

# pylint: disable=C0330

LOG = logging.getLogger("qtm_rt")
LOG.addHandler(logging.NullHandler())

# Library logging hygiene (issue #44): the SDK never emits output on its own.
# QTM_LOGGING only lowers the qtm_rt logger's threshold. It does not attach
# handlers or emit anything — the application still owns all output. Setting a
# logger's level is benign (it affects only this logger); attaching handlers or
# calling logging.basicConfig() from a library is not, so we don't.
if os.getenv("QTM_LOGGING") == "debug":
    LOG.setLevel(logging.DEBUG)


__author__ = "mge"
