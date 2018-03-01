import asyncio
import struct
import collections
import logging

from qtm.packet import QRTPacketType
from qtm.packet import QRTPacket, QRTEvent
from qtm.packet import RTheader, RTEvent, RTCommand

logger = logging.getLogger(__name__)


class QRTCommandException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class QTMProtocol(asyncio.Protocol):
    def __init__(self, loop, on_disconnect=None, on_event=None):
        self._received_data = b''

        self.on_disconnect = on_disconnect
        self.on_event = on_event
        self.on_packet = None

        self.request_queue = collections.deque()
        self.event_future = None
        self._start_streaming = False

        self._handlers = {
            QRTPacketType.PacketError: self._on_error,
            QRTPacketType.PacketData: self._on_data,
            QRTPacketType.PacketCommand: self._on_command,
            QRTPacketType.PacketEvent: self._on_event,
            QRTPacketType.PacketXML: self._on_xml
        }

    async def set_version(self, version):
        version_cmd = "version %s" % version
        # No need to check response, will throw if error
        await self.send_command(version_cmd)

    async def _wait_loop(self, event):
        while True:
            self.event_future = asyncio.get_event_loop().create_future()
            result = await self.event_future

            if event is None or event == result:
                break
        return result

    async def await_event(self, event=None, timeout=None):
        if self.event_future is not None:
            raise Exception("Can't wait on multiple events!")

        result = await asyncio.wait_for(self._wait_loop(event), timeout)
        return result

    def send_command(self,
                     command,
                     callback=True,
                     command_type=QRTPacketType.PacketCommand):

        if self.transport is not None:
            cmd_length = len(command)
            logger.debug("S: %s", command)
            self.transport.write(
                struct.pack(RTCommand % cmd_length,
                            RTheader.size + cmd_length + 1, command_type.value,
                            command.encode(), b'\0'))

            future = None
            if callback:
                future = asyncio.get_event_loop().create_future()
                self.request_queue.append(future)
            return future

        raise QRTCommandException("Not connected!")

    def connection_made(self, transport):
        logger.info('Connected')
        self.transport = transport

    def set_on_packet(self, on_packet):
        self.on_packet = on_packet
        self._start_streaming = on_packet != None

    def data_received(self, data):
        self._received_data += data
        h_size = RTheader.size

        data = self._received_data
        size, type_ = RTheader.unpack_from(data, 0)

        while len(data) >= size:
            self.parse_received(data[h_size:size], type_)
            data = data[size:]

            if len(data) < h_size:
                break

            size, type_ = RTheader.unpack_from(data, 0)

        self._received_data = data

    def _deliver_promise(self, data):
        try:
            future = self.request_queue.pop()
            future.set_result(data)
        except IndexError:
            pass

    def _on_data(self, data):
        packet = QRTPacket(data)

        if self.on_packet is not None:
            if self._start_streaming:
                self._deliver_promise(b'Ok')
                self._start_streaming = False

            self.on_packet(packet)
        else:
            self._deliver_promise(packet)
        return

    def _on_event(self, data):
        event, = RTEvent.unpack(data)
        event = QRTEvent(ord(event))
        logger.info(event)

        if self.event_future is not None:
            future, self.event_future = self.event_future, None
            future.set_result(event)

        if self.on_event:
            self.on_event(event)

    def _on_error(self, data):
        response = data[:-1]
        logger.debug("Error: %s", response)
        if self._start_streaming:
            self.set_on_packet(None)
        try:
            future = self.request_queue.pop()
            future.set_exception(QRTCommandException(response))
        except IndexError:
            raise QRTCommandException(response)

    def _on_xml(self, data):
        response = data[:-1]
        logger.debug("XML: %s ...", data[:min(len(response), 70)])
        self._deliver_promise(data[:-1])

    def _on_command(self, data):
        response = data[:-1]
        logger.debug("R: %s", response)
        if response != b'QTM RT Interface connected':
            self._deliver_promise(response)

    def parse_received(self, data, type_):
        type_ = QRTPacketType(type_)
        try:
            self._handlers[type_](data)
        except KeyError:
            logger.error('Non handled packet type!')

    def connection_lost(self, exc):
        self.transport = None
        logger.info('Disconnected')
        if self.on_disconnect is not None:
            self.on_disconnect(exc)
