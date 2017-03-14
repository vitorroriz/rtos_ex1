import threading
import time
import datetime

from inElev3 import Elevator

def main():
	#list with the IPs of the allowed elevators in the system
	elevatorsList = {"129.241.187.145", "129.241.187.38"}
	#creating a elevator object, it needs a serverport, a elevator list and a number of floors
	elevator1 = Elevator(serverport = 51012, elevatorsList = elevatorsList, number_of_floors = 4)

	ip = elevator1.myIP
	print "Hello, my ip is:"
	print ip
	
	#running the whole system
	elevator1.run()

	#Just some information prints
	while True:
		t = str(datetime.datetime.now().replace(microsecond=0))
		print t + " Elevator: " + elevator1.myIP + " busy = " + str(elevator1.system_info[ip]["busy"]) + " at floor " + str(elevator1.system_info[ip]["lastF"] )
		print "Interface: " + str(elevator1.interface)
		print "SYSTEM:"
		print str(elevator1.system_info)
		print "CONTROL:"
		print str(elevator1.control_info)
		time.sleep(1)
	
	

if __name__ == '__main__':
	main()
