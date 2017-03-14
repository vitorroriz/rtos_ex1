#dsys
import socket
import sys
import time
import struct
import threading
import pickle
import mutex
import datetime
from ctypes import cdll

#Importing project modules
from networkUDP import networkUDP
from Brain3 import  Brain

class Elevator(object):
	"""Class that represents an Elevator"""

	# -------- Handlers to received messages to pass to the Network ----------------------------
	def _handler_send_order(self,data_in, addr):
		#Looking the floor the elevator told thigo
		floor = data_in["floor"]
		#Sending the elevator to the destin required
		self._go_to_destin_e(floor)
		print "I've got an order from elevator %s " %addr[0]

	def _handler_update_control_info(self,data_in,addr):
		elevator_IP  = data_in["elevator_IP"]
		ex_destin = data_in["ex_destin"]
		dOa = data_in["dOa"]
		LRT = data_in["LRT"]

		if  ex_destin != None:
			self.control_info[elevator_IP]["ex_destin"] = ex_destin
		if dOa != None:
			self.control_info[elevator_IP]["dOa"] = dOa
		if LRT != None:
			self.control_info[elevator_IP]["LRT"] = LRT

	def _handler_interface_update(self,data_in, addr):
		self.interface_resource.acquire()
		for floor in range(self.number_of_floors):
			for button in range(2):
				self.interface[floor][button] |= data_in[floor][button]
		self.interface_resource.release()

	def _handler_system_info_update(self, data_in, addr):
		self.system_info_resource.acquire()
		self.system_info[addr[0]]["lastF"] = data_in["lastF"]
		self.system_info[addr[0]]["lastDir"] = data_in["lastDir"]
		self.system_info[addr[0]]["busy"] = data_in["busy"]
		self.system_info_resource.release()

	def _handler_external_request_done(self, data_in, addr):
		self.interface_resource.acquire()
		for floor in range(self.number_of_floors):
			for button in range(2):
				self.interface[floor][button] &= data_in[floor][button]
		self.interface_resource.release()

	def _handler_deadOa_question(self, data_in, addr):
		#setting up the reply message and sendint it
		m_type = "dOa_r"
		addr_to_reply = (addr[0], self.serverport) 
		self.net_client.sendto(addr_to_reply, m_type,"")

	def _handler_deadOa_reply(self,data_in, addr):
		self.control_info[addr[0]]["dOa"] = 1
		self.control_info[addr[0]]["LRT"] = time.time()
		self._update_control_info(addr[0], None, None, self.control_info[addr[0]]["LRT"], None)

	def _handler_request_interface(self, data_in, addr):
		#Elevator informs his current values for interface 
		addr_to_reply = (addr[0], self.serverport)
		m_type = "IU"
		self.net_client.sendto(addr_to_reply, m_type, self.interface)

	def _handler_request_control_info(self, data_in, addr):
		m_type = "DU"
		msg = {"elevator_IP" : self.myIP, "ex_destin": self.control_info[self.myIP]["ex_destin"], "dOa" : self.control_info[self.myIP]["dOa"] , "LRT" : self.control_info[self.myIP]["LRT"]}
		self.net_client.sendto((addr[0],self.serverport),m_type, msg)
    #-----------end of handlers definition--------------------------------------------------------------

    # ---------- Class Constructor ---------------------------------------------------------------------
	def __init__(self ,serverport = 20023, elevatorsList = None, number_of_floors = 4):		
		self.broadcastaddr = "129.241.187.255"
		self.serverport = serverport
		#Dictionary for the elevatorsList in the system
		if (elevatorsList == None):
			self.elevatorsList = {"129.241.187.48", "129.241.187.38", "129.241.187.46"}
		else:
			self.elevatorsList = elevatorsList
		#Number of elevators in the system
		self.number_of_elevators = len(self.elevatorsList)
		#NUmber of floors
		self.number_of_floors = number_of_floors
		#Initializing data structures
		self.system_info = {}
		self.control_info = {}
		self.interface = {}
		self.commands = {}
		for elevator in self.elevatorsList:
			self.system_info[elevator] =  {"lastF" : 0, "lastDir" : 0, "busy" : 0}
			self.control_info[elevator] = {"ex_destin" : -1, "dOa" : 1, "LRT" : time.time()}

		for floor in range(self.number_of_floors):
		#Current external requests in the system for each floor (interface)
			self.interface[floor] = {0 : 0 , 1 : 0}
		#Current internal requests in the elevator for each floor (commands)
			self.commands[floor] = 0
		#mutex to control access to the system info table
		self.system_info_resource = threading.Lock()
		#mutex to control access to the interface 	
		self.interface_resource = threading.Lock()
		#mutex to control acess to the commands
		self.commands_resource = threading.Lock()
		#mutex to control access to the motor
		self.motor_resource = threading.Lock()
		#Dictionary for registering the handlers for each kind of message received
		self.handler_dic = {"MO"    : self._handler_send_order,  
							"dOa_q" : self._handler_deadOa_question, 
							"dOa_r" : self._handler_deadOa_reply,
							"IU"    : self._handler_interface_update,
							"SU"    : self._handler_system_info_update,
							"ERD"   : self._handler_external_request_done,
							"DU"    : self._handler_update_control_info,
							"RI"    : self._handler_request_interface,
							"RC"	: self._handler_request_control_info}

		#Creating a network object to receive messages
		self.net_server = networkUDP(serverport, elevatorsList, serverhost = None, handlers_list = self.handler_dic)
		#Creating a network object to listen to broadcast messages
		self.net_bdcast = networkUDP(serverport, elevatorsList, serverhost = self.broadcastaddr, handlers_list = self.handler_dic)
		#Creating a network object to send messages
		self.net_client = networkUDP(serverport, elevatorsList)
		#Creating a driver object
		self.driver = cdll.LoadLibrary('./libelev2.so')
		self.driver.elev_init(1) #0-> elevator hardware, #1-> elevator simulator
		#getting my IP
		self.myIP = self.net_server.getmyip()
		#Tolerance in seconds to  receive a reply of dead or alive question from a other instance of elevator
		self.dead_or_alive_tolerance_time = 7
		#Tolerance in seconds to consider the motor with problems (power loss or elevator stuck in rail)
		self.motor_loss_tolerance_time = 10
		#Creating a Brain object for the elevator
		self.brain = Brain(self.system_info, self.interface, self.myIP, self.elevatorsList, self.control_info, self.commands)
		#Threads of the elevator object
		self.thread_buttonsM    = threading.Thread(target = self._buttonsMonitor)
		self.thread_interfaceU  = threading.Thread(target = self._lightsUpdate)
		self.thread_interfaceB  = threading.Thread(target = self._interfaceBroadcast)
		self.thread_systeminfoB = threading.Thread(target = self._systeminfoBroadcast)
		self.thread_positionM 	= threading.Thread(target = self._positionMonitor)
		self.thread_internalE   = threading.Thread(target = self._internal_exe)
		self.thread_externalE   = threading.Thread(target = self._external_exe)
		self.thread_dOa_M       = threading.Thread(target = self._dead_or_alive_monitor)
		self.thread_server      = threading.Thread(target = self.net_server.listen)
		self.thread_server_bdc  = threading.Thread(target = self.net_bdcast.listen)
		#Sending the lift to a known position (default = 0)
		self._system_init()
 	# ---------- End of Class Constructor ---------------------------------------------------------------------

 	# ---------- Elevator Public functions (Interface) --------------------------------------------------------
	def run(self):
	#Start object threads
		self.thread_buttonsM.start()
		self.thread_interfaceU.start()
		self.thread_interfaceB.start()
		self.thread_systeminfoB.start()
		self.thread_positionM.start()
		self.thread_internalE.start()
		self.thread_externalE.start()	
		self.thread_dOa_M.start()
		self.thread_server.start()
		self.thread_server_bdc.start()
		
		self._request_control_info();
		self._request_interface();
	
		# self.thread_buttonsM.join()
		# self.thread_interfaceU.join()
		# self.thread_interfaceB.join()
		# self.thread_systeminfoB.join()
		# self.thread_positionM.join()
		# self.thread_internalE.join()
		# self.thread_externalE.join()
		# self.thread_server.join()
		# self.thread_dOa_M.join()

# ---------- Elevator Private functions (Not in Interface) -------------------------------------------------------
	def _buttonsMonitor(self):
		while True:
			change_in_interface = 0
			self.interface_resource.acquire()
			for floor in range (self.number_of_floors):
				for button in range (2):
					current_value = self.driver.elev_get_button_signal(button, floor)
					if ((current_value == 1 ) and (self.interface[floor][button] == 0)):
						self.interface[floor][button] = 1
						change_in_interface = 1
			if(change_in_interface):
				self._interfaceBroadcast()	
			self.interface_resource.release()
				
			self.commands_resource.acquire()
			for floor in range (self.number_of_floors):
				self.commands[floor] |= self.driver.elev_get_button_signal(2, floor)
			self.commands_resource.release()	

			time.sleep(0.25)	

	def _positionMonitor(self):
		while True:
			floor = self.driver.elev_get_floor_sensor_signal()
			if floor != -1:
				self.system_info[self.myIP]["lastF"] = floor
			time.sleep(0.1) 

	def _lightsUpdate(self):
		while True:
			self.interface_resource.acquire()
			self.commands_resource.acquire()
			for floor in range(self.number_of_floors):
				self.driver.elev_set_button_lamp(2, floor, self.commands[floor])
				for button in range(2):		
					self.driver.elev_set_button_lamp(button, floor, self.interface[floor][button])
			self.commands_resource.release()
			self.interface_resource.release()
			
			self.driver.elev_set_floor_indicator(self.system_info[self.myIP]["lastF"])
			time.sleep(0.25)

	def _open_door(self, time_s):
		self.driver.elev_set_door_open_lamp(1)
		time.sleep(time_s)
		self.driver.elev_set_door_open_lamp(0)

	def _system_init(self):
		floor = -1
		while floor != 0:
			self.driver.elev_set_motor_direction(-1)
			floor = self.driver.elev_get_floor_sensor_signal()
		self.driver.elev_set_motor_direction(0)

		for elevator in self.elevatorsList:
			self.system_info[elevator]["LRT"] = time.time()

	def _interfaceBroadcast(self):
		m_type =  "IU"
		self.net_client.broadcast(m_type, self.interface)			

	def _systeminfoBroadcast(self):
		while True:
			m_type = "SU"
			self.system_info_resource.acquire()
			self.net_client.broadcast(m_type, self.system_info[self.myIP])
			self.system_info_resource.release()
			time.sleep(0.1)

	def _request_interface(self):
		self.net_client.broadcast("RI","")

	def _request_control_info(self):
		self.net_client.broadcast("RC","")

	def _set_busy_state(self, busy_state):
		if (busy_state == 0):
			self.system_info_resource.acquire()
			self.system_info[self.myIP]["busy"] = 0
			self.system_info_resource.release()
			print "Releasing the motor."
			#releasing the control of the motor
			self.motor_resource.release() 
		else:
			self.system_info_resource.acquire()
			self.system_info[self.myIP]["busy"] = 1
			self.system_info_resource.release()
			#taking the control of the motor
			print "Elevator will move. Acquiring motor."
			self.motor_resource.acquire() 

	def _clear_internal_request(self, destination):
		self.commands_resource.acquire()
		self.commands[destination] = 0
		self.commands_resource.release()

	def _clear_external_request(self, floor, button):
		#0 -> clear button up | 1 -> clear button down | 2 -> clear both
		if(floor != -1):
			if button == 2:
				self.interface_resource.acquire()
				self.interface[floor][0] = 0 
				self.interface[floor][1] = 0 
				self.net_client.broadcast("ERD",self.interface)
				self.interface_resource.release()
				return
			self.interface_resource.acquire()
			self.interface[floor][button] = 0 
			self.net_client.broadcast("ERD",self.interface)
			self.interface_resource.release()

	def _number_of_internal_requests(self):
		c = 0
		for floor in range (self.number_of_floors):
			if self.commands[floor] == 1:
				c = c + 1
		return c

	def _go_to_destin(self, destination_o):
		#Method to be used to execute internal orders
		while(self._number_of_internal_requests != 0):
			destination = self.brain.internal_next_destin()	
			print "Going to " + str(destination)

			print "Number of requests = " + str(self._number_of_internal_requests())
			current = self.system_info[self.myIP]["lastF"]
			distance = destination - current
			if (distance > 0):
				direction = 1
			elif(distance < 0):
				direction = -1
			else:
				self.driver.elev_set_motor_direction(0)
				self._clear_internal_request(destination)
				direction = 0
				
			self.system_info_resource.acquire()
			self.system_info[self.myIP]["lastDir"] = direction
			self.system_info_resource.release()

			print "going to " + str(destination)
			#Keep the elevator moving till it arrives in its destination
			time_init = time.time()
			while(self.driver.elev_get_floor_sensor_signal() != destination):
				
				#Recalculating internal destination in case there is a floor to stop in the same direction the elevator is going
				time.sleep(0.01) #just to guarantee chances of preemption
				destination = self.brain.internal_next_destin()
				if destination == -1:
					self.system_info[self.myIP]["lastDir"] = 0
					print "Here!"
					return 
					
				self.driver.elev_set_motor_direction(direction)
				if((int)(time.time() - time_init) > self.motor_loss_tolerance_time):
					self._power_loss_handler(external_internaln = 0, destination = destination)
					
			self.driver.elev_set_motor_direction(0)
			self._clear_internal_request(destination)
			
			if((direction == 1)):
				if(destination == 3):	
					self._clear_external_request(destination,1)		
				else:
					self._clear_external_request(destination,0)				
			else:
				if(destination == 0):
					self._clear_external_request(destination,0)
				else:
					self._clear_external_request(destination,1)
	#		Open the door for 3 seconds to the passagers to enter
			self._open_door(3)

	def _go_to_destin_e(self, destination_o):
		#elevator is busy
		self._set_busy_state(1)

		destination = destination_o
		current = self.system_info[self.myIP]["lastF"]
		distance = destination - current
		if (distance > 0):
			direction = 1
		elif(distance < 0):
			direction = -1
		else:
			self.driver.elev_set_motor_direction(0)
			self._clear_external_request(destination,2)
			#Open the door for 3 seconds to the passagers to enter
			self._open_door(3)
			self.control_info[self.myIP]["ex_destin"] = -1
			self._update_control_info(self.myIP, -1, None, None, None)
			#Elevator is not busy anymore		
			self._set_busy_state(0)
			return

		self.system_info_resource.acquire()
		self.system_info[self.myIP]["lastDir"] = direction
		self.system_info_resource.release()
		time_init = time.time()

		while(self.driver.elev_get_floor_sensor_signal() != destination):
			#destination = self.brain.external_next_destin(self.myIP)
			self.driver.elev_set_motor_direction(direction)
			time_now = time.time()
			#If the movement takes more than 10 seconds, stop movement, declare elevator as dead, and release its ex_destin to be taken by other elevator
			time.sleep(0.01) #just to guarantee chances of preemption
			if((int)(time_now - time_init) > self.motor_loss_tolerance_time):
				self._power_loss_handler(external_internaln = 1, destination = destination)
				return 	

		self.driver.elev_set_motor_direction(0)
		self._clear_external_request(destination,2)
		#Open the door for 3 seconds to the passagers to enter
		self._open_door(3)
		self.control_info[self.myIP]["ex_destin"] = -1
		self._update_control_info(self.myIP, -1, None, None, None)
		#Elevator is not busy anymore 
		self._set_busy_state(0)
		print "Movement done!"

	def _send_order(self, elevator_IP, floor_n):
		#Send a message of MO type (an order),
		#ordering an elevator to go to a specific floor to attend a external request
		m_type = "MO"
		msg = {"floor": floor_n}
		addr = (elevator_IP, self.serverport)
		self.net_client.sendto(addr, m_type, msg)

	def _update_control_info(self, elevator_IP, ex_destin, dOa, LRT, MMWS):
		m_type = "DU"
		msg = {"elevator_IP" : elevator_IP, "ex_destin": ex_destin, "dOa" : dOa , "LRT" : LRT}
		self.net_client.broadcast(m_type, msg)
		
	def _internal_exe(self):
		while True:
			if self.system_info[self.myIP]["busy"] == 0:
#				print "Remaining IR = " + str(self._number_of_internal_requests())
				if(self._number_of_internal_requests() > 0):
					self._set_busy_state(1)
					print "Elevator busy due to internal requests" 
					self._go_to_destin(0)
					print "Internals: RELEASING MOTOR!"
					self._set_busy_state(0)
				else:
					self._clear_internal_request(self.system_info[self.myIP]["lastF"])
			time.sleep(1)

	def _external_exe(self):
		i_dic_ext = {"uf1" : 0 , "uf2" : 1, "uf3" : 2, "df2" : 1, "df3" : 2, "df4" : 3}
		while True:
			for floor in self.interface.keys():
				self.interface_resource.acquire()
				if ( (self.interface[floor][0] == 1) or (self.interface[floor][1] == 1 )):
					self.interface_resource.release()
					elevator_to_send = self.brain.elevator_to_send(floor)
					if elevator_to_send != -1:
						print "Sending : " + elevator_to_send + " to attend the floor %i" %floor  
						self.control_info[elevator_to_send]["ex_destin"] = floor
						self._update_control_info(elevator_to_send, floor, None, None, None)						
						if (elevator_to_send == self.myIP):
							print "Sending a thread to handle my movement"
							thread_execution = threading.Thread(target = self._go_to_destin_e, args = (floor,))
							thread_execution.start()
						else:			
							self._send_order(elevator_to_send, floor)
							print "I SENT THIS ORDER TO " + elevator_to_send + ":" + str(self.serverport) 
				else:		
					self.interface_resource.release()
				time.sleep(1) #sleep for a while inside the floor so the elevator can take the order

	# ---------- Extra functions for Fault handling (dead elevator and motor loss, network handles itself)------------------------
	def _dead_or_alive_monitor(self):
		while True:
			m_type = "dOa_q"
			self.net_client.broadcast(m_type, "")
			current_time = time.time()
			for elevator in self.elevatorsList:
				if ( (elevator != self.myIP) and (self.control_info[elevator]["dOa"] == 1)):
					if(int(current_time - self.control_info[elevator]["LRT"]) > self.dead_or_alive_tolerance_time):
						#declare elevator as dead
						self.control_info[elevator]["dOa"] = 0
						#release its ex_destin field, so we can attend a possible external destin the elevator was going before
						self.control_info[elevator]["ex_destin"] = -1 
						#broadcasting the new ex_destin (-1) and the new dOa value to update the control_info
						self._update_control_info(elevator, -1, 0, None, None) #broadcast
						print "ALERT: ELEVATOR %s is DEAD or under problems for now!" %(elevator)
			time.sleep(1.5)
	
	def _power_loss_handler(self, external_internaln, destination = None):
		self.control_info[self.myIP]["dOa"] = 0
		self.control_info[self.myIP]["ex_destin"] = -1
		self._update_control_info(self.myIP, -1, 0, None, None)
		print "FAULT: Elevator got stuck while moving to floor %i. Possible causes: Motor power loss, problems in the rail." %(destination)

		while(self.driver.elev_get_floor_sensor_signal() != destination):
			time.sleep(0.01)

		self.driver.elev_set_motor_direction(0)
		print "Motor recovered!"	
		self.control_info[self.myIP]["dOa"] = 1
		self.control_info[self.myIP]["ex_destin"] = -1
		self._update_control_info(self.myIP, -1, 1, None, None)

		if(external_internaln):
			self._set_busy_state(0)

	
