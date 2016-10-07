from twisted.internet import reactor, defer
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.error import ConnectionRefusedError

from qtm.protocol import QRTFactory, QRTCommandException
from qtm.packet import QRTPacketType


def _response_validator(response, expected_responses):
    for r in expected_responses:
        if response.startswith(r):
            return response

    raise QRTCommandException('Expected %s but got %s' % (expected_responses, response))


def _register_callbacks(d, on_ok, on_error):
    if on_ok and on_error:
        d.addCallbacks(on_ok, on_error)
    elif on_error:
        d.addErrback(on_error)
    elif on_ok:
        d.addCallback(on_ok)


class QRT(object):
    """Object responsible for creating the connection to QTM

        :param host: Address of the computer running QTM.
        :param port: Port number to connect to, should be the port configured for little endian.
        :param version: What version of the protocol to use, tested for 1.14 and above but could
            work with lower versions as well.
        :param logger: Callback for logging messages sent to and from QTM.
    """

    def __init__(self, host, port=22223, version='1.14', logger=None):
        super(QRT, self).__init__()
        self.host = host
        self.port = port
        self.version = version
        self.logger = logger

    @defer.inlineCallbacks
    def connect(self, on_connect, on_disconnect=None, on_event=None):
        """Connect to QTM

        :param on_connect: Called on successful connection to QTM. Callback receives an :class:`QRTConnection` object.
        :param on_disconnect: Called if connection fails or when connection is lost.
        :param on_event: Called when there's an event from QTM.

        """
        point = TCP4ClientEndpoint(reactor, self.host, self.port)
        factory = QRTFactory(self.version, on_disconnect, on_event, self.logger)
        try:
            p = yield point.connect(factory)
        except ConnectionRefusedError as reason:
            if on_disconnect:
                on_disconnect(QRTCommandException(str(reason)))
            return
        except Exception as reason:
            if on_disconnect:
                on_disconnect(reason)
            return

        try:
            version = yield p.connected_d
        except Exception as reason:
            if on_disconnect:
                p.on_disconnect = None
                p.transport.loseConnection()
                on_disconnect(reason)
            return

        on_connect(QRTConnection(p), version)


class QRTConnection(object):
    """Represent a connection to QTM.

        Should not be instantiated, obtained from the :func:`~qtm.QRT.connect` on_connect callback.
    """

    def __init__(self, protocol):
        super(QRTConnection, self).__init__()
        self.protocol = protocol

    def disconnect(self):
        """Disconnect from QTM."""
        self.protocol.transport.loseConnection()

    def qtm_version(self, on_ok=None, on_error=None):
        """Get QTM version."""
        d = self.protocol.send_command("qtmversion")
        _register_callbacks(d, on_ok, on_error)
        return d

    def byte_order(self, on_ok=None, on_error=None):
        """Get the byte order used when communicating(should only ever be little endian)."""
        d = self.protocol.send_command("byteorder")
        _register_callbacks(d, on_ok, on_error)
        return d

    def get_state(self):
        """Get the latest state of QTM, will be returned to the callback specified by the
            :func:`~qtm.QRT.connect` on_event callback.
        """
        return self.protocol.send_command("getstate", callback=False)

    def get_parameters(self, parameters=None, on_ok=None, on_error=None):
        """Get the settings for the requested component(s) of QRM in XML format.

        :param parameters: Parameters to request. Could be 'all' or any combination
            of 'general', '3d', '6d', 'analog', 'force', 'gazevector', 'image'.
        """

        if parameters is None:
            parameters = ['all']

        cmd = "getparameters %s" % " ".join(parameters)
        d = self.protocol.send_command(cmd)
        _register_callbacks(d, on_ok, on_error)
        return d

    def get_current_frame(self, components=None, on_packet=None):
        """Get measured values from QTM for a single frame.

        :param components: See QTM RT protocol distributed with QTM for possible values.
        :param on_packet: Callback called **once** on successful request.
            Callback will receive a :class:`QRTPacket`
        """

        if components is None:
            components = ['all']

        cmd = "getcurrentframe %s" % " ".join(components)
        self.protocol.set_on_packet(on_packet)
        return self.protocol.send_command(cmd)

    def stream_frames(self, frames='allframes', components=None, on_packet=None):
        """Stream measured frames from QTM until :func:`~qtm.QRTConnection.stream_frames_stop` is called.


        :param frames: Which frames to receive, possible values are 'allframes',
            'frequency:n' or 'frequencydivisor:n' where n should be desired value.
        :param components: See QTM RT protocol distributed with QTM for possible values.
        :param on_packet: Callback called **repeatedly** on successful request.
            Callback will receive a :class:`QRTPacket`
        """

        if components is None:
            components = ['all']

        cmd = "streamframes %s %s" % (frames, " ".join(components))
        self.protocol.set_on_packet(on_packet)
        return self.protocol.send_command(cmd)

    def stream_frames_stop(self):
        """Stop streaming frames."""
        cmd = "streamframes stop"
        self.protocol.set_on_packet(None)
        return self.protocol.send_command(cmd, callback=False)

    def take_control(self, password, on_ok=None, on_error=None):
        """Take control over QTM.

        :param password: Password as entered in QTM.
        """
        cmd = "takecontrol %s" % password
        d = self.protocol.send_command(cmd)
        d.addCallback(_response_validator,
                      expected_responses=[b'You are now master'])
        _register_callbacks(d, on_ok, on_error)
        return d

    def release_control(self, on_ok=None, on_error=None):
        """Release control over QTM."""

        cmd = "releasecontrol"
        d = self.protocol.send_command(cmd)
        _register_callbacks(d, on_ok, on_error)
        return d

    def new(self, on_ok=None, on_error=None):
        """Create a new measurement."""
        cmd = "new"
        d = self.protocol.send_command(cmd)
        d.addCallback(_response_validator,
                      expected_responses=[b'Creating new connection',
                                          b'Already connected'])
        _register_callbacks(d, on_ok, on_error)
        return d

    def close(self, on_ok=None, on_error=None):
        """Close a measurement"""
        cmd = "close"
        d = self.protocol.send_command(cmd)
        d.addCallback(_response_validator,
                      expected_responses=[b'Closing connection',
                                          b'File closed',
                                          b'Closing file',
                                          b'No connection to close'])
        _register_callbacks(d, on_ok, on_error)
        return d

    def start(self, rtfromfile=False, on_ok=None, on_error=None):
        """Start RT from file. You need to be in control of QTM to be able to do this."""
        cmd = "start" + (' rtfromfile' if rtfromfile else "")
        d = self.protocol.send_command(cmd)
        d.addCallback(_response_validator,
                      expected_responses=[b'Starting measurement',
                                          b'Starting RT from file'])
        _register_callbacks(d, on_ok, on_error)
        return d

    def stop(self, on_ok=None, on_error=None):
        """Stop RT from file."""
        cmd = "stop"
        d = self.protocol.send_command(cmd)
        d.addCallback(_response_validator,
                      expected_responses=[b'Stopping measurement'])
        _register_callbacks(d, on_ok, on_error)
        return d

    def load(self, filename, on_ok=None, on_error=None):
        """Load a measurement.

        :param filename: Path to measurement you want to load.
        """
        cmd = "load %s" % filename
        d = self.protocol.send_command(cmd)
        d.addCallback(_response_validator,
                      expected_responses=[b'Measurement loaded'])
        _register_callbacks(d, on_ok, on_error)
        return d

    def save(self, filename, overwrite=False, on_ok=None, on_error=None):
        """Save a measurement.

        :param filename: Filename you wish to save as.
        :param overwrite: If QTM should overwrite existing measurement.
        """
        cmd = "save %s%s" % (filename, " overwrite" if overwrite else "")
        d = self.protocol.send_command(cmd)
        d.addCallback(_response_validator,
                      expected_responses=[b'Measurement saved'])
        _register_callbacks(d, on_ok, on_error)
        return d

    def load_project(self, project_path, on_ok=None, on_error=None):
        """Load a project.

        @param project_path: Path to project you want to load.
        """
        cmd = "loadproject %s" % project_path
        d = self.protocol.send_command(cmd)
        d.addCallback(_response_validator,
                      expected_responses=[b'Project loaded'])
        _register_callbacks(d, on_ok, on_error)
        return d

    def trig(self, on_ok=None, on_error=None):
        """Trigger QTM, only possible when QTM is configured to use Software/Wireless trigger"""
        cmd = "trig"
        d = self.protocol.send_command(cmd)
        d.addCallback(_response_validator,
                      expected_responses=[b'Trig ok'])
        _register_callbacks(d, on_ok, on_error)
        return d

    def set_qtm_event(self, event=None, on_ok=None, on_error=None):
        """Set event in QTM."""
        cmd = "event%s" % "" if event is None else " " + event
        d = self.protocol.send_command(cmd)
        d.addCallback(_response_validator,
                      expected_responses=[b'Event set'])
        _register_callbacks(d, on_ok, on_error)
        return d

    def send_xml(self, xml, on_ok=None, on_error=None):
        """Used to update QTM settings, see QTM RT protocol for more information.

        :param xml: XML document as a str.
        """
        d = self.protocol.send_command(xml, command_type=QRTPacketType.PacketXML)
        _register_callbacks(d, on_ok, on_error)
        return d


        # TODO GetCaptureC3D
        # TODO GetCaptureQTM
