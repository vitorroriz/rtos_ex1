import socket
import sys
import time
from collections import namedtuple
import threading





class networkUDP:
    'Class that defines a simple UDP server'
    def __init__(self, serverport, serverhost = None):
        self.serverport = int(serverport)
        if serverhost:
            self.serverhost = serverhost
        else:
            self.serverhost = self.getmyip()
            
        self.serveraddr = (self.serverhost, self.serverport)
        self.shutdown   =  False
        self.MAX_PKT_SIZE = 512

    def makeserversocket(self):
        #Creating socket (UDP)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP socket
        #Bind socket to a port
        print 'Starting up on %s port %d' % self.serveraddr
        sock.bind(self.serveraddr)
        return sock

    def listen(self):
        sock = self.makeserversocket()

        while not self.shutdown:
            try:
                #print '\nWaiting to receive message'
                data, addr = sock.recvfrom(self.MAX_PKT_SIZE)

                print 'received %s bytes from %s' % (len(data), addr)
                print data

#                if data:
#                   sent = sock.sendto(data,addr)
#           print 'sent %s bytes back to %s' % (sent,addr)
            except KeyboardInterrupt:
                self.shutdown = True
        sock.close()
        print '\nServer closed by Keyboard interruption'

    
    def sendto(self, addr, message = 'This is the client default message :D!'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) #Let port be reused when socket is closed
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #enable broadcast
                  

        try:
    #       print 'Sending "%s"' % message
            sent = sock.sendto(message, addr)
    #       print 'Waiting to receive'
    #        data, server = sock.recvfrom(512)
    #           print 'received "%s" from %s' % (data,server)

        finally:
#           print 'closing client socket'
            sock.close()

    def broadcast(self, message):
        self.sendto(('255.255.255.255',self.serverport), message)
                    

    def getmyip(self):
            dummysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dummysocket.connect(('google.com',0))
            return dummysocket.getsockname()[0]


net1 = networkUDP(20000)


def serverhand():
    net1.listen()
    
def clienthand():
    while True:
        try:
            message = raw_input('-> ')
            net1.sendto(('192.168.1.103'),30000)
        except KeyboardInterrupt:
            print 'Keyboard int'            
            sys.exit()




def main():
    net1 = networkUDP(30000)
    print 'Oi'
    print net1.getmyip()
    net1.broadcast('Message bcast')

    
if __name__ == '__main__':
    main()
