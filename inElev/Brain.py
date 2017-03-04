class Brain(object):
	"""docstring for Brain"""
	def __init__(self, system_info, externals, myIP, hierarchy, control_info):
		self.system_info = system_info
		self.system_info_v = system_info[myIP]
		self.externals = externals
		self.hierarchy = hierarchy
		self.control_info = control_info

	def internal_next_destin(self):
		#saving the status of the internal buttons for a specific elevator
		cf1 = self.system_info_v["cf1"]
		cf2 = self.system_info_v["cf2"] 
		cf3 = self.system_info_v["cf3"] 
		cf4 = self.system_info_v["cf4"] 

		#translation for the dictionaries
		internal_requests = {"cf1" : cf1 , "cf2" : cf2, "cf3" : cf3, "cf4" : cf4}
		i_dic_int = {"cf1" : 0, "cf2" : 1 , "cf3" : 2 , "cf4" : 3}

		#empty dictionary to register potential internal requests to attend
		distances = {}

		#Reading the internal requests (and some external according to policy) and calculating the next destination
		for i in internal_requests.keys():
			if internal_requests[i] != 0:
				if(self.system_info_v["lastDir"] == 0):
					distance_raw = abs(i_dic_int[i] - self.system_info_v["lastF"])
				else:
					distance_raw = (i_dic_int[i] - self.system_info_v["lastF"])*self.system_info_v["lastDir"]
				if (distance_raw > 0):
					distances[i] = distance_raw
		try:
			#if there is some potential destinal, min() will not fail and we take the nearest one
			destination = min(distances, key=distances.get)
			#self.system_info_v["busy"] = 1
			#return next destination calculated
			return i_dic_int[destination]
		except:
			#if there is no more potential destination for the internal part, min() causes an excepetion, then we 
			#declare that elevator stopped (lastDir = 0) and we release the elevator to be allocated to external 
			#requestions by the master (busy = 0)
			self.system_info_v["lastDir"] = 0
			#self.system_info_v["busy"] = 0
			#Also we need to return the current floor (lastF) as the next destination
			return -1


	def external_next_destin(self, elevator_IP):
		#Returns the next_destin for a given elevator, based in the external requests

		#translation for the dictionaries
#		translation_d = {1 : "df2" , 2 : "df3" , 3 : "df4"}
#		translation_u = {0 : "uf1" , 1 : "uf2" , 2 : "uf3"}
		i_dic_ext = {"uf1" : 0 , "uf2" : 1, "uf3" : 2, "df2" : 1, "df3" : 2, "df4" : 3}
		
		distances = {}
		print "BRAIN: Ex requests = " + str(self.externals)
		for button in self.externals.keys():
			if  ((self.externals[button] != 0) and (self._is_destin_valid(button, elevator_IP))):
				distance_raw = abs(i_dic_ext[button] - self.system_info[elevator_IP]["lastF"])
				distances[button] = distance_raw
		try:
			destination = min(distances, key=distances.get)
			return i_dic_ext[destination]
			#print "A"
		except:
			self.system_info_v["lastDir"] = 0
			#self.system_info_v["busy"] = 0
			#print "B"
			#return self.system_info_v["lastF"]
			return -1


	def _is_destin_valid(self, button, elevator_IP):
		i_dic_ext = {"uf1" : 0 , "uf2" : 1, "uf3" : 2, "df2" : 1, "df3" : 2, "df4" : 3}
		
		for elevator in self.hierarchy.keys():
			print "ex_destin of " + elevator + " is " + str(self.control_info[elevator]["ex_destin"])
			if self.control_info[elevator]["ex_destin"] == i_dic_ext[button]:
				print "BRAIN: returning 0 for button " + button + " elevator: " + elevator_IP + " because of " + elevator 			
				return 0
	
		return 1
			



	# def _internal_dir(self,current_floor, internal_request):
	# 	if (internal_request - current_floor) < 0: return -1
	# 	else: return 1 

	# def set_destination(self):
	# i_dic_int = {"cf1" : 0, "cf2" : 1 , "cf3" : 2 , "cf4" : 3}
	# i_dic_ext = {"uf1" : 0 , "uf2" : 1, "uf3" : 2, "df2" : 1, "df3" : 2, "df4" : 3}
	# dic_dir_ext = {"uf1" : 1, "uf2" : 1 , "uf3" : 1, "df2" : -1, "df3" : -1, "df4" : -1}



	# internal_distances = {}

	# 	for i in self.internals:
	# 		if self.internals[i]:
	# 			internal_dir_req = self._internal_dir(system_info_v["lastF"], i_dic_int[i])
	# 			current_dir = self.system_info_v["lastDir"]
	# 			if ((internal_dir_req == current_dir) || current_dir == 0):
	# 				internal_distances[i] = i_dic_int[i] -  system_info_v["lastF"]
		
# 	