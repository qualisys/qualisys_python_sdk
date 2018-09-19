""" Python SDK for QTM """

import logging
import os

from .discovery import Discover
from .reboot import reboot
from .qrt import connect, QRTConnection
from .packet import QRTPacket, QRTEvent
from .protocol import QRTCommandException

# pylint: disable=C0330

LOG = logging.getLogger("qtm")
LOG_LEVEL = os.getenv("QTM_LOGGING", None)

LEVEL = logging.DEBUG if LOG_LEVEL == "debug" else logging.INFO
logging.basicConfig(
    level=LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class TakeControl:
    """ Context manager for taking control and releasing control of QTM """

    def __init__(self, connection: QRTConnection, password: str):
        self.connection = connection
        self.password = password

    async def __aenter__(self):
        await self.connection.take_control(self.password)
        LOG.info("Took control")

    async def __aexit__(self, exc_type, exc, _):
        if self.connection.has_transport() is not None:
            await self.connection.release_control()
            LOG.info("Released control")


__author__ = "mge"
