class Brain(object):
	"""docstring for Brain"""
	def __init__(self, system_info_v, externals):
		self.system_info_v = system_info_v
		self.externals = externals


	def internal_next_destin(self):
		cf1 = self.system_info_v["cf1"]
		cf2 = self.system_info_v["cf2"] 
		cf3 = self.system_info_v["cf3"] 
		cf4 = self.system_info_v["cf4"] 
		internal_requests = {"cf1" : cf1 , "cf2" : cf2, "cf3" : cf3, "cf4" : cf4}
		i_dic_int = {"cf1" : 0, "cf2" : 1 , "cf3" : 2 , "cf4" : 3}
		distances = {}
		for i in internal_requests.keys():
			if internal_requests[i] != 0:
				if(self.system_info_v["lastDir"] == 0):
					distance_raw = abs(i_dic_int[i] - self.system_info_v["lastF"])
				else:
					distance_raw = (i_dic_int[i] - self.system_info_v["lastF"])*self.system_info_v["lastDir"]
				if (distance_raw > 0):
					distances[i] = distance_raw
		try:
			destination = min(distances, key=distances.get)
		except:
			self.system_info_v["lastDir"] = 0
			return self.system_info_v["lastF"]
		return i_dic_int[destination]




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