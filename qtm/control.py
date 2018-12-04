import asyncio
import logging

from .qrt import QRTConnection

LOG = logging.getLogger("qtm")


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
