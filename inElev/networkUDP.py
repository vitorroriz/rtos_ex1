import socket
import sys
import time
import struct
import threading
import pickle


class networkUDP:
    'Class that defines a simple UDP server'

    # -------- Handlers to received packets ----------------------------
    # def _handler_request(self,data_in):
    #     print "This is a request handler:"
    #     print "There was a request in floor: " + data_in["floor"]
    #     print "This was a request of type:   " + data_in["request_n"]
    #     print "The request had the msg       :"+ data_in["msg"]


    # def _handler_chat(self,data_in):
    #     print "This is a chat handler"
    #     print data_in["msg"]
    #-----------end of handlers definition-------------------------------

    # -------- Constructor for the class obj ----------------------------
    def __init__(self, serverport, serverhost = None, handlers_list = None):
        self.serverport = int(serverport)
        self.myIP = self.getmyip()

        if serverhost:
            self.serverhost = serverhost
        else:
            self.serverhost = self.myIP
            
        self.serveraddr = (self.serverhost, self.serverport)
        self.shutdown   =  False
        self.MAX_PKT_SIZE = 512

        # if handlers_list == None:
        #     #Dictionary to handlers functions (TO BE CHANGED BY OUR APP)
        #     self.handler_dic = {"request" : self._handler_request, "chat" : self._handler_chat}
        # else:
        self.handler_dic = handlers_list
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

        while True:
            try:
                #Waiting for new data
                data, addr = sock.recvfrom(self.MAX_PKT_SIZE)

                if addr[0] != self.myIP:
                    data_out, data_in = self._unpack(data)
#                    print 'received %s bytes from %s' % (len(data), addr)
                    m_type = data_out["m_type"]

                    #Creating threads to handle new income data according to its type
                    t = threading.Thread(target = self.handler_dic[m_type], args = (data_in, addr))
                    t.start()

            except KeyboardInterrupt:
                self.shutdown = True

        sock.close()

    def _pack(self, message_type, data_in):
        data_in_packed = pickle.dumps(data_in)
        data_out = {"m_type" : message_type, "data" : data_in_packed }
        data_out_packed = pickle.dumps(data_out)
        return data_out_packed
     
    def sendto(self, addr , message_type, data_in):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) #Let port be reused when socket is closed
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #enable broadcast
        
        data_out_packed = self._pack(message_type, data_in)

        try:
	    for i in range (3):
            	sent = sock.sendto(data_out_packed, addr)
        finally:
            sock.close()

    def broadcast(self, message_type, data_in):
	for i in range (3):
       		self.sendto(('129.241.187.255',self.serverport), message_type, data_in)               

    def getmyip(self):
            dummysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dummysocket.connect(('8.8.8.8',80)) #connecting to google to find my IP
            return dummysocket.getsockname()[0]



def serverhand():
    net1 = networkUDP(27024) 
    print 'My IP is: ' + net1.getmyip()

    
    try:
        packed_data = net1.listen()
    except KeyboardInterrupt:
        print 'Keyboard int'
        sys.exit()



def clienthand():
    net2 = networkUDP(27024, serverhost = '')
    
    i = 1

    c_addr = ('129.241.187.48',27023)
    while True:

        i = i+1
        if(i%2):
            ms = {"floor": "3", "request_n": "4", "msg":"this is my message"}
            message_type = "request"
        else:
            ms = {"msg": "Hello dic World. This is a msg test"}
            message_type = "chat"

        try:
            net2.sendto(c_addr, message_type, ms)
        except KeyboardInterrupt:
            print 'Keyboard int'            
            sys.exit()
        time.sleep(3)

# def main():
#     ts = threading.Thread(target = serverhand)
#     tc = threading.Thread(target = clienthand)

#     ts.start()
#     tc.start()

# #   ts.join()
#     while tc.isAlive():
#         tc.join(5.0)




