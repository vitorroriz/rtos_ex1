import socket
import sys
import time
import struct
import threading
import pickle


#The messages sent and received are dictionary types with two layers:
#External layer:
#data_out = {"m_type" : my_m_type, "data" : data_in}
#Internal layer:
#data_in = {to be defined by app}


class networkUDP:
    'Class that defines a simple UDP server'

    # -------- Handlers to received packets ----------------------------
    def __handler_request(data_in):
        print "This is a request handler:"
        print "There was a request in floor: " + data_in["floor"]
        print "This was a request of type:   " + data_in["request_n"]
        print "The request had the msg       :"+ data_in["msg"]

    def __handler_chat(data_in):
        print "This is a chat handler"
        print data_in["msg"]
    #-----------end of handlers definition-------------------------------

    # -------- Constructor for the class obj ----------------------------
    def __init__(self, serverport, serverhost = None):
        self.serverport = int(serverport)
        if serverhost:
            self.serverhost = serverhost
        else:
            self.serverhost = self.getmyip()
            
        self.serveraddr = (self.serverhost, self.serverport)
        self.shutdown   =  False
        self.MAX_PKT_SIZE = 512

        #Dictionary to handlers functions (TO BE CHANGED BY OUR APP)
        self.handler_dic = {"request" : handler_request, "chat" : handler_chat}
    # -------- end of constructor ---------- ----------------------------


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

    def _unpack(self, data_out_packed):
        #Deserializing new data into out and in data packs
        data_out = pickle.loads(data_out_packed)
        data_in_packed = data_out["data"]
        data_in = pickle.loads(data_in_packed)
        return data_out, data_in        

    def listen(self):
        sock = self.__makeserversocket()

        try:
            #Waiting for new data
            data, addr = sock.recvfrom(self.MAX_PKT_SIZE)
            data_out, data_in = self._unpack(data)
            print 'received %s bytes from %s' % (len(data), addr)
            m_type = data_out["m_type"]
            print 'Message of type: ' + m_type


            #Creating threads to handle new income data according to its type
            t = threading.Thread(target = self.handler_dic[m_type], args = (data_in,))
            t.start()

        except KeyboardInterrupt:
            self.shutdown = True

        sock.close()

    def _pack(self, message_type, data_in):
        data_in_packed = pickle.dumps(data_in)
        data_out = {"m_type" : m_type, "data" : data_in_packed }
        data_out_packed = pickle.dumps(data_out)
        return data_out_packed
     
    def sendto(self, addr , message_type, data_in):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) #Let port be reused when socket is closed
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #enable broadcast
        
        data_out_packed = self._pack(message_type, data_in)

        try:
            sent = sock.sendto(data_out_packed, addr)
        finally:
            sock.close()

    def broadcast(self, message):
        self.sendto(('192.168.1.255',self.serverport), message)               

    def getmyip(self):
            dummysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dummysocket.connect(('8.8.8.8',80)) #connecting to google to find my IP
            return dummysocket.getsockname()[0]


def packethandler(packed_data):

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
