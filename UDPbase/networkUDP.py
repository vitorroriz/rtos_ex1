import socket
import sys
import time
import struct
import binascii
from collections import namedtuple
import threading

#Defines the type of struct: TO BE CHANGED ACCORDING TO OUR APPLICATION
struct_format = '4s I I I I'

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
        self.MAX_PKT_SIZE = 20

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

        try:
            data, addr = sock.recvfrom(self.MAX_PKT_SIZE)

            print 'received %s bytes from %s' % (len(data), addr)
            return data

        except KeyboardInterrupt:
            self.shutdown = True

        sock.close()

    
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

    def sendstructto(self, addr, my_struct):
        packer = struct.Struct(struct_format)
        packed_data = packer.pack(*my_struct)
        self.sendto(addr, packed_data)

    def getstruct(self,packed_struct):
        unpacker = struct.Struct(struct_format)
        return unpacker.unpack(packed_data)

def packethandler(packed_data):
    net = networkUDP(1)
    data = net.getstruct(packed_data)
    print data
    print data[0]
    print str(data[1])
    print str(data[2])
    print str(data[3])
    print str(data[4])

def serverhand():
    net1 = networkUDP(20023) 
    print 'My IP is: ' + net1.getmyip()

    while True:
        packed_data = net1.listen()
        t = threading.Thread(target = packethandler, args = packed_data)
        t.start()
        t.join()


def clienthand():
    net2 = networkUDP(20023, serverhost = '192.168.1.37')
    ms = ('vrrz',3,4,9,8)
    c_addr = ('129.241.187.43',20000)
    while True:
        try:
            net2.sendstructto(c_addr, ms)
        except KeyboardInterrupt:
            print 'Keyboard int'            
            sys.exit()
        time.sleep(3)

def main():
    ts = threading.Thread(target = serverhand)
    tc = threading.Thread(target = clienthand)

    ts.start()
    tc.start()

#   ts.join()
    while tc.isAlive():
        tc.join(5.0)



    
if __name__ == '__main__':
    main()
