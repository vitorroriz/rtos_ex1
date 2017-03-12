import threading
import time
import datetime

from inElev3 import Elevator

def main():
	elevator1 = Elevator(serverport = 51012, hierarchy = {"129.241.187.48" : 0, "129.241.187.151" : 0, "129.241.187.143" : 0})

	elevator1 = Elevator(serverport = 51012, hierarchy = {"129.241.187.48" : 0})
	ip = elevator1.myIP
	print "Hello, my ip is:"
	print ip
	
	elevator1.run()


	while True:
		t = str(datetime.datetime.now().replace(microsecond=0))
		print t + " Elevator: " + elevator1.myIP + " busy = " + str(elevator1.system_info[ip]["busy"]) + " at floor " + str(elevator1.system_info[ip]["lastF"] )
		time.sleep(1)
	
	
	



if __name__ == '__main__':
	main()
