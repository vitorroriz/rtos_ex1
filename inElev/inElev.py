import socket
import sys
import time
import struct
import threading
import pickle
import mutex
from ctypes import cdll

#Importing project modules
from networkUDP import networkUDP
from Brain import  Brain
#Elevator class
#-----------Definitions for the interface with the .C driver files-----
N_FLOORS = 4

N_BUTTONS = 3

DIRN_DOWN = -1
DIRN_STOP = 0
DIRN_UP = 1


BUTTON_CALL_UP = 0
BUTTON_CALL_DOWN = 1
BUTTON_COMMAND = 2
#--------------------------- end of definitions -----------------------

class Elevator(object):
	"""Class that represents the internals of the Elevator"""

	# -------- Handlers to received packets ----------------------------
	def _handler_master_order(self,data_in, addr):
		self.system_info_resource.acquire()
		self.system_info[self.myIP]["busy"] = 1
		self.system_info_resource.release()

		floor = data_in["floor"]
		self._go_to_destin_e(floor)
		self.system_info_resource.acquire()
		self.system_info[self.myIP]["busy"] = 0
		self.system_info_resource.release()



	def _handler_interface_update(self,data_in, addr):

		self.interface_resource.acquire()
		self.interface["uf1"] |= data_in["uf1"]
		self.interface["uf2"] |= data_in["uf2"]
		self.interface["uf3"] |= data_in["uf3"]

		self.interface["df2"] |= data_in["df2"]
		self.interface["df3"] |= data_in["df3"]
		self.interface["df4"] |= data_in["df4"]	
		self.interface_resource.release()

	def _handler_system_info_update(self, data_in, addr):
		self.system_info_resource.acquire()
		self.system_info[addr[0]]["cf1"] = data_in["cf1"]
		self.system_info[addr[0]]["cf2"] = data_in["cf2"]
		self.system_info[addr[0]]["cf3"] = data_in["cf3"]
		self.system_info[addr[0]]["cf4"] = data_in["cf4"]
		self.system_info[addr[0]]["stop"] = data_in["stop"]
		self.system_info[addr[0]]["M/MW/S"] = data_in["M/MW/S"]
		self.system_info[addr[0]]["lastF"] = data_in["lastF"]
		self.system_info[addr[0]]["lastDir"] = data_in["lastDir"]
		self.system_info[addr[0]]["busy"] = data_in["busy"]
		self.system_info_resource.release()
		
		
	def _handler_external_request_done(self, data_in, addr):
		self.interface_resource.acquire()
		self.interface["uf1"] &= data_in["uf1"]
		self.interface["uf2"] &= data_in["uf2"]
		self.interface["uf3"] &= data_in["uf3"]

		self.interface["df2"] &= data_in["df2"]
		self.interface["df3"] &= data_in["df3"]
		self.interface["df4"] &= data_in["df4"]	
		self.interface_resource.release()

	def _handler_deadOa_question(self, data_in, addr):
		#updating the status of masterAlive
		self.masterAlive = 1
		#fetching master address to reply to the question
		addr = (self.hierachy["master"], self.serverport)
		print "Dear or alive question handler, I will reply to: " + str(addr)
		#setting up the reply message and sendint it
		m_type = "dOa_r"
		msg = {"alive"}
		self.net_client.sendto(addr, m_type, msg)
		print ""

	def _handler_deadOa_reply(self,data_in, addr):
		print "Dear or alive reply handler"
		print ""

	def _handler_switchmaster(self, data_in, addr):
		print "Switch master handler"
		self.hierachy["master"] = self.hierachy["slave1"]
		self.hierachy["slave1"] = self.hierachy["slave2"]
		print ""

		print "Handler order"

    #-----------end of handlers definition-------------------------------

	def __init__(self, serverport = 20023):		
		self.broadcastaddr = "129.241.187.255"
		self.serverport = serverport
		#Dictionary for the hierachy in the system
		self.hierachy = {"129.241.187.38" : 0, "129.241.187.48" : 1}
	#	self.hierachy = {"129.241.187.153" : 0}


		#Number of elevators in the system
		self.number_of_elevators = len(self.hierachy)

		self.system_info = {}
		for i in self.hierachy.keys():
			self.system_info[i] = {"cf1" : 0, "cf2" : 0, "cf3" : 0, "cf4" : 0, "stop" : 0, 
									"M/MW/S" : self.hierachy[i], "lastF" : 0, "lastDir" : 0, "busy" : 0}

		self.system_info_resource = threading.Lock()
		self.interface_resource = threading.Lock()

		#Dictionary for registering the handlers for each kind of message received
		self.handler_dic = {"MO" : self._handler_master_order,  
							"dOa_q" : self._handler_deadOa_question, 
							"dOa_r" : self._handler_deadOa_reply,
							"IU" : self._handler_interface_update,
							"SU" : self._handler_system_info_update,
							"ERD" : self._handler_external_request_done}

		#Creating a network object to receive messages
		self.net_server = networkUDP(serverport, serverhost = None, handlers_list = self.handler_dic)
		#Creating a network object to broadcast
		self.net_bdcast = networkUDP(serverport, serverhost = self.broadcastaddr, handlers_list = self.handler_dic)

		#Creating a network object to send messages
		self.net_client = networkUDP(serverport)
		#Creating a driver object
		self.driver = cdll.LoadLibrary('./libelev.so')
		self.driver.elev_init()
		
		self.myIP = self.net_server.getmyip()
		self.master_or_slaven = self.system_info[self.myIP]["M/MW/S"]

		#Flag for slave1 monitor if the master is alive
		self.masterALive = 1
		#Tolerance in seconds to receive a question from master
		self.masterWatcher_tolerance = 4
		

		#Collection current external requests in the system for each floor
		self.interface = {"uf1" : 0, "uf2" : 0, "uf3" : 0, "df2" : 0, "df3" : 0, "df4" : 0}
		

		#Creating a Brain object
		self.brain = Brain(self.system_info, self.interface, self.myIP)
		
		self.thread_interfaceM  = threading.Thread(target = self.interfaceMonitor)
		self.thread_interfaceU  = threading.Thread(target = self.interfaceUpdate)
		self.thread_interfaceB  = threading.Thread(target = self._interfaceBroadcast)
		self.thread_systeminfoB = threading.Thread(target = self._systeminfoBroadcast)
		self.thread_positionM 	= threading.Thread(target = self.positionMonitor)
		self.thread_internalE   = threading.Thread(target = self.internal_exe)
		self.thread_externalE   = threading.Thread(target = self.external_exe)
		#Sending the lift to a known position (default = 0)
		self._system_init()

	def _interfaceBroadcast(self):
		while True:
			m_type =  "IU"
			self.interface.acquire()
			self.net_client.broadcast(m_type, self.interface)
			self.interface.release()			

			time.sleep(0.1)

	def _systeminfoBroadcast(self):
		while True:
			m_type = "SU"
			self.system_info_resource.acquire()
			self.net_client.broadcast(m_type, self.system_info[self.myIP])
			self.system_info_resource.release()
#			print self.system_info[self.myIP]["busy"]

			time.sleep(0.1)
				

	def interfaceMonitor(self):
		while True:

			self.interface_resource.acquire()
			self.interface["uf1"] |= self.driver.elev_get_button_signal(BUTTON_CALL_UP, 0)
			self.interface["uf2"] |= self.driver.elev_get_button_signal(BUTTON_CALL_UP, 1)
			self.interface["uf3"] |= self.driver.elev_get_button_signal(BUTTON_CALL_UP, 2)
		
			self.interface["df2"] |= self.driver.elev_get_button_signal(BUTTON_CALL_DOWN, 1)
			self.interface["df3"] |= self.driver.elev_get_button_signal(BUTTON_CALL_DOWN, 2)
			self.interface["df4"] |= self.driver.elev_get_button_signal(BUTTON_CALL_DOWN, 3)	
			self.interface_resource.release()

			self.system_info_resource.acquire()
			self.system_info[self.myIP]["cf1"] |= self.driver.elev_get_button_signal(BUTTON_COMMAND, 0)
			self.system_info[self.myIP]["cf2"] |= self.driver.elev_get_button_signal(BUTTON_COMMAND, 1)
			self.system_info[self.myIP]["cf3"] |= self.driver.elev_get_button_signal(BUTTON_COMMAND, 2)
			self.system_info[self.myIP]["cf4"] |= self.driver.elev_get_button_signal(BUTTON_COMMAND, 3)
			self.system_info[self.myIP]["stop"]|= self.driver.elev_get_stop_signal()
			self.system_info_resource.release()	
			time.sleep(0.1)	

	def interfaceUpdate(self):
		while True:

			self.interface_resource.acquire()
			self.driver.elev_set_button_lamp(BUTTON_CALL_UP, 0, self.interface["uf1"])
			self.driver.elev_set_button_lamp(BUTTON_CALL_UP, 1, self.interface["uf2"])
			self.driver.elev_set_button_lamp(BUTTON_CALL_UP, 2, self.interface["uf3"])

			self.driver.elev_set_button_lamp(BUTTON_CALL_DOWN, 1, self.interface["df2"])
			self.driver.elev_set_button_lamp(BUTTON_CALL_DOWN, 2, self.interface["df3"])
			self.driver.elev_set_button_lamp(BUTTON_CALL_DOWN, 3, self.interface["df4"])	
			self.interface_resource.release()	

			self.system_info_resource.acquire()
			self.driver.elev_set_button_lamp(BUTTON_COMMAND, 0, self.system_info[self.myIP]["cf1"])
			self.driver.elev_set_button_lamp(BUTTON_COMMAND, 1, self.system_info[self.myIP]["cf2"])
			self.driver.elev_set_button_lamp(BUTTON_COMMAND, 2, self.system_info[self.myIP]["cf3"])
			self.driver.elev_set_button_lamp(BUTTON_COMMAND, 3, self.system_info[self.myIP]["cf4"])
			self.driver.elev_set_stop_lamp(self.system_info[self.myIP]["stop"])
			self.driver.elev_set_floor_indicator(self.system_info[self.myIP]["lastF"])
			self.system_info_resource.release()
			time.sleep(0.1)

	def positionMonitor(self):
		while True:
			floor = self.driver.elev_get_floor_sensor_signal()
			if floor != -1:
				self.system_info_resource.acquire()
				self.system_info[self.myIP]["lastF"] = floor
				self.system_info_resource.release()
			time.sleep(0.01) #100 times per second






#	def go_to_destin(self, destination):
#		#Public method, it is in the class interface. Sends the elevator to a specific floor.
#		current = self.system_info[self.myIP]["lastF"]
#		distance = destination - current
#		if (distance > 0):
#			direction = 1
#		elif(distance < 0):
#			direction = -1
#		else:
#			self.system_info_resource.acquire()
#			self.system_info[self.myIP][translation[destination]] = 0
#			self.system_info_resource.release()
#			return

#		while(self.system_info[self.myIP]["lastF"] != destination):
#			self.driver.elev_set_motor_direction(direction)
#		self.driver.elev_set_motor_direction(0)





	def _go_to_destin(self, destination_o):
		#PRIVATE METHOD, it is not in the interface
		#Method to be used to execute internal orders
		translation = {0 : "cf1" , 1 : "cf2" , 2 : "cf3", 3 : "cf4"}
		translation_d = {1 : "df2" , 2 : "df3" , 3 : "df4"}
		translation_u = {0 : "uf1" , 1 : "uf2" , 2 : "uf3"}

#		print "GOING TO DESTINATION " + str(destination)
		destination = destination_o
		current = self.system_info[self.myIP]["lastF"]
		distance = destination - current
		if (distance > 0):
			direction = 1
		elif(distance < 0):
			direction = -1
		else:
			self.system_info_resource.acquire()
			self.system_info[self.myIP][translation[destination]] = 0
			self.system_info_resource.release()
			return

		self.system_info_resource.acquire()
		self.system_info[self.myIP]["lastDir"] = direction
		self.system_info_resource.release()

		while(self.system_info[self.myIP]["lastF"] != destination):
			destination = self.brain.internal_next_destin()
			self.driver.elev_set_motor_direction(direction)
			# self.system_info_resource.acquire()
			# self.system_info[self.myIP]["lastDir"] = direction
			# self.system_info_resource.release()

		self.driver.elev_set_motor_direction(0)


		self.system_info_resource.acquire()
		self.system_info[self.myIP][translation[destination]] = 0
		self.interface_resource.acquire()
		if((direction == 1)):
			if(destination == 3):
				self.interface[translation_d[destination]] = 0
				
			else:
				self.interface[translation_u[destination]] = 0 
			
		else:
			if(destination == 0):
				self.interface[translation_u[destination]] = 0
			else:
				self.interface[translation_d[destination]] = 0 
		self.net_client.broadcast("ERD",self.interface)
		self.interface_resource.release()
		self.system_info_resource.release()
#		Open the door for 3 seconds to the passagers to enter
		self.open_door(3)



	def _go_to_destin_e(self, destination_o):
		self.system_info_resource.acquire()
		self.system_info[self.myIP]["busy"] = 1
		self.system_info_resource.release()

		translation_d = {0: "uf1", 1 : "df2" , 2 : "df3" , 3 : "df4"}
		translation_u = {0: "uf1" , 1 : "uf2" , 2 : "uf3", 3 : "df4"}

#		print "GOING TO DESTINATION " + str(destination)
		destination = destination_o
		current = self.system_info[self.myIP]["lastF"]
		distance = destination - current
		if (distance > 0):
			direction = 1
		elif(distance < 0):
			direction = -1
		else:
			self.interface_resource.acquire()
			self.interface[translation_u[destination]] = 0
			self.interface[translation_d[destination]] = 0
			self.net_client.broadcast("ERD",self.interface)
			self.interface_resource.release()
					
			self.open_door(3)
			
			self.system_info_resource.acquire()
			self.system_info[self.myIP]["busy"] = 0
			self.system_info_resource.release()
			return

		self.system_info_resource.acquire()
		self.system_info[self.myIP]["lastDir"] = direction
		self.system_info_resource.release()

		while(self.system_info[self.myIP]["lastF"] != destination):
			#destination = self.brain.external_next_destin(self.myIP)
			self.driver.elev_set_motor_direction(direction)


		self.driver.elev_set_motor_direction(0)

		#		Open the door for 3 seconds to the passagers to enter
		self.open_door(3)
		

		self.interface_resource.acquire()
		self.interface[translation_u[destination]] = 0
		self.interface[translation_d[destination]] = 0
		self.net_client.broadcast("ERD",self.interface)
		self.interface_resource.release()


		self.system_info_resource.acquire()
		self.system_info[self.myIP]["busy"] = 0
		self.system_info_resource.release()




	def open_door(self, time_s):
		self.driver.elev_set_door_open_lamp(1)
		time.sleep(time_s)
		self.driver.elev_set_door_open_lamp(0)

	def master_order(self, elevator_IP, floor_n):
		#Function to be called by the master, send a message of the MO (maste order) type,
		#ordering a elevator to go to a specific floor to attend a external request
		m_type = "MO"
		msg = {"floor": floor_n}
		addr = (elevator_IP, self.serverport)
		self.net_client.sendto(addr, m_type, msg)

	def internal_exe(self):
		while True:
			destin = self.brain.internal_next_destin()
			self._go_to_destin(destin)
#			print "Destin: " + str(destin)
			time.sleep(1)
			print self.interface
			print self.myIP + " ---> busy = " + str(self.system_info[self.myIP]["busy"])

	def external_exe(self):
		while True:
			#checking if i am the master
			if (self.master_or_slaven == 0):
				for elevator_IP in self.hierachy.keys():
					self.system_info_resource.acquire()
					if self.system_info[elevator_IP]["busy"] != 1:
						self.system_info_resource.release()
						destin = self.brain.external_next_destin(elevator_IP)
						if destin != -1:
							if (elevator_IP == self.myIP):
								print "IVE GOT MY DESTIN"
								#self._go_to_destin_e(destin)
								self.system_info[self.myIP]["busy"] = 1
								thread_execution = threading.Thread(target = self._go_to_destin_e, args = (destin,))
								thread_execution.start()
								print "I AM DONE WITH THE MOVEMENT"

							else:			
								self.master_order(elevator_IP, destin)
								print "I SENT THIS ORDER TO " + elevator_IP + ":" + str(self.serverport) 
					else:
						#if the elevator is busy, dont do nothing, just remeber to release the resource
						self.system_info_resource.release()
					time.sleep(0.5) #sleep for a while inside the floor so the elevator can take the order
#			print "Destin: " + str(destin)
			time.sleep(1)
		

	def _system_init(self):
		floor = -1
		while floor != 0:
			self.driver.elev_set_motor_direction(-1)
			floor = self.driver.elev_get_floor_sensor_signal()
		self.driver.elev_set_motor_direction(0)

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
	elevator1 = Elevator(serverport = 51012)
	print "Hello, my ip is:"
	print elevator1.net_server.getmyip()
	print "Master = 1 Slave = 0 ---> master_or_slaven = " + str(elevator1.master_or_slaven)
	
	thread_server = threading.Thread(target = elevator1.net_server.listen)
	
	elevator1.thread_interfaceM.start()
	elevator1.thread_interfaceU.start()
	elevator1.thread_interfaceB.start()
	elevator1.thread_systeminfoB.start()
	elevator1.thread_positionM.start()
	elevator1.thread_internalE.start()
	elevator1.thread_externalE.start()	

#	while True:
#		m_type = "request"
#		ms = {"floor": "3", "request_n": "4", "msg":"this is my message"}
#		elevator1.net_client.broadcast(m_type, ms)
#		time.sleep(2)

	thread_server.start()
	elevator1.net_bdcast.listen()


	elevator1.thread_interfaceM.join()
	elevator1.thread_interfaceU.join()
	elevator1.thread_interfaceB.join()
	elevator1.thread_systeminfoB.join()
	elevator1.thread_positionM.join()
	elevator1.thread_internalE.join()
	elevator1.thread_externalE.join()
	thread_server.join()

if __name__ == '__main__':
	main()


		
