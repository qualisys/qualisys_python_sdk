import asyncio

from qtm.packet import QRTPacketType
from qtm.protocol import QTMProtocol, QRTCommandException


def validate_response(expected_responses):
    def internal_decorator(function):
        async def wrapper(*args, **kwargs):

            response = await function(*args, **kwargs)

            for r in expected_responses:
                if response.startswith(r):
                    return response

            raise QRTCommandException('Expected %s but got %s' %
                                      (expected_responses, response))

        return wrapper

    return internal_decorator


async def connect(host,
                  port=22223,
                  version='1.18',
                  on_event=None,
                  on_disconnect=None,
                  timeout=5):
    """Connect to QTM

    :param host: Address of the computer running QTM.
    :param port: Port number to connect to, should be the port configured for little endian.
    :param version: What version of the protocol to use, tested for 1.14 and above but could
        work with lower versions as well.
    :param on_event: Called when there's an event from QTM.

    """
    loop = asyncio.get_event_loop()

    try:
        _, protocol = await loop.create_connection(
            lambda: QTMProtocol(loop, on_event=on_event, on_disconnect=on_disconnect), host, port)
    except ConnectionRefusedError as e:
        print(e)
        return None

    try:
        await protocol.set_version(version)
    except Exception as e:
        return None

    return QRTConnection(protocol, timeout=timeout)


class QRTConnection(object):
    """Represent a connection to QTM.

        Should not be instantiated, obtained from the :func:`~qtm.QRT.connect` on_connect callback.
    """

    def __init__(self, protocol, timeout):
        super(QRTConnection, self).__init__()
        self._protocol = protocol
        self._timeout = timeout

    def disconnect(self):
        """Disconnect from QTM."""
        self._protocol.transport.close()

    async def qtm_version(self):
        """Get QTM version."""
        return await asyncio.wait_for(
            self._protocol.send_command("qtmversion"), timeout=self._timeout)

    async def byte_order(self):
        """Get the byte order used when communicating(should only ever be little endian)."""
        return await asyncio.wait_for(
            self._protocol.send_command("byteorder"), timeout=self._timeout)

    async def get_state(self):
        """Get the latest state of QTM, will be returned to the callback specified by the
            :func:`~qtm.QRT.connect` on_event callback.
        """
        self._protocol.send_command("getstate", callback=False)
        return await self._protocol.await_event()

    async def await_event(self, event=None, timeout=30):
        return await self._protocol.await_event(event, timeout=timeout)

    async def get_parameters(self, parameters=None):
        """Get the settings for the requested component(s) of QRM in XML format.

        :param parameters: Parameters to request. Could be 'all' or any combination
            of 'general', '3d', '6d', 'analog', 'force', 'gazevector', 'image'.
        """

        if parameters is None:
            parameters = ['all']

        cmd = "getparameters %s" % " ".join(parameters)
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    async def get_current_frame(self, components=None):
        """Get measured values from QTM for a single frame.

        :param components: See QTM RT protocol distributed with QTM for possible values.
            Callback will receive a :class:`QRTPacket`
        """

        if components is None:
            components = ['all']

        cmd = "getcurrentframe %s" % " ".join(components)
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    async def stream_frames(self,
                            frames='allframes',
                            components=None,
                            on_packet=None):
        """Stream measured frames from QTM until :func:`~qtm.QRTConnection.stream_frames_stop` is called.


        :param frames: Which frames to receive, possible values are 'allframes',
            'frequency:n' or 'frequencydivisor:n' where n should be desired value.
        :param components: See QTM RT protocol distributed with QTM for possible values.
            Callback will receive a :class:`QRTPacket`
        """

        if components is None:
            components = ['all']

        self._protocol.set_on_packet(on_packet)

        cmd = "streamframes %s %s" % (frames, " ".join(components))
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    async def stream_frames_stop(self):
        """Stop streaming frames."""

        self._protocol.set_on_packet(None)

        cmd = "streamframes stop"
        self._protocol.send_command(cmd, callback=False)

    @validate_response([b'You are now master'])
    async def take_control(self, password):
        """Take control over QTM.

        :param password: Password as entered in QTM.
        """
        cmd = "takecontrol %s" % password
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    @validate_response([b'You are now a regular client'])
    async def release_control(self):
        """Release control over QTM."""

        cmd = "releasecontrol"
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    @validate_response([b'Creating new connection', b'Already connected'])
    async def new(self):
        """Create a new measurement."""
        cmd = "new"
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    @validate_response([
        b'Closing connection', b'File closed', b'Closing file',
        b'No connection to close'
    ])
    async def close(self):
        """Close a measurement"""
        cmd = "close"
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    @validate_response([b'Starting measurement', b'Starting RT from file'])
    async def start(self, rtfromfile=False):
        """Start RT from file. You need to be in control of QTM to be able to do this."""
        cmd = "start" + (' rtfromfile' if rtfromfile else "")
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    @validate_response([b'Stopping measurement'])
    async def stop(self):
        """Stop RT from file."""
        cmd = "stop"
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    @validate_response([b'Measurement loaded'])
    async def load(self, filename):
        """Load a measurement.

        :param filename: Path to measurement you want to load.
        """
        cmd = "load %s" % filename
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    @validate_response([b'Measurement saved'])
    async def save(self, filename, overwrite=False):
        """Save a measurement.

        :param filename: Filename you wish to save as.
        :param overwrite: If QTM should overwrite existing measurement.
        """
        cmd = "save %s%s" % (filename, " overwrite" if overwrite else "")
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    @validate_response([b'Project loaded'])
    async def load_project(self, project_path):
        """Load a project.

        @param project_path: Path to project you want to load.
        """
        cmd = "loadproject %s" % project_path
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    @validate_response([b'Trig ok'])
    async def trig(self):
        """Trigger QTM, only possible when QTM is configured to use Software/Wireless trigger"""
        cmd = "trig"
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    @validate_response([b'Event set'])
    async def set_qtm_event(self, event=None):
        """Set event in QTM."""
        cmd = "event%s" % ("" if event is None else " " + event)
        return await asyncio.wait_for(
            self._protocol.send_command(cmd), timeout=self._timeout)

    async def send_xml(self, xml):
        """Used to update QTM settings, see QTM RT protocol for more information.

        :param xml: XML document as a str.
        """
        return await asyncio.wait_for(
            self._protocol.send_command(
                xml, command_type=QRTPacketType.PacketXML),
            timeout=self._timeout)

        # TODO GetCaptureC3D
        # TODO GetCaptureQTM
