from .discovery import discover
from .reboot import reboot
from .qrt import connect, QRTConnection
from .packet import QRTPacket, QRTEvent
from .protocol import QRTCommandException
from .rest import QRest

import logging
import os

logger = logging.getLogger('qtm')
log = os.getenv('QTM_LOGGING', None)
if log is not None:

    level = logging.DEBUG if log == 'debug' else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class take_control(object):
    def __init__(self, connection, password):
        self.connection = connection
        self.password = password

    async def __aenter__(self):
        await self.connection.take_control(self.password)
        logger.info('Took control')

    async def __aexit__(self, exc_type, exc, tb):
        if self.connection._protocol.transport is not None:
            await self.connection.release_control()
            logger.info('Released control')


__author__ = 'mge'
