"""
    Tests for connect and QRTConnection
"""

import asyncio

import pytest

from qtm.qrt import QRTConnection, connect
from qtm.protocol import QTMProtocol, QRTCommandException


# pylint: disable=W0621, C0111, C0330, E1101, W0212


@pytest.mark.parametrize("exception", [ConnectionRefusedError, TimeoutError, OSError])
@pytest.mark.asyncio
async def test_connect_connection_fail(exception, event_loop, mocker):
    mocker.patch.object(
        event_loop, "create_connection", mocker.MagicMock(side_effect=exception)
    )
    result = await connect("192.0.2.0")
    assert result is None


@pytest.mark.asyncio
async def test_connect_no_loop(event_loop, mocker):
    mocker.patch("asyncio.get_event_loop", mocker.MagicMock(return_value=event_loop))

    mocker.patch.object(
        event_loop,
        "create_connection",
        mocker.MagicMock(side_effect=ConnectionRefusedError),
    )

    await connect("192.0.2.0")
    assert asyncio.get_event_loop.call_count == 1


@pytest.mark.asyncio
async def test_connect_loop(event_loop, mocker):
    mocker.patch("asyncio.get_event_loop", mocker.MagicMock())

    mocker.patch.object(
        event_loop,
        "create_connection",
        mocker.MagicMock(side_effect=ConnectionRefusedError),
    )

    await connect("192.0.2.0", loop=event_loop)
    assert asyncio.get_event_loop.call_count == 0


@pytest.mark.asyncio
async def test_connect_set_version(event_loop, mocker):
    protocol = mocker.MagicMock()

    async def side_effect(*_):
        return None, protocol

    mocker.patch.object(
        event_loop, "create_connection", mocker.MagicMock(side_effect=side_effect)
    )

    await connect("192.0.2.0")
    assert protocol.set_version.call_count == 1


@pytest.mark.asyncio
async def test_connect_success(event_loop, mocker):
    async def set_version(*_):
        pass

    async def side_effect(*_):
        return None, protocol

    protocol = mocker.MagicMock()
    protocol.set_version = set_version

    mocker.patch.object(
        event_loop, "create_connection", mocker.MagicMock(side_effect=side_effect)
    )

    connection = await connect("192.0.2.0")

    assert isinstance(connection, QRTConnection)


async def async_function(*_, **__):
    pass


@pytest.fixture
def a_qrt(mocker):
    protocol = mocker.MagicMock(
        spec=QTMProtocol, name="QTMProtocol", side_effect=async_function
    )
    protocol.transport = mocker.MagicMock(name="transport")
    protocol.send_command.side_effect = async_function
    protocol.await_event.side_effect = async_function
    return QRTConnection(protocol, 5)


def test_disconnect(a_qrt):
    a_qrt.disconnect()
    assert a_qrt._protocol.transport.close.call_count == 1


@pytest.mark.asyncio
async def test_qtm_version(a_qrt):
    await a_qrt.qtm_version()
    a_qrt._protocol.send_command.assert_called_once_with("qtmversion")


@pytest.mark.asyncio
async def test_byte_order(a_qrt):
    await a_qrt.byte_order()
    a_qrt._protocol.send_command.assert_called_once_with("byteorder")


@pytest.mark.asyncio
async def test_get_state(a_qrt):
    await a_qrt.get_state()

    a_qrt._protocol.send_command.assert_called_once_with("getstate", callback=False)
    assert a_qrt._protocol.await_event.call_count == 1


@pytest.mark.asyncio
async def test_get_parameters_none(a_qrt):
    await a_qrt.get_parameters()
    a_qrt._protocol.send_command.assert_called_once_with("getparameters all")


@pytest.mark.asyncio
async def test_get_parameters_fail(a_qrt):
    with pytest.raises(QRTCommandException):
        await a_qrt.get_parameters(parameters=["fail"])


@pytest.mark.parametrize(
    "parameters",
    [
        ["all"],
        ["general"],
        ["3d"],
        ["6d"],
        ["analog"],
        ["force"],
        ["gazevector"],
        ["image"],
        ["general", "3d"],
        ["general", "3d", "analog"],
    ],
)
@pytest.mark.asyncio
async def test_get_parameters(parameters, a_qrt):
    await a_qrt.get_parameters(parameters=parameters)

    a_qrt._protocol.send_command.assert_called_once_with(
        "getparameters {}".format(" ".join(parameters))
    )


@pytest.mark.parametrize(
    "components",
    [
        ["2D"],
        ["2DLin"],
        ["3D"],
        ["3DRes"],
        ["3DNoLabels"],
        ["3DNoLabelsRes"],
        ["Analog"],
        ["AnalogSingle"],
        ["Force"],
        ["ForceSingle"],
        ["6D"],
        ["6DRes"],
        ["6DEuler"],
        ["6DEulerRes"],
        ["GazeVector"],
        ["Image"],
        ["Timecode"],
    ],
)
@pytest.mark.asyncio
async def test_stream_frames(components, a_qrt):
    await a_qrt.stream_frames(components=components)

    a_qrt._protocol.send_command.assert_called_once_with(
        "streamframes {} {}".format("allframes", " ".join(components))
    )


@pytest.mark.asyncio
async def test_stream_frames_fail(a_qrt):
    with pytest.raises(QRTCommandException):
        await a_qrt.stream_frames(components=["fail"])


@pytest.mark.asyncio
async def test_stream_frames_stop(a_qrt):
    await a_qrt.stream_frames_stop()
    a_qrt._protocol.send_command.assert_called_once_with(
        "streamframes stop", callback=False
    )


@pytest.mark.asyncio
async def test_take_control(a_qrt):
    async def got_control(*_):
        return b"You are now master"

    a_qrt._protocol.send_command.side_effect = got_control

    password = "password"
    await a_qrt.take_control(password)
    a_qrt._protocol.send_command.assert_called_once_with(
        "takecontrol {}".format(password)
    )


@pytest.mark.asyncio
async def test_take_control_fail(a_qrt):
    async def no_control(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = no_control

    password = "password"
    with pytest.raises(QRTCommandException):
        await a_qrt.take_control(password)

    a_qrt._protocol.send_command.assert_called_once_with(
        "takecontrol {}".format(password)
    )


@pytest.mark.asyncio
async def test_release_control(a_qrt):
    async def release_control(*_):
        return b"You are now a regular client"

    a_qrt._protocol.send_command.side_effect = release_control

    await a_qrt.release_control()
    a_qrt._protocol.send_command.assert_called_once_with("releasecontrol")


@pytest.mark.asyncio
async def test_release_control_fail(a_qrt):
    async def no_control(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = no_control

    with pytest.raises(QRTCommandException):
        await a_qrt.release_control()

    a_qrt._protocol.send_command.assert_called_once_with("releasecontrol")


@pytest.mark.asyncio
async def test_new(a_qrt):
    async def new(*_):
        return b"Creating new connection"

    a_qrt._protocol.send_command.side_effect = new
    await a_qrt.new()
    a_qrt._protocol.send_command.assert_called_once_with("new")


@pytest.mark.asyncio
async def test_new_fail(a_qrt):
    async def fail(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = fail

    with pytest.raises(QRTCommandException):
        await a_qrt.new()

    a_qrt._protocol.send_command.assert_called_once_with("new")


@pytest.mark.asyncio
async def test_calibrate(a_qrt):
    async def calibrate(*_):
        return b"Starting calibration"

    async def xml(*_):
        return b"XML"

    a_qrt._protocol.send_command.side_effect = calibrate
    a_qrt._protocol.receive_response.side_effect = xml

    response = await a_qrt.calibrate()

    if response != b"XML":
        pytest.fail("Calibration result error")

    a_qrt._protocol.send_command.assert_called_once_with("calibrate")



@pytest.mark.asyncio
async def test_calibrate_fail(a_qrt):
    async def calibrate(*_):
        return b"Can not start calibration"

    async def xml(*_):
        return b"XML"

    a_qrt._protocol.send_command.side_effect = calibrate
    a_qrt._protocol.receive_response.side_effect = xml

    with pytest.raises(QRTCommandException):
        response = await a_qrt.calibrate()

    a_qrt._protocol.send_command.assert_called_once_with("calibrate")


@pytest.mark.asyncio
async def test_close(a_qrt):
    async def close(*_):
        return b"Closing connection"

    a_qrt._protocol.send_command.side_effect = close
    await a_qrt.close()
    a_qrt._protocol.send_command.assert_called_once_with("close")


@pytest.mark.asyncio
async def test_close_fail(a_qrt):
    async def fail(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = fail

    with pytest.raises(QRTCommandException):
        await a_qrt.close()

    a_qrt._protocol.send_command.assert_called_once_with("close")


@pytest.mark.asyncio
async def test_start(a_qrt):
    async def start(*_):
        return b"Starting measurement"

    a_qrt._protocol.send_command.side_effect = start
    await a_qrt.start()
    a_qrt._protocol.send_command.assert_called_once_with("start")


@pytest.mark.asyncio
async def test_start_rtfromfile(a_qrt):
    async def start(*_):
        return b"Starting RT from file"

    a_qrt._protocol.send_command.side_effect = start
    await a_qrt.start(rtfromfile=True)
    a_qrt._protocol.send_command.assert_called_once_with("start rtfromfile")


@pytest.mark.asyncio
async def test_start_fail(a_qrt):
    async def fail(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = fail

    with pytest.raises(QRTCommandException):
        await a_qrt.start()

    a_qrt._protocol.send_command.assert_called_once_with("start")


@pytest.mark.asyncio
async def test_stop(a_qrt):
    async def stop(*_):
        return b"Stopping measurement"

    a_qrt._protocol.send_command.side_effect = stop
    await a_qrt.stop()
    a_qrt._protocol.send_command.assert_called_once_with("stop")


@pytest.mark.asyncio
async def test_stop_fail(a_qrt):
    async def fail(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = fail

    with pytest.raises(QRTCommandException):
        await a_qrt.stop()

    a_qrt._protocol.send_command.assert_called_once_with("stop")


@pytest.mark.asyncio
async def test_load(a_qrt):
    async def load(*_):
        return b"Measurement loaded"

    filename = "test"

    a_qrt._protocol.send_command.side_effect = load
    await a_qrt.load(filename)
    a_qrt._protocol.send_command.assert_called_once_with("load {}".format(filename))


@pytest.mark.asyncio
async def test_load_fail(a_qrt):
    async def fail(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = fail

    with pytest.raises(QRTCommandException):
        await a_qrt.load("fail")


@pytest.mark.asyncio
async def test_save(a_qrt):
    async def save(*_):
        return b"Measurement saved"

    filename = "test"

    a_qrt._protocol.send_command.side_effect = save
    await a_qrt.save(filename)
    a_qrt._protocol.send_command.assert_called_once_with("save {}".format(filename))


@pytest.mark.asyncio
async def test_save_fail(a_qrt):
    async def fail(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = fail

    with pytest.raises(QRTCommandException):
        await a_qrt.load("fail")


@pytest.mark.asyncio
async def test_loadproject(a_qrt):
    async def loadproject(*_):
        return b"Project loaded"

    filename = "test"

    a_qrt._protocol.send_command.side_effect = loadproject
    await a_qrt.load_project(filename)
    a_qrt._protocol.send_command.assert_called_once_with(
        "loadproject {}".format(filename)
    )


@pytest.mark.asyncio
async def test_loadproject_fail(a_qrt):
    async def fail(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = fail

    with pytest.raises(QRTCommandException):
        await a_qrt.load_project("fail")


@pytest.mark.asyncio
async def test_trig(a_qrt):
    async def trig(*_):
        return b"Trig ok"

    a_qrt._protocol.send_command.side_effect = trig
    await a_qrt.trig()
    a_qrt._protocol.send_command.assert_called_once_with("trig")


@pytest.mark.asyncio
async def test_trig_fail(a_qrt):
    async def fail(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = fail

    with pytest.raises(QRTCommandException):
        await a_qrt.trig()


@pytest.mark.asyncio
async def test_set_qtm_event(a_qrt):
    async def set_qtm_event(*_):
        return b"Event set"

    a_qrt._protocol.send_command.side_effect = set_qtm_event
    await a_qrt.set_qtm_event()
    a_qrt._protocol.send_command.assert_called_once_with("event")


@pytest.mark.asyncio
async def test_set_qtm_event_name(a_qrt):
    async def set_qtm_event(*_):
        return b"Event set"

    event = "test"

    a_qrt._protocol.send_command.side_effect = set_qtm_event
    await a_qrt.set_qtm_event(event)
    a_qrt._protocol.send_command.assert_called_once_with("event {}".format(event))


@pytest.mark.asyncio
async def test_set_qtm_event_fail(a_qrt):
    async def fail(*_):
        return b"Fail"

    a_qrt._protocol.send_command.side_effect = fail

    with pytest.raises(QRTCommandException):
        await a_qrt.set_qtm_event()


# TODO XML test
