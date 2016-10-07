import struct
from enum import Enum

from twisted.internet import defer
from twisted.internet.protocol import Factory, Protocol

from qtm.packet import QRTPacketType, QRTPacket, QRTEvent


RTheader = struct.Struct("<II")
RTEvent = struct.Struct("<c")

RTCommand = "<II%dsc"


class QRTLoggerInfo(Enum):
    Sent = 0
    Received = 1
    Error = 2
    Event = 3


class QRTCommandException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# noinspection PyPep8Naming
class QRTProtocol(Protocol):
    def __init__(self, version, on_disconnect=None, on_event=None, logger=None):
        self.version_checked = False
        self.received_data = b''
        self.version = version

        self.on_disconnect = on_disconnect
        self.on_event = on_event
        self.logger = logger

        self.on_packet = None

        self.connected_d = defer.Deferred()

        self.request_queue = []

    @defer.inlineCallbacks
    def get_version(self):
        version_cmd = "Version %s" % self.version
        try:
            self.version_checked = True
            result = yield self.send_command(version_cmd)
        except QRTCommandException as e:
            self.connected_d.errback(e)
        else:
            self.connected_d.callback(result)


    def send_command(self, command, callback=True, command_type=QRTPacketType.PacketCommand):
        if self.logger:
            self.logger(command, QRTLoggerInfo.Sent)

        cmd_length = len(command)
        self.transport.write(struct.pack(RTCommand % cmd_length, RTheader.size + cmd_length + 1,
                                         command_type.value, command.encode(), b'\0'))
        d = None
        if callback:
            d = defer.Deferred()
            self.request_queue.append(d)

        return d


    def connectionMade(self):
        self.transport.setTcpNoDelay(True)

    def connectionLost(self, reason):
        if self.on_disconnect:
            self.on_disconnect(reason.getErrorMessage())

    def dataReceived(self, data):
        self.received_data += data
        h_size = RTheader.size

        data = self.received_data
        size, type_ = RTheader.unpack_from(data, 0)

        while len(data) >= size:
            self.parse_received(data[h_size:size], type_)
            data = data[size:]

            if len(data) < h_size:
                break

            size, type_ = RTheader.unpack_from(data, 0)

        self.received_data = data

    def set_on_packet(self, on_packet):
        self.on_packet = on_packet

    def parse_received(self, data, type_):
        type_ = QRTPacketType(type_)
        # print data, type_

        # never any callbacks
        if type_ == QRTPacketType.PacketEvent:
            event, = RTEvent.unpack(data)
            event = QRTEvent(ord(event))

            if self.logger:
                self.logger(event.name, QRTLoggerInfo.Event)

            if self.on_event:
                self.on_event(event)
            return

        # Get a deferred to return result
        d = self.request_queue.pop(0) if len(self.request_queue) > 0 else None

        if type_ == QRTPacketType.PacketError:
            response = data[:-1]
            if self.logger:
                self.logger(response, QRTLoggerInfo.Error)

            if d:
                d.errback(QRTCommandException(response))

        elif type_ == QRTPacketType.PacketXML:
            response = data[:-1]

            if d:
                d.callback(response)

        elif type_ == QRTPacketType.PacketCommand:
            response = data[:-1]

            if not self.version_checked:
                self.get_version()

            if self.logger:
                self.logger(response, QRTLoggerInfo.Received)

            if d:
                d.callback(response)

        elif type_ == QRTPacketType.PacketData:
            if d:
               d.callback('Ok')

            packet = QRTPacket(data)
            if self.on_packet:
                self.on_packet(packet)



class QRTFactory(Factory):
    protocol = QRTProtocol

    def __init__(self, version, on_disconnect=None, on_event=None, logger=None):
        self.version = version
        self.logger = logger

        self.on_disconnect = on_disconnect
        self.on_event = on_event

    def buildProtocol(self, addr):
        p = self.protocol(self.version, self.on_disconnect, self.on_event, self.logger)
        p.factory = self
        return p
