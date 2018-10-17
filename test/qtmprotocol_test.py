"""
    Tests for QTMProtocol
"""

import asyncio

import pytest

from qtm.protocol import QTMProtocol, QRTCommandException
from qtm.packet import QRTEvent, RTEvent

# pylint: disable=W0621, C0111, W0212


@pytest.fixture
def qtmprotocol(event_loop) -> QTMProtocol:
    return QTMProtocol(loop=event_loop)


@pytest.mark.asyncio
async def test_send_command_not_connected(qtmprotocol: QTMProtocol):

    with pytest.raises(QRTCommandException):
        await qtmprotocol.send_command("dummy")


@pytest.mark.asyncio
async def test_await_any_event_timeout(qtmprotocol: QTMProtocol):
    awaitable = qtmprotocol.await_event(timeout=0.1)
    with pytest.raises(asyncio.TimeoutError):
        await awaitable


@pytest.mark.asyncio
async def test_await_any_event(event_loop, qtmprotocol: QTMProtocol):
    awaitable = qtmprotocol.await_event(timeout=1)
    event_loop.call_later(0, lambda: qtmprotocol._on_event(QRTEvent.EventConnected))
    result = await awaitable

    assert result == QRTEvent.EventConnected


@pytest.mark.asyncio
async def test_await_specific_event(event_loop, qtmprotocol: QTMProtocol):
    awaitable = qtmprotocol.await_event(event=QRTEvent.EventConnected, timeout=1)
    event_loop.call_later(0, lambda: qtmprotocol._on_event(QRTEvent.EventConnected))
    result = await awaitable

    assert result == QRTEvent.EventConnected


@pytest.mark.asyncio
async def test_await_event_multiple(event_loop, qtmprotocol: QTMProtocol):
    awaitable = qtmprotocol.await_event(event=QRTEvent.EventConnected, timeout=1)

    event_loop.call_later(
        0, lambda: qtmprotocol._on_event(QRTEvent.EventConnectionClosed)
    )
    event_loop.call_later(0.1, lambda: qtmprotocol._on_event(QRTEvent.EventConnected))

    result = await awaitable

    assert result == QRTEvent.EventConnected


@pytest.mark.asyncio
async def test_await_multiple(qtmprotocol: QTMProtocol):
    awaitable1 = qtmprotocol.await_event(event=QRTEvent.EventConnected)
    awaitable2 = qtmprotocol.await_event(event=QRTEvent.EventConnectionClosed)

    done, _ = await asyncio.wait(
        [awaitable1, awaitable2], return_when=asyncio.FIRST_EXCEPTION
    )

    print(done)

    with pytest.raises(Exception):
        done.pop().result()
