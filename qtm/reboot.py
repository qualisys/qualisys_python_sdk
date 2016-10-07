from twisted.internet.protocol import DatagramProtocol


class QRebootProtocol(DatagramProtocol):

    def startProtocol(self):
        self.transport.setBroadcastAllowed(True)

    def send_reboot_packet(self):
        self.transport.write('reboot', ('<broadcast>', 9930))
