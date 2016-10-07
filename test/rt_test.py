import xml.etree.ElementTree as ET
from functools import partial

from twisted.trial import unittest
from twisted.python.failure import Failure
from twisted.internet import reactor, defer
from twisted.internet.error import ConnectionRefusedError

from qtm.util import RestError
from qtm.protocol import QRTProtocol
from qtm.packet import QRTPacket, QRTComponentType, QRTEvent
from qtm import QRT, QRTConnection, QRTCommandException


class TestConnection(unittest.TestCase):

    def setUp(self):
        self.connection = None

    def tearDown(self):
        if self.connection:
            self.connection.disconnect()

    def test_connection(self):
        self.qrt = QRT("127.0.0.1", 22223)

        self.qrt.connect(on_connect=self.on_connect, on_disconnect=None, on_event=None)
        self.d = defer.Deferred()
        self.d.addCallback(self.assertIsInstance, QRTConnection)
        return self.d

    def test_connection_wrong_version(self):
        self.qrt = QRT("127.0.0.1", 22223, version='1000.0')

        self.qrt.connect(on_connect=self.on_connect, on_disconnect=self.on_disconnect, on_event=None)
        self.d = defer.Deferred()
        self.d.addCallback(self.assertIsInstance, QRTCommandException)
        return self.d

    def test_connection_unreachable(self):
        self.qrt = QRT("127.0.0.1", 65535)

        self.qrt.connect(on_connect=self.on_connect, on_disconnect=self.on_disconnect, on_event=None)
        self.d = defer.Deferred()
        self.d.addCallback(self.assertIsInstance, QRTCommandException)
        return self.d

    def on_disconnect(self, reason):
        self.d.callback(reason)

    def on_connect(self, connection, _):
        self.connection = connection
        self.d.callback(connection)


class TestPacket(unittest.TestCase):

    @defer.inlineCallbacks
    def setUp(self):
        self.connection = None
        self.qrt = QRT("127.0.0.1", 22223)
        self.defered_connection = defer.Deferred()
        self.qrt.connect(on_connect=self.on_connect, on_disconnect=None, on_event=None)
        yield self.defered_connection
        yield self.connection.take_control('password')
        yield self.connection.load("d:/measurements/3d_analog_6dof_big27file.qtm")
        yield self.connection.start(rtfromfile=True)

    def tearDown(self):
        if self.connection:
            self.connection.close()
            self.connection.disconnect()

    def on_connect(self, connection, _):
        self.connection = connection
        self.defered_connection.callback(None)

    def create_deferred(self):
        self.d = defer.Deferred()
        self.d.addCallback(self.validate_packet)
        return self.d

    def get_packet(self, packet_type, component, getter=None):
        self.connection.get_current_frame(components=[packet_type], on_packet=self.on_packet)
        self.component_type = component
        self.getter = getter

    def test_6d(self):
        self.get_packet("6d", QRTComponentType.Component6d, "get_6d")
        return self.create_deferred()

    def test_6dres(self):
        self.get_packet("6dres", QRTComponentType.Component6dRes, "get_6d_residual")
        return self.create_deferred()

    def test_6deuler(self):
        self.get_packet("6deuler", QRTComponentType.Component6dEuler, "get_6d_euler")
        return self.create_deferred()

    def test_6deulerres(self):
        self.get_packet("6deulerres", QRTComponentType.Component6dEulerRes, "get_6d_euler_residual")
        return self.create_deferred()

    def test_analog(self):
        self.get_packet("analog", QRTComponentType.ComponentAnalog, "get_analog")
        return self.create_deferred()

    def test_analog_single(self):
        self.get_packet("analogsingle", QRTComponentType.ComponentAnalogSingle, "get_analog_single")
        return self.create_deferred()

    def test_3d(self):
        self.get_packet("3d", QRTComponentType.Component3d, "get_3d_markers")
        return self.create_deferred()

    def test_3dres(self):
        self.get_packet("3dres", QRTComponentType.Component3dRes, "get_3d_markers_residual")
        return self.create_deferred()

    def test_3dnolabels(self):
        self.get_packet("3dnolabels", QRTComponentType.Component3dNoLabels, "get_3d_markers_no_label")
        return self.create_deferred()

    def test_3dnolabelsres(self):
        self.get_packet("3dnolabelsres", QRTComponentType.Component3dNoLabelsRes,
                        "get_3d_markers_no_label_residual")
        return self.create_deferred()

    def test_2d(self):
        self.get_packet("2d", QRTComponentType.Component2d, "get_2d_markers")
        return self.create_deferred()

    def test_2dlin(self):
        self.get_packet("2dlin", QRTComponentType.Component2dLin, "get_2d_markers_linearized")
        return self.create_deferred()

    # def test_image(self):
    #     self.get_packet("image", QRTComponentType.ComponentImage, "get_image")
    #     return self.create_deferred()

    def test_force(self):
        self.get_packet("force", QRTComponentType.ComponentForce, "get_force")
        return self.create_deferred()

    def test_force_single(self):
        self.get_packet("forcesingle", QRTComponentType.ComponentForceSingle, "get_force_single")
        return self.create_deferred()
    
    def on_packet(self, packet):
        self.d.callback(packet)

    def validate_packet(self, packet):
        print(packet.components.keys())
        self.assertIsInstance(packet, QRTPacket)
        self.assertIn(self.component_type, packet.components)
        if self.getter:
            fn = getattr(packet, self.getter)
            data = fn()
            print(data)
            self.assertIsInstance(data, tuple)


class TestStream(unittest.TestCase):

    @defer.inlineCallbacks
    def setUp(self):
        self.connection = None
        self.qrt = QRT("127.0.0.1", 22223)
        self.defered_connection = defer.Deferred()
        self.qrt.connect(on_connect=self.on_connect, on_disconnect=None, on_event=None)
        yield self.defered_connection
        yield self.defered_connection
        yield self.connection.take_control('password')
        yield self.connection.load("d:/measurements/3d_analog_6dof_big27file.qtm")
        yield self.connection.start(rtfromfile=True)

    def tearDown(self):
        if self.connection:
            self.connection.close()
            self.connection.disconnect()

    def on_connect(self, connection, _):
        self.connection = connection
        self.defered_connection.callback(None)

    def create_deferred(self):
        self.d = defer.Deferred()
        self.d.addCallback(self.validate_packet)
        return self.d

    def on_packet(self, packet):
        self.connection.stream_frames("stop")
        # reactor.callLater(5, self.d.callback, packet)
        self.d.callback(packet)

    def test_stream_parse_error(self):
        d = self.connection.stream_frames(frames='error').addErrback(self.validate_error)
        self.d = defer.Deferred()
        return self.d

    def test_stream_all(self):
        self.connection.stream_frames(on_packet=self.on_packet)
        return self.create_deferred()

    def validate_packet(self, packet):
        print(packet.components.keys())
        self.assertIsInstance(packet, QRTPacket)

    def validate_error(self, error):
        self.assertIsInstance(error.value, QRTCommandException)
        self.d.callback(True)


class TestCommands(unittest.TestCase):

    @defer.inlineCallbacks
    def setUp(self):
        self.connection = None
        self.qrt = QRT("127.0.0.1", 22223)
        self.defered_connection = defer.Deferred()
        self.qrt.connect(on_connect=self.on_connect, on_disconnect=None, on_event=self.on_event)
        self.d = None
        yield self.defered_connection

    def tearDown(self):
        if self.connection:
            self.connection.disconnect()

    def on_connect(self, connection, _):
        self.connection = connection
        self.defered_connection.callback(None)

    def on_event(self, event):
        self.assertIsInstance(event, QRTEvent)
        if self.d:
            self.d.callback(event)

    def test_take_control(self):
        d = self.connection.take_control("password")
        d.addCallback(self.assertEquals, b'You are now master')
        return d

    def test_fail_control(self):
        d = self.connection.take_control("wrong_password")
        d.addErrback(self.validate_error, b'Wrong or missing password')
        return d

    def test_qtm_version(self):
        d = self.connection.qtm_version()
        d.addCallback(self.starts_with, b'QTM Version is')
        return d

    def test_byte_order(self):
        d = self.connection.byte_order()
        d.addCallback(self.starts_with, b'Byte order is')
        return d

    def test_get_state(self):
        self.d = defer.Deferred()
        self.connection.get_state()
        return self.d

    def test_get_parameters(self):
        d = self.connection.get_parameters()
        d.addCallback(self.validate_parameters)
        return d

    def test_multiple_commands(self):
        d = []
        d.append(self.connection.take_control("password"))
        d.append(self.connection.load("d:\measurements\FirstMiqusMeasurement.qtm"))
        d.append(self.connection.start(rtfromfile=True))
        d.append(self.connection.stop())
        d.append(self.connection.close())
        d.append(self.connection.release_control())
        deferreds = defer.gatherResults(d)
        deferreds.addCallback(self.validate_deferred_list)
        return deferreds

    def on_packet(self, packet):
        pass

    def starts_with(self, result, expected):
        self.assertTrue(result.startswith(expected))

    def validate_parameters(self, parameters):
        xml = ET.fromstring(parameters)
        self.assertIsInstance(xml, ET.Element)

    def validate_deferred_list(self, deferreds):
        print(deferreds)

    def validate_error(self, error, expected):
        # TODO value.value isn't very intuitive
        self.assertEqual(error.value.value, expected)

    def validate_error_swizzle(self, expected, error):
        self.validate_error(error, expected)

    def test_callbacks_on_ok(self):
        return self.connection.take_control('password',
                                            on_ok=partial(self.starts_with,
                                                          b'You are now master'))

    def test_callbacks_on_error(self):
        return self.connection.take_control('wrong_password',
                                            on_error=partial(self.validate_error_swizzle,
                                                             b'Wrong or missing password'))

    def test_callbacks_both_error(self):
        return self.connection.take_control('wrong_password',
                                            on_ok=self._fail,
                                            on_error=partial(self.validate_error_swizzle,
                                                             b'Wrong or missing password'))
    def test_callbacks_both_ok(self):
        return self.connection.take_control('password',
                                            on_ok=partial(self.starts_with,
                                                          b'You are now master'),
                                            on_error=self._fail)

    def _fail(self, _):
        self.assertTrue(False)

    def on_ok(self, result):
        print(result)




if __name__ == '__main__':
    unittest.main()
