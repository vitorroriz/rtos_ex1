#dsys
import socket
import sys
import time
import struct
import threading
import pickle

class networkUDP:
    'Class that defines a simple UDP server'
    # -------- Constructor for the class obj ----------------------------
    def __init__(self, serverport, elevatorsList,serverhost = None, handlers_list = None):
        self.serverport = int(serverport)
        self.myIP = self.getmyip()
        self.elevatorsList = elevatorsList
        #Variable and constants to handle network fault
        self.network_fault = 0
        #self.request_interface = "RI"
        #self.request_control = "RC"
        if serverhost:
            self.serverhost = serverhost
        else:
            self.serverhost = self.myIP
            
        self.serveraddr = (self.serverhost, self.serverport)
        self.MAX_PKT_SIZE = 512
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

    def _pack(self, message_type, data_in):
        #Serializing new data into out and in data packs
        data_in_packed = pickle.dumps(data_in)
        data_out = {"m_type" : message_type, "data" : data_in_packed }
        data_out_packed = pickle.dumps(data_out)
        return data_out_packed

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
                if(addr[0] in self.elevatorsList):
                    if (addr[0] != self.myIP):
                        data_out, data_in = self._unpack(data)
#                       print 'received %s bytes from %s' % (len(data), addr)
                        m_type = data_out["m_type"]
                        #Creating threads to handle new income data according to its type
                        t = threading.Thread(target = self.handler_dic[m_type], args = (data_in, addr))
                        t.start()
            except:
                print "FAULT: Failed to receive UDP packet due to problem in the Network."
                time.sleep(1)

        sock.close()
     
    def sendto(self, addr , message_type, data_in):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) #Let port be reused when socket is closed
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #enable broadcast
        
        data_out_packed = self._pack(message_type, data_in)
#        if (self.network_fault):
#            try:
#                sock.sendto(self._pack(self.request_control,""), addr)
#                sock.sendto(self._pack(self.request_interface,""), addr)
#                print "Network recovered!"
#            except:
#                print "FAULT: Failed to send UDP packet due to problem in the Network."
        try:
            for i in range (2):
            	sent = sock.sendto(data_out_packed, addr)
            self.network_fault = 0
        except:
            self.network_fault = 1
            print "FAULT: Failed to send UDP packet due to problem in the Network."
            time.sleep(1)
        finally:
            sock.close()

    def broadcast(self, message_type, data_in):       
   		self.sendto(('129.241.187.255',self.serverport), message_type, data_in)               

    def getmyip(self):
        dummysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dummysocket.connect(('8.8.8.8',80)) #connecting to google to find my IP
        return dummysocket.getsockname()[0]


