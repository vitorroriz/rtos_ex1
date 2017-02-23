import socket
import sys
import time
import struct
import threading
import pickle
from networkUDP import networkUDP


class Elevator(object):
	"""Class that represents the internals of the Elevator"""

	# -------- Handlers to received packets ----------------------------
	def _handler_request(self,data_in):
		print "REQUEST HANDLER FROM ELEVATOR"
		print "Contents of received packet:"
		print data_in["floor"]
		print data_in["request_n"]
		print data_in["msg"]
		print ""



	def _handler_chat(self,data_in):
		print "CHAT HANDLER FROM ELEVATOR"
		print "Contents of received packet:"
		print data_in["msg"]
		print ""

    #-----------end of handlers definition-------------------------------

    # def _listener(self, net_socket):
    # 	net_socket.listen()


	def __init__(self, elevatorID, master_or_slaven, serverport = 20023):
		#super(Elevator, self).__init__()
		self.elevatorID = elevatorID
		#defines if instace of elevator is a master (1) or slave(0)
		self.master_or_slave = master_or_slaven
		#Dictionary for registering the handlers for each kind of message received
		self.handler_dic = {"request" : self._handler_request, "chat" : self._handler_chat}
		#Creating a network object to receive messages
		self.net_server = networkUDP(serverport, handlers_list = self.handler_dic)
		#Creating a network object to send messages
		self.net_client = networkUDP(serverport)



	def goUP(self):
		#import function from driver
		print 'Elevator ' + str(self.elevatorID) + ' going UP'
	def goDown(self):
		#import function from driver
		print 'Elevator ' + str(self.elevatorID) + ' going UP'
	def stop(self):
		print 'Elevator ' + str(self.elevatorID) + ' stopped'
			


def main():
	elevator1 = Elevator(3,1,serverport = 27023)
	print "Hello, my ip is:"
	print elevator1.net_server.getmyip()

	elevator1.net_server.listen()




if __name__ == '__main__':
	main()


		