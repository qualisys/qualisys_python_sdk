import struct
from collections import namedtuple

from twisted.internet.protocol import DatagramProtocol

from .protocol import RTheader, QRTPacketType

QRTDiscoveryP1 = struct.Struct("<II")
QRTDiscoveryP2 = struct.Struct(">H")
QRTDiscoveryPacketSize = QRTDiscoveryP1.size + QRTDiscoveryP2.size
QRTDiscoveryBasePort = struct.Struct(">H")

QRTDiscoveryResponse = namedtuple('QRTDiscoveryResponse', 'info host port')


class QRTDiscoveryProtocol(DatagramProtocol):

    def __init__(self, receiver=None):
        self.port = None
        self.receiver = receiver

    def startProtocol(self):
        self.transport.setBroadcastAllowed(True)
        self.port = self.transport.getHost().port

    def send_discovery_packet(self):
        if self.port is None:
            return

        self.transport.write(QRTDiscoveryP1.pack(QRTDiscoveryPacketSize,
                             QRTPacketType.PacketDiscover.value) + QRTDiscoveryP2.pack(self.port),
                             ('<broadcast>', 22226))

    def datagramReceived(self, datagram, address):
        size, type_ = RTheader.unpack_from(datagram, 0)
        info, = struct.unpack_from("{0}s".format(size - 3 - 8), datagram, RTheader.size)
        base_port, = QRTDiscoveryBasePort.unpack_from(datagram, size-2)

        if self.receiver is not None:
            self.receiver(QRTDiscoveryResponse(info, address[0], base_port))
