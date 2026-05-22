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

LOG = logging.getLogger("qtm_rt")

# Library logging hygiene: configure the qtm_rt logger only, never the root
# logger. The previous logging.basicConfig() call here mutated root config at
# import time, causing duplicate output for any application that also set up
# logging (issue #44).
if not LOG.handlers:
    LOG.setLevel(logging.DEBUG if os.getenv("QTM_LOGGING") == "debug" else logging.INFO)
    _qtm_rt_handler = logging.StreamHandler()
    _qtm_rt_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    LOG.addHandler(_qtm_rt_handler)


__author__ = "mge"
