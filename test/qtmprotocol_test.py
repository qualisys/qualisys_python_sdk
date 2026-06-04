"""
    Tests for QTMProtocol
"""

import asyncio
from unittest.mock import MagicMock

import pytest

from qtm_rt.protocol import QTMProtocol, QRTCommandException
from qtm_rt.packet import QRTEvent

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
async def test_await_any_event(qtmprotocol: QTMProtocol):
    awaitable = qtmprotocol.await_event(timeout=1)
    asyncio.get_running_loop().call_later(0, lambda: qtmprotocol._on_event(QRTEvent.EventConnected))
    result = await awaitable

    assert result == QRTEvent.EventConnected


@pytest.mark.asyncio
async def test_await_specific_event(qtmprotocol: QTMProtocol):
    awaitable = qtmprotocol.await_event(event=QRTEvent.EventConnected, timeout=1)
    asyncio.get_running_loop().call_later(
        0, lambda: qtmprotocol._on_event(QRTEvent.EventConnected)
    )
    result = await awaitable

    assert result == QRTEvent.EventConnected


@pytest.mark.asyncio
async def test_await_event_multiple(qtmprotocol: QTMProtocol):
    awaitable = qtmprotocol.await_event(event=QRTEvent.EventConnected, timeout=1)

    asyncio.get_running_loop().call_later(
        0, lambda: qtmprotocol._on_event(QRTEvent.EventConnectionClosed)
    )
    asyncio.get_running_loop().call_later(
        0.1, lambda: qtmprotocol._on_event(QRTEvent.EventConnected)
    )

    result = await awaitable

    assert result == QRTEvent.EventConnected


@pytest.mark.asyncio
async def test_await_multiple(qtmprotocol: QTMProtocol):
    loop = asyncio.get_event_loop()
    awaitable1 = loop.create_task(qtmprotocol.await_event(event=QRTEvent.EventConnected))
    awaitable2 = loop.create_task(qtmprotocol.await_event(event=QRTEvent.EventConnectionClosed))

    done, _ = await asyncio.wait(
        [awaitable1, awaitable2], return_when=asyncio.FIRST_EXCEPTION
    )

    with pytest.raises(Exception):
        done.pop().result()


def _attach_transport(qtmprotocol: QTMProtocol):
    qtmprotocol.transport = MagicMock()


@pytest.mark.asyncio
async def test_responses_match_commands_in_fifo_order(qtmprotocol: QTMProtocol):
    _attach_transport(qtmprotocol)

    future_a = qtmprotocol.send_command("a")
    future_b = qtmprotocol.send_command("b")

    qtmprotocol._on_command(b"response_a")
    qtmprotocol._on_command(b"response_b")

    assert await future_a == b"response_a"
    assert await future_b == b"response_b"


@pytest.mark.asyncio
async def test_late_response_to_cancelled_future_does_not_crash(
    qtmprotocol: QTMProtocol,
):
    _attach_transport(qtmprotocol)

    cancelled_future = qtmprotocol.send_command("save")
    cancelled_future.cancel()

    later_future = qtmprotocol.send_command("releasecontrol")

    # Late response to "save" is dropped (caller gave up); next response goes to
    # "releasecontrol". Neither must raise InvalidStateError.
    qtmprotocol._on_command(b"Measurement saved")
    qtmprotocol._on_command(b"You are now a regular client")

    assert await later_future == b"You are now a regular client"


@pytest.mark.asyncio
async def test_unsolicited_error_does_not_raise(qtmprotocol: QTMProtocol):
    _attach_transport(qtmprotocol)

    # Empty request queue. Old behaviour raised QRTCommandException from inside
    # data_received and killed the transport.
    qtmprotocol._on_error(b"some unsolicited error")

    # Subsequent commands still work.
    future = qtmprotocol.send_command("a")
    qtmprotocol._on_command(b"response_a")
    assert await future == b"response_a"


@pytest.mark.asyncio
async def test_error_for_cancelled_future_does_not_raise(qtmprotocol: QTMProtocol):
    _attach_transport(qtmprotocol)

    # Error packet arrives for a command whose caller already gave up.
    # Must not raise InvalidStateError out of data_received.
    cancelled_future = qtmprotocol.send_command("save")
    cancelled_future.cancel()

    qtmprotocol._on_error(b"some error for the cancelled save")

    # Subsequent commands still work — transport was not torn down.
    future = qtmprotocol.send_command("a")
    qtmprotocol._on_command(b"response_a")
    assert await future == b"response_a"


@pytest.mark.asyncio
async def test_error_propagates_to_next_live_caller(qtmprotocol: QTMProtocol):
    _attach_transport(qtmprotocol)

    future = qtmprotocol.send_command("stop")
    qtmprotocol._on_error(b"No measurement is running")

    with pytest.raises(QRTCommandException):
        await future
