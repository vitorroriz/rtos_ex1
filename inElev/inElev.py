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
		floor = data_in["floor"]
		request_n = data_in["request_n"]



		print ""



	def _handler_chat(self,data_in):
		print "CHAT HANDLER FROM ELEVATOR"
		print "Contents of received packet:"
		print data_in["msg"]
		print ""

	def _handler_deadOa_question(self, data_in):
		#updating the status of masterAlive
		self.masterAlive = 1
		#fetching master address to reply to the question
		addr = (self.hierachy["master"], self.serverport)
		print "Dear or alive question handler, I will reply to: " + str(addr)
		#setting up the reply message and sendint it
		m_type = "dOa_r"
		msg = {"alive"}
		self.net_server.sendto(addr, m_type, msg)
		print ""

	def _handler_deadOa_reply(self,data_in):
		print "Dear or alive reply handler"
		print ""

	def _handler_switchmaster(self, data_in):
		print "Switch master handler"
		self.hierachy["master"] = self.hierachy["slave1"]
		self.hierachy["slave1"] = self.hierachy["slave2"]
		print ""

	def _handler_order(self, data_in):
		print "Handler order"

    #-----------end of handlers definition-------------------------------

	def __init__(self, elevatorID, masterID, serverport = 20023):
		self.serverport = serverport
		#Dictionary for the hierachy in the system
		self.hierachy = {"master" : "129.241.187.48", "slave1" : "129.241.187.155", "slave2" : "129.241.187.45"}
		#Dictionary for registering the handlers for each kind of message received
		self.handler_dic = {"request" : self._handler_request, "chat" : self._handler_chat, 
							"dOa_q" : self._handler_deadOa_question, "dOa_r" : self._handler_deadOa_reply}
		#Creating a network object to receive messages
		self.net_server = networkUDP(serverport, handlers_list = self.handler_dic)
		#Creating a network object to send messages
		self.net_client = networkUDP(serverport)

		self.myIP = self.net_server.getmyip()
		if self.hierachy["master"] ==  self.myIP:
			self.master_or_slaven = 1
		else:
			self.master_or_slaven = 0

		#Flag for slave1 monitor if the master is alive
		self.masterALive = 1
		#Tolerance in seconds to receive a question from master
		self.masterWatcher_tolerance = 4

		#COllection current external requests in the system for each floor
		#0 - > no request | 1 - > go up | 2 - > go down | 3 - > go up and down 
		self.ex_requests = {"F1" : 0, "F2" : 0, "F3" : 0 , "F4" : 0}

		





	def goUP(self):
		#import function from driver
		print 'Elevator ' + str(self.elevatorID) + ' going UP'
	def goDown(self):
		#import function from driver
		print 'Elevator ' + str(self.elevatorID) + ' going UP'
	def stop(self):
		print 'Elevator ' + str(self.elevatorID) + ' stopped'
	def _masterWatcher(self):
		while True:
			if not self.masterALive:
				self._switchmaster()
			else:
				self.masterALive = 0

			sys.sleep(masterWatcher_tolerance)

	def _switchmaster(self):
		#To be implemented -> call switchmaster handler and send switch master msg to everyone (BC)
		print "switch master function"


def main():
	elevator1 = Elevator(3,1,serverport = 27023)
	print "Hello, my ip is:"
	print elevator1.net_server.getmyip()
	print "Master = 1 Slave = 0 ---> master_or_slaven = " + str(elevator1.master_or_slaven)

	elevator1.net_server.listen()




if __name__ == '__main__':
	main()


		