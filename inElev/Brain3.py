class Brain(object):
	"""docstring for Brain"""
	def __init__(self, system_info, externals, myIP, hierarchy, control_info, commands):
		self.system_info = system_info
		self.externals = externals
		self.hierarchy = hierarchy
		self.control_info = control_info
		self.commands = commands
		self.myIP = myIP
	def internal_next_destin(self):
		#empty dictionary to register potential internal requests to attend
		distances = {}
		#Reading the internal requests (and some external according to policy) and calculating the next destination
		for floor in self.commands.keys():
			if self.commands[floor] == 1:
				if(self.system_info[self.myIP]["lastDir"] == 0):
					distance_raw = abs(floor - self.system_info[self.myIP]["lastF"])
				else:
					distance_raw = (floor - self.system_info[self.myIP]["lastF"])*self.system_info[self.myIP]["lastDir"]
				if (distance_raw >= 0):
					distances[floor] = distance_raw
		try:
			#if there is some potential destin, min() will not fail and we take the nearest one
			destination = min(distances, key=distances.get)
			#return next destination calculated
			return destination
		except:
			#if there is no more potential destination for the internal part, min() causes an excepetion, then we 
			#declare that elevator stopped (lastDir = 0) and we release the elevator to be allocated to external 
			#requestions by the master (busy = 0)
			self.system_info[self.myIP]["lastDir"] = 0
			#Also we need to return -1 to signalize this event to the caller funciton
			return -1

	def external_next_destin(self, elevator_IP):
		#Returns the next_destin for a given elevator, based in the external requests
		distances = {}

		for floor in self.externals.keys():
			if  (((self.externals[floor][0] == 1) or (self.externals[floor][1] == 1)) and (self._is_destin_valid(floor))):
				distance_raw = abs(floor - self.system_info[elevator_IP]["lastF"])
				distances[floor] = distance_raw
		try:
			destination = min(distances, key=distances.get)
			return destination

		except:
			self.system_info[self.myIP]["lastDir"] = 0
			return -1


	def elevator_to_send(self, floor):
		distances = {}
		for elevator in self.hierarchy.keys():
			if ((self.system_info[elevator]["busy"] == 0) and (self.control_info[elevator]["dOa"]) and (self._is_destin_valid(floor))):
				distances[elevator] = abs(floor - self.system_info[elevator]["lastF"])
		try:
			elevator_selected = min(distances, key=distances.get)
			return elevator_selected
		except:
			return -1


	def _is_destin_valid(self, floor):
		for elevator in self.hierarchy.keys():
			if self.control_info[elevator]["ex_destin"] == floor:			
				return 0
		return 1
			
