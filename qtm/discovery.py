""" Implementation of QTM discovery protocol """

import struct
import asyncio
from collections import namedtuple
import logging

from .protocol import RTheader, QRTPacketType

# pylint: disable=C0103

LOG = logging.getLogger("qtm")

QRTDiscoveryP1 = struct.Struct("<II")
QRTDiscoveryP2 = struct.Struct(">H")
QRTDiscoveryPacketSize = QRTDiscoveryP1.size + QRTDiscoveryP2.size
QRTDiscoveryBasePort = struct.Struct(">H")

QRTDiscoveryResponse = namedtuple("QRTDiscoveryResponse", "info host port")

class QRTDiscoveryProtocol:
    """ Oqus/Miqus/Arqus discovery protocol implementation"""

    def __init__(self, receiver=None):
        self.port = None
        self.receiver = receiver
        self.transport = None

    def connection_made(self, transport):
        """ On socket creation """
        self.transport = transport

        sock = transport.get_extra_info("socket")
        self.port = sock.getsockname()[1]

    def datagram_received(self, datagram, address):
        """ Parse response from QTM instances """
        size, _ = RTheader.unpack_from(datagram, 0)
        info, = struct.unpack_from("{0}s".format(size - 3 - 8), datagram, RTheader.size)
        base_port, = QRTDiscoveryBasePort.unpack_from(datagram, size - 2)

        if self.receiver is not None:
            self.receiver(QRTDiscoveryResponse(info, address[0], base_port))

    def send_discovery_packet(self):
        """ Send discovery packet for QTM to respond to """
        if self.port is None:
            return

        self.transport.sendto(
            QRTDiscoveryP1.pack(
                QRTDiscoveryPacketSize, QRTPacketType.PacketDiscover.value
            )
            + QRTDiscoveryP2.pack(self.port),
            ("<broadcast>", 22226),
        )

class Discover:
    """async discovery of qtm instances"""

    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.queue = asyncio.Queue()
        self.first = True

    def __aiter__(self):
        return self

    async def __anext__(self) -> QRTDiscoveryResponse:

        loop = asyncio.get_event_loop()
        if self.first:

            protocol_factory = lambda: QRTDiscoveryProtocol(
                receiver=self.queue.put_nowait
            )

            _, protocol = await loop.create_datagram_endpoint(
                protocol_factory,
                local_addr=(self.ip_address, 0),
                allow_broadcast=True,
            )

            LOG.debug("Sending discovery packet on %s", self.ip_address)
            protocol.send_discovery_packet()
            self.first = False

        call_handle = loop.call_later(0.2, lambda: self.queue.put_nowait(None))
        result = await self.queue.get()
        if result is None:
            LOG.debug("Discovery timed out")
            raise StopAsyncIteration

        LOG.debug(result)
        call_handle.cancel()
        return result


