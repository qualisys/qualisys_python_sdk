from __future__ import print_function

import qtm

class QScript:

    def __init__(self):
        self.qrt = qtm.QRT("127.0.0.1", 22223)
        self.qrt.connect(on_connect=self.on_connect, on_disconnect=self.on_disconnect, on_event=self.on_event)

    def on_connect(self, connection, version):
        print('Connected to QTM with {}'.format(version))
        # Connection is the object containing all methods/commands you can send to qtm
        self.connection = connection
        # Try to start rt from file

        self.connection.start(rtfromfile=True, on_ok=lambda result: self.start_stream(), on_error=self.on_error)

    def on_disconnect(self, reason):
        print(reason)
        # Stops main loop and exits script
        qtm.stop()

    def on_event(self, event):
        # Print event type
        print(event)

    def on_error(self, error):
        error_message = error.getErrorMessage()
        if error_message == "'RT from file already running'":
            # If rt already is running we can start the stream anyway
            self.start_stream()
        else:
            # On other errors we fail
            print(error_message)
            self.connection.disconnect()

    def on_packet(self, packet):
        # All packets has a Framenumber and a timestamp
        print('Framenumber: %d\t Timestamp: %d' % (packet.framenumber, packet.timestamp))

        # all components have some sort of header
        # both header and components are named tuples
        header, markers = packet.get_2d_markers()

        # named tuples can be accessed like this:
        print('Header: %d\t%d\t%d' % (header.camera_count, header.drop_rate, header.out_of_sync_rate))

        # print all markers for all cameras
        for index, camera in enumerate(markers, 1):
            print('\t', 'Camera %d' % index)

            for marker in camera:
                # or named tuples can be unpacked as normal tuples
                x, y, w, h = marker
                print('\t\t', x, y, w, h)

    def start_stream(self):
        # Start streaming 2d data and register packet callback
        self.connection.stream_frames(on_packet=self.on_packet, components=['2d'])

        # Schedule a call for later to shutdown connection
        qtm.call_later(5, self.connection.disconnect)

def main():
    # Instantiate our script class
    # We don't need to create a class, you could also store the connection object in a global variable
    QScript()

    # Start the processing loop
    qtm.start()


if __name__ == '__main__':
    main()
