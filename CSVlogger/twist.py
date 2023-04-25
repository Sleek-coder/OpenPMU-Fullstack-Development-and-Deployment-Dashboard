#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

address = "127.0.0.1"
# Here's a UDP version of the simplest possible protocol
class EchoUDP(DatagramProtocol):
    def datagramReceived(self, datagram, address):
        self.transport.write(datagram, address)
        print('Datagram received at server: ', repr(datagram))


def main():
    reactor.listenUDP(48011, EchoUDP())
    reactor.run()

if __name__ == '__main__':
    main()
