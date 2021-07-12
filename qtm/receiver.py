import logging

from qtm.packet import QRTPacketType
from qtm.packet import QRTPacket, QRTEvent
from qtm.packet import RTheader, RTEvent, RTCommand

LOG = logging.getLogger("qtm")


class Receiver(object):
    def __init__(self, handlers):
        self._handlers = handlers
        self._received_data = b""

    def data_received(self, data):
        """ Received from QTM and route accordingly """
        self._received_data += data
        h_size = RTheader.size
        data = self._received_data
        data_len = len(data);

        while data_len >= h_size:
            size, type_ = RTheader.unpack_from(data, 0)
            if data_len >= size:
                self._parse_received(data[h_size:size], type_)
                data = data[size:]
                data_len = len(data);
            else:
                break;

        self._received_data = data

    def _parse_received(self, data, type_):
        type_ = QRTPacketType(type_)

        if (
            type_ == QRTPacketType.PacketError
            or type_ == QRTPacketType.PacketCommand
            or type_ == QRTPacketType.PacketXML
        ):
            data = data[:-1]
        elif type_ == QRTPacketType.PacketData:
            data = QRTPacket(data)
        elif type_ == QRTPacketType.PacketEvent:
            event, = RTEvent.unpack(data)
            data = QRTEvent(ord(event))

        try:
            self._handlers[type_](data)
        except KeyError:
            LOG.error("Non handled packet type! - %s", type_)
