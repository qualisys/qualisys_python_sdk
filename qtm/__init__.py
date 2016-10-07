from twisted.internet import reactor

from .discovery import QRTDiscoveryProtocol, QRTDiscoveryResponse
from .reboot import QRebootProtocol
from .packet import QRTPacket, QRTEvent
from .protocol import QRTCommandException, QRTLoggerInfo
from .qrt import QRT, QRTConnection
from .rest import QRest


def start():
    reactor.run()

def stop():
    reactor.stop()

def call_later(seconds, function, *args, **kwargs):
    reactor.callLater(seconds, function, *args, **kwargs)

__author__ = 'mge'
