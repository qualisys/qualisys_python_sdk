'''
    Tests for QTMProtocol
'''

import asyncio

import pytest

from qtm.protocol import QTMProtocol, QRTCommandException
from qtm.packet import QRTEvent, RTEvent


@pytest.fixture
def qtmprotocol():
    return QTMProtocol(asyncio.get_event_loop())


@pytest.mark.asyncio
async def test_send_command_not_connected(qtmprotocol):  #pylint: disable=W0621

    with pytest.raises(QRTCommandException):
        await qtmprotocol.send_command('dummy')


@pytest.mark.asyncio
async def test_await_any_event_timeout(qtmprotocol):  #pylint: disable=W0621
    awaitable = qtmprotocol.await_event(timeout=0.1)
    with pytest.raises(asyncio.TimeoutError):
        await awaitable


def _create_event_data(event):
    return RTEvent.pack(chr(event.value).encode())


@pytest.mark.asyncio
async def test_await_any_event(event_loop, qtmprotocol):  #pylint: disable=W0621
    data = _create_event_data(QRTEvent.EventConnected)

    awaitable = qtmprotocol.await_event(timeout=1)
    event_loop.call_later(0, lambda: qtmprotocol._on_event(data))
    result = await awaitable

    assert result == QRTEvent.EventConnected


@pytest.mark.asyncio
async def test_await_specific_event(event_loop, qtmprotocol):  #pylint: disable=W0621
    data = _create_event_data(QRTEvent.EventConnected)

    awaitable = qtmprotocol.await_event(
        event=QRTEvent.EventConnected, timeout=1)
    event_loop.call_later(0, lambda: qtmprotocol._on_event(data))
    result = await awaitable

    assert result == QRTEvent.EventConnected


@pytest.mark.asyncio
async def test_await_event_multiple(event_loop, qtmprotocol):  #pylint: disable=W0621
    data1 = _create_event_data(QRTEvent.EventConnectionClosed)
    data2 = _create_event_data(QRTEvent.EventConnected)

    awaitable = qtmprotocol.await_event(
        event=QRTEvent.EventConnected, timeout=1)

    event_loop.call_later(0, lambda: qtmprotocol._on_event(data1))
    event_loop.call_later(0.1, lambda: qtmprotocol._on_event(data2))

    result = await awaitable

    assert result == QRTEvent.EventConnected


@pytest.mark.asyncio
async def test_await_multiple(qtmprotocol):  #pylint: disable=W0621
    awaitable1 = qtmprotocol.await_event(event=QRTEvent.EventConnected)
    awaitable2 = qtmprotocol.await_event(event=QRTEvent.EventConnectionClosed)

    done, _ = await asyncio.wait(
        [awaitable1, awaitable2], return_when=asyncio.FIRST_EXCEPTION)

    print(done)

    with pytest.raises(Exception):
        done.pop().result()
