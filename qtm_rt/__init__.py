""" Python SDK for QTM """

import logging
import os

from .discovery import Discover
from .reboot import reboot
from .qrt import connect, QRTConnection
from .protocol import QRTCommandException
from .control import TakeControl
from .packet import QRTPacket, QRTEvent
from .receiver import Receiver

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
