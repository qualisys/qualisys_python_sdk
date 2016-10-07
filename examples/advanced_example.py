from __future__ import print_function
import xml.etree.cElementTree as ET

from twisted.internet import defer

import qtm
from qtm.protocol import QRTCommandException, QRTEvent
from qtm.packet import QRTComponentType


class QScript:

    def __init__(self):
        self.qrt = qtm.QRT("127.0.0.1", 22223)
        self.qrt.connect(on_connect=self.on_connect, on_disconnect=self.on_disconnect, on_event=self.on_event)
        self.init = False
        self.connection = None

    # Inline callbacks is a feature of the twisted framework that makes it possible to write
    # asynchronous code that looks synchronous
    # http://twistedmatrix.com/documents/current/api/twisted.internet.defer.inlineCallbacks.html
    @defer.inlineCallbacks
    def on_connect(self, connection, version):
        print('Connected to QTM with {}'.format(version))
        # Connection is the object containing all methods/commands you can send to qtm
        self.connection = connection

        try:
            # By yielding we return control to the twisted library and execution of this function will
            # continue when we have received a reply, or an error
            # Errors will result in a QRTCommandException
            result = yield self.connection.get_parameters(parameters=['3d'])
        except QRTCommandException as e:
            self.fail(e.value)
            return

        # Parse the returned xml
        xml = ET.fromstring(result)
        self.labels = [label.text for label in xml.iter('Name')]

        # Get state to try and figure out if we're already doing rt from file
        self.connection.get_state()

    def fail(self, msg):
        print('Error: %s' % msg)
        self.connection.disconnect()

    def on_disconnect(self, reason):
        print(reason)
        # Stops main loop and exits script
        qtm.stop()

    @defer.inlineCallbacks
    def on_event(self, event):
        # Print event type
        print(event)

        if not self.init:
            self.init = True
            rt = event == QRTEvent.EventRTfromFileStarted

            try:
                # control is needed
                yield self.connection.take_control('password')

                # start rt from file if it's not running
                # (might fail if it wasn't the last event...)
                if not rt:
                    yield self.connection.start(rtfromfile=True)

                # start streaming
                yield self.connection.stream_frames(components=['3d', 'analog'], on_packet=self.on_packet)

            except QRTCommandException as e:
                self.fail(e.value)
        return

    def on_packet(self, packet):
        # All packets has a Framenumber and a timestamp
        print('Framenumber: %d\t Timestamp: %d' % (packet.framenumber, packet.timestamp))

        # Since components have different frequencies, all requested types might not be present
        # in each package, so we check
        if QRTComponentType.Component3d in packet.components:
            header, markers = packet.get_3d_markers()

            # You can pair a label name and marker by index, however, if you change the order or
            # a label in qtm it will not be updated here unless you fetch marker info again
            for marker, label in zip(markers, self.labels):
                print('%s - X: %.4f Y: %.4f Z: %.4f' % (label, marker.x, marker.y, marker.z))


        # Just print analog
        if QRTComponentType.ComponentAnalog in packet.components:
            component, analog = packet.get_analog()

            first_samples = [str(sample.samples[0]) for device, sample_number, sample in analog]
            print('Analog:', '\t'.join(first_samples))



def main():
    # Instantiate our script class
    # We don't need to create a class, you could also store the connection object in a global variable
    QScript()

    # Start the processing loop
    qtm.start()


if __name__ == '__main__':
    main()
