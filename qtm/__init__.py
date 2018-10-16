""" Python SDK for QTM """

import logging
import sys
import os

PYTHON3 = sys.version_info.major == 3

if PYTHON3:
    from .discovery import Discover
    from .reboot import reboot
    from .qrt import connect, QRTConnection
    from .protocol import QRTCommandException
    from .control import TakeControl

from .packet import QRTPacket, QRTEvent
from .receiver import Receiver

# pylint: disable=C0330

LOG = logging.getLogger("qtm")
LOG_LEVEL = os.getenv("QTM_LOGGING", None)

LEVEL = logging.DEBUG if LOG_LEVEL == "debug" else logging.INFO
logging.basicConfig(
    level=LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


__author__ = "mge"
