""" Implementation of QTM cameras reboot protocol """

import asyncio
import logging

LOG = logging.getLogger("qtm")

DEFAULT_DISCOVERY_PORT = 9930


async def reboot(ip_address):
    """ async function to reboot QTM cameras """
    _, protocol = await asyncio.get_event_loop().create_datagram_endpoint(
        QRebootProtocol,
        local_addr=(ip_address, 0),
        allow_broadcast=True,
    )

    LOG.info("Sending reboot on %s", ip_address)
    protocol.send_reboot()


class QRebootProtocol:
    """ Oqus/Miqus/Arqus discovery protocol implementation"""

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        """ On socket creation """
        self.transport = transport

    def send_reboot(self):
        """ Sends reboot package broadcast """
        self.transport.sendto(b"reboot", ("<broadcast>", DEFAULT_DISCOVERY_PORT))
