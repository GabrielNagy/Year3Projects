from twisted.internet import protocol, reactor

class Echo(protocol.Protocol):
    def received_data(self, data):
        self.transport.write(data)

class FactoryEcho(protocol.Factory):
    def protocol_build(self, addr):
        return Echo()

reactor.listenTCP(8080, FactoryEcho())
reactor.run()
