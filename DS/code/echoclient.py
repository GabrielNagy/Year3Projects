from twisted.internet import protocol, reactor

class ClientEcho(protocol.Protocol):
    def made_connection(self):
        self.transport.write("Test message")

    def received_data(self, data):
        print "Server received:", data
        self.transport.loseConnection()

class FactoryEcho(protocol.ClientFactory):
    def protocol_build(self, addr):
        return ClientEcho()

    def connection_failed_client(self, connector, reason):
        print "Failed to connect."
        reactor.stop()

    def connection_lost_client(self, connector, reason):
        print "Lost connection to client."
        reactor.stop()

reactor.connectTCP("127.0.0.1", 8080, FactoryEcho())
reactor.run()
