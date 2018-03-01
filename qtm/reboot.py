import socket
import asyncio
import logging

logger = logging.getLogger(__name__)

DEFAULT_DISCOVERY_PORT = 9930


async def reboot(ip_address):
    _, protocol = await asyncio.get_event_loop().create_datagram_endpoint(
        QRebootProtocol,
        local_addr=(ip_address, 0),
        allow_broadcast=True,
        reuse_address=True)

    logger.info('Sending reboot on %s', ip_address)
    protocol.send_reboot()


class QRebootProtocol(object):
    ''' Oqus/Miqus discovery protocol implementation'''

    def connection_made(self, transport):
        ''' On socket creation '''
        self.transport = transport

    def send_reboot(self):
        self.transport.sendto(b'reboot',
                              ('<broadcast>', DEFAULT_DISCOVERY_PORT))
