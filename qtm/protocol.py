"""
    QTM RT Protocol implementation
"""

import asyncio
import struct
import collections
import logging

from qtm.packet import QRTPacketType
from qtm.packet import QRTPacket, QRTEvent
from qtm.packet import RTheader, RTEvent, RTCommand
from qtm.receiver import Receiver

# pylint: disable=C0330

LOG = logging.getLogger("qtm")


class QRTCommandException(Exception):
    """
        Basic RT Command Exception
    """

    def __init__(self, value):
        super(QRTCommandException, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class QTMProtocol(asyncio.Protocol):
    """
        QTM RT Protocol implementation
        Should be constructed by ::qrt.connect
    """

    def __init__(self, *, loop=None, on_disconnect=None, on_event=None):
        self._received_data = b""

        self.on_disconnect = on_disconnect
        self.on_event = on_event
        self.on_packet = None

        self.request_queue = collections.deque()
        self.event_future = None
        self._start_streaming = False

        self.loop = loop or asyncio.get_event_loop()
        self.transport = None

        self._handlers = {
            QRTPacketType.PacketError: self._on_error,
            QRTPacketType.PacketData: self._on_data,
            QRTPacketType.PacketCommand: self._on_command,
            QRTPacketType.PacketEvent: self._on_event,
            QRTPacketType.PacketXML: self._on_xml,
            QRTPacketType.PacketNoMoreData: lambda _: LOG.debug(
                QRTPacketType.PacketNoMoreData
            ),
        }

        self._receiver = Receiver(self._handlers)

    async def set_version(self, version):
        """ Set version of RT protocol used to communicate with QTM """
        version_cmd = "version %s" % version
        # No need to check response, will throw if error
        await self.send_command(version_cmd)

    async def _wait_loop(self, event):
        while True:
            self.event_future = self.event_future or self.loop.create_future()
            result = await self.event_future

            if event is None or event == result:
                break
        return result

    async def await_event(self, event=None, timeout=None):
        """ Wait for any or specified event """
        if self.event_future is not None:
            raise Exception("Can't wait on multiple events!")

        result = await asyncio.wait_for(self._wait_loop(event), timeout)
        return result

    def send_command(
        self, command, callback=True, command_type=QRTPacketType.PacketCommand
    ):
        """ Sends commands to QTM """
        if self.transport is not None:
            cmd_length = len(command)
            LOG.debug("S: %s", command)
            self.transport.write(
                struct.pack(
                    RTCommand % cmd_length,
                    RTheader.size + cmd_length + 1,
                    command_type.value,
                    command.encode(),
                    b"\0",
                )
            )

            future = self.loop.create_future()
            if callback:
                self.request_queue.append(future)
            else:
                future.set_result(None)
            return future

        raise QRTCommandException("Not connected!")

    def receive_response(self):
        """ Sends commands to QTM """
        if self.transport is not None:
            future = self.loop.create_future()
            self.request_queue.append(future)
            return future

        raise QRTCommandException("Not connected!")

    def connection_made(self, transport):
        LOG.info("Connected")
        self.transport = transport

    def set_on_packet(self, on_packet):
        """ Set callback to use when packet arrives """
        self.on_packet = on_packet
        self._start_streaming = on_packet is not None

    def data_received(self, data):
        """ Received from QTM and route accordingly """
        self._receiver.data_received(data)

    def _deliver_promise(self, data):
        try:
            future = self.request_queue.pop()
            future.set_result(data)
        except IndexError:
            pass

    def _on_data(self, packet):
        if self.on_packet is not None:
            if self._start_streaming:
                self._deliver_promise(b"Ok")
                self._start_streaming = False

            self.on_packet(packet)
        else:
            self._deliver_promise(packet)
        return

    def _on_event(self, event):
        LOG.info(event)

        if self.event_future is not None:
            future, self.event_future = self.event_future, None
            future.set_result(event)

        if self.on_event:
            self.on_event(event)

    def _on_error(self, response):
        LOG.debug("Error: %s", response)
        if self._start_streaming:
            self.set_on_packet(None)
        try:
            future = self.request_queue.pop()
            future.set_exception(QRTCommandException(response))
        except IndexError:
            raise QRTCommandException(response)

    def _on_xml(self, response):
        LOG.debug("XML: %s ...", response[: min(len(response), 70)])
        self._deliver_promise(response)

    def _on_command(self, response):
        LOG.debug("R: %s", response)
        if response != b"QTM RT Interface connected":
            self._deliver_promise(response)

    def connection_lost(self, exc):
        self.transport = None
        LOG.info("Disconnected")
        if self.on_disconnect is not None:
            self.on_disconnect(exc)
