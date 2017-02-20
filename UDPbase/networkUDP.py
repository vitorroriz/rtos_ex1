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

    def __makeserversocket(self, addr = None ):
        #Creating socket (UDP)
        if addr == None:
            addr_to_bind = self.serveraddr
        else:
            addr_to_bind = addr

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) #Let port be reused when socket is closed
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #enable broadcast

        #Bind socket to a port
        print 'Starting up on %s port %d' % self.serveraddr
        sock.bind(addr_to_bind)
        return sock

    def listen(self):
        sock = self.__makeserversocket()

        while not self.shutdown:
            try:
                data, addr = sock.recvfrom(self.MAX_PKT_SIZE)

                print 'received %s bytes from %s' % (len(data), addr)
                print data

            except KeyboardInterrupt:
                self.shutdown = True
        sock.close()
        print '\nServer closed by Keyboard interruption'

    
    def sendto(self, addr , message = 'This is the client default message :D!'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) #Let port be reused when socket is closed
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #enable broadcast
                  
        try:
            sent = sock.sendto(message, addr)
        finally:
            sock.close()

    def broadcast(self, message):
        self.sendto(('192.168.1.255',self.serverport), message)
                    

    def getmyip(self):
            dummysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dummysocket.connect(('8.8.8.8',80)) #connecting to google to find my IP
            return dummysocket.getsockname()[0]


def serverhand():
    net1 = networkUDP(20001) 
    print 'My IP is: ' + net1.getmyip()
    net1.listen()
def clienthand():
    net2 = networkUDP(20000, serverhost = '192.168.1.37')
    while True:
        try:
            message = raw_input('-> ')
            #net1.sendto(('192.168.1.38'),30000)
            net2.sendto(('192.168.1.37',20000), message)
        except KeyboardInterrupt:
            print 'Keyboard int'            
            sys.exit()


def main():
    print 'Oi'
    #print net1.getmyip()
    #net1 = networkUDP(20000, serverhost = '192.168.1.37')

    ts = threading.Thread(target = serverhand)
    tc = threading.Thread(target = clienthand)

    ts.start()
    tc.start()

#   ts.join()
    while tc.isAlive():
        tc.join(5.0)



    
if __name__ == '__main__':
    main()
