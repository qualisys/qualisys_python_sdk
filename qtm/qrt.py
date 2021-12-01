""" QTM RT protocol implementation """

import asyncio
import logging
from functools import wraps

from qtm.packet import QRTPacketType, QRTPacket
from qtm.protocol import QTMProtocol, QRTCommandException

# pylint: disable=C0330

LOG = logging.getLogger("qtm")  # pylint: disable C0103


def validate_response(expected_responses):
    """ Decorator to validate responses from QTM """

    def internal_decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):

            response = await function(*args, **kwargs)

            for expected_response in expected_responses:
                if response.startswith(expected_response):
                    return response

            raise QRTCommandException(
                "Expected %s but got %s" % (expected_responses, response)
            )

        return wrapper

    return internal_decorator


class QRTConnection(object):
    """Represent a connection to QTM.

        Returned by :func:`~qtm.connect` when successfuly connected to QTM.
    """

    def __init__(self, protocol: QTMProtocol, timeout):
        super(QRTConnection, self).__init__()
        self._protocol = protocol
        self._timeout = timeout

    def disconnect(self):
        """Disconnect from QTM."""
        self._protocol.transport.close()

    def has_transport(self):
        """ Check if connected to QTM """
        return self._protocol.transport is not None

    async def qtm_version(self):
        """Get the QTM version.
        """
        return await asyncio.wait_for(
            self._protocol.send_command("qtmversion"), timeout=self._timeout
        )

    async def byte_order(self):
        """Get the byte order used when communicating
            (should only ever be little endian using this library).
        """
        return await asyncio.wait_for(
            self._protocol.send_command("byteorder"), timeout=self._timeout
        )

    async def get_state(self):
        """Get the latest state change of QTM. If the :func:`~qtm.connect` on_event
        callback was set the callback will be called as well.

        :rtype: A :class:`qtm.QRTEvent`
        """
        await self._protocol.send_command("getstate", callback=False)
        return await self._protocol.await_event()

    async def await_event(self, event=None, timeout=30):
        """Wait for an event from QTM.

        :param event: A :class:`qtm.QRTEvent`
            to wait for a specific event. Otherwise wait for any event.

        :param timeout: Max time to wait for event.

        :rtype: A :class:`qtm.QRTEvent`
        """
        return await self._protocol.await_event(event, timeout=timeout)

    async def get_parameters(self, parameters=None):
        """Get the settings for the requested component(s) of QTM in XML format.

        :param parameters: A list of parameters to request.
            Could be 'all' or any combination
            of 'general', '3d', '6d', 'analog', 'force', 'gazevector', 'eyetracker', 'image',
            'skeleton', 'skeleton:global', 'calibration'.
        :rtype: An XML string containing the requested settings.
            See QTM RT Documentation for details.
        """

        if parameters is None:
            parameters = ["all"]
        else:
            for parameter in parameters:
                if not parameter in [
                    "all",
                    "general",
                    "3d",
                    "6d",
                    "analog",
                    "force",
                    "gazevector",
                    "eyetracker",
                    "image",
                    "skeleton",
                    "skeleton:global",
                    "calibration",
                ]:
                    raise QRTCommandException("%s is not a valid parameter" % parameter)

        cmd = "getparameters %s" % " ".join(parameters)
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    async def get_current_frame(self, components=None) -> QRTPacket:
        """Get measured values from QTM for a single frame.

        :param components: A list of components to receive, could be any combination of
                '2d', '2dlin', '3d', '3dres', '3dnolabels',
                '3dnolabelsres', 'analog', 'analogsingle', 'force', 'forcesingle', '6d', '6dres',
                '6deuler', '6deulerres', 'gazevector', 'eyetracker', 'image', 'timecode',
                'skeleton', 'skeleton:global'

        :rtype: A :class:`qtm.QRTPacket` containing requested components
        """

        _validate_components(components)

        cmd = "getcurrentframe %s" % " ".join(components)
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    async def stream_frames(self, frames="allframes", components=None, on_packet=None):
        """Stream measured frames from QTM until :func:`~qtm.QRTConnection.stream_frames_stop`
           is called.


        :param frames: Which frames to receive, possible values are 'allframes',
            'frequency:n' or 'frequencydivisor:n' where n should be desired value.
        :param components: A list of components to receive, could be any combination of
                '2d', '2dlin', '3d', '3dres', '3dnolabels',
                '3dnolabelsres', 'analog', 'analogsingle', 'force', 'forcesingle', '6d', '6dres',
                '6deuler', '6deulerres', 'gazevector', 'eyetracker', 'image', 'timecode',
                'skeleton', 'skeleton:global'

        :rtype: The string 'Ok' if successful
        """

        _validate_components(components)

        self._protocol.set_on_packet(on_packet)

        cmd = "streamframes %s %s" % (frames, " ".join(components))
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    async def stream_frames_stop(self):
        """Stop streaming frames."""

        self._protocol.set_on_packet(None)

        cmd = "streamframes stop"
        await self._protocol.send_command(cmd, callback=False)

    @validate_response([b"You are now master"])
    async def take_control(self, password):
        """Take control of QTM.

        :param password: Password as entered in QTM.
        """
        cmd = "takecontrol %s" % password
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    @validate_response([b"You are now a regular client"])
    async def release_control(self):
        """Release control of QTM.
        """

        cmd = "releasecontrol"
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    @validate_response([b"Creating new connection", b"Already connected"])
    async def new(self):
        """Create a new measurement.
        """
        cmd = "new"
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    @validate_response(
        [
            b"Closing connection",
            b"File closed",
            b"Closing file",
            b"No connection to close",
        ]
    )
    async def close(self):
        """Close a measurement
        """
        cmd = "close"
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    @validate_response([b"Starting measurement", b"Starting RT from file"])
    async def start(self, rtfromfile=False):
        """Start RT from file. You need to be in control of QTM to be able to do this.
        """
        cmd = "start" + (" rtfromfile" if rtfromfile else "")
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    @validate_response([b"Stopping measurement"])
    async def stop(self):
        """Stop RT from file."""
        cmd = "stop"
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    @validate_response([b"Measurement loaded"])
    async def load(self, filename):
        """Load a measurement.

        :param filename: Path to measurement you want to load.
        """
        cmd = "load %s" % filename
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    @validate_response([b"Measurement saved"])
    async def save(self, filename, overwrite=False):
        """Save a measurement.

        :param filename: Filename you wish to save as.
        :param overwrite: If QTM should overwrite existing measurement.
        """
        cmd = "save %s%s" % (filename, " overwrite" if overwrite else "")
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    @validate_response([b"Project loaded"])
    async def load_project(self, project_path):
        """Load a project.

        :param project_path: Path to project you want to load.
        """
        cmd = "loadproject %s" % project_path
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    @validate_response([b"Trig ok"])
    async def trig(self):
        """Trigger QTM, only possible when QTM is configured to use Software/Wireless trigger"""
        cmd = "trig"
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    @validate_response([b"Event set"])
    async def set_qtm_event(self, event=None):
        """Set event in QTM."""
        cmd = "event%s" % ("" if event is None else " " + event)
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout
        )

    async def send_xml(self, xml):
        """Used to update QTM settings, see QTM RT protocol for more information.

        :param xml: XML document as a str. See QTM RT Documentation for details.
        """
        return await asyncio.wait_for(
            self._protocol.send_command(xml, command_type=QRTPacketType.PacketXML),
            timeout=self._timeout,
        )

    async def calibrate(self, timeout=600):  # Timeout 10 min.
        """Start calibration and return calibration result.

        :param timeout_: Calibration timeout.

        :rtype: An XML string containing the calibration result.
            See QTM RT Documentation for details.
        """
        cmd = "calibrate"
        response = await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

        if response != b"Starting calibration":
            raise QRTCommandException(response) 
        
        return await asyncio.wait_for(
            self._protocol.receive_response(), timeout=timeout)



# TODO GetCaptureC3D
# TODO GetCaptureQTM


async def connect(
    host,
    port=22223,
    version="1.23",
    on_event=None,
    on_disconnect=None,
    timeout=5,
    loop=None,
) -> QRTConnection:
    """Async function to connect to QTM

    :param host: Address of the computer running QTM.
    :param port: Port number to connect to, should be the port configured for little endian.
    :param version: Version of the rt protocol to use. Default is the latest version.
        The Qualisys Python sdk does not support versions older than 1.8.
    :param on_disconnect: Function to be called when a disconnect from QTM occurs.
    :param on_event: Function to be called when there's an event from QTM.
    :param timeout: The default timeout time for calls to QTM.
    :param loop: Alternative event loop, will use asyncio default if None.

    :rtype: A :class:`.QRTConnection`
    """
    loop = loop or asyncio.get_event_loop()

    try:
        _, protocol = await loop.create_connection(
            lambda: QTMProtocol(
                loop=loop, on_event=on_event, on_disconnect=on_disconnect
            ),
            host,
            port,
        )
    except (ConnectionRefusedError, TimeoutError, OSError) as exception:
        LOG.error(exception)
        return None

    try:
        await protocol.set_version(version)
    except QRTCommandException as exception:
        LOG.error(exception)
        return None
    except TypeError as exception:  # TODO: fix test requiring this (test_connect_set_version)
        LOG.error(exception)
        return None

    return QRTConnection(protocol, timeout=timeout)


def _validate_components(components):
    for component in components:
        if not component.lower() in [
            "2d",
            "2dlin",
            "3d",
            "3dres",
            "3dnolabels",
            "3dnolabelsres",
            "analog",
            "analogsingle",
            "force",
            "forcesingle",
            "6d",
            "6dres",
            "6deuler",
            "6deulerres",
            "gazevector",
            "eyetracker",
            "image",
            "timecode",
            "skeleton",
            "skeleton:global",
        ]:
            raise QRTCommandException("%s is not a valid component" % component)

