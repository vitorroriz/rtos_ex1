import threading

from inElev import Elevator

def main():
	elevator1 = Elevator(serverport = 51012, hierarchy = {"129.241.187.155" : 0})
	print "Hello, my ip is:"
	print elevator1.net_server.getmyip()
	
	elevator1.run()


	while True:
		pass
	
	



if __name__ == '__main__':
	main()
