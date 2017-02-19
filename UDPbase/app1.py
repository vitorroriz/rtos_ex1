import socket
import sys
import time
from serverUDP import UDPserver
from clientUDP import UDPclient
import threading

def serverhand():
	server1 = UDPserver('localhost', 5200)
	server1.start()

def clienthand():
	client1 = UDPclient('localhost', 5300)
	while True:
		try:
			message = raw_input('-> ')
			client1.send(message)
		except KeyboardInterrupt:
			print 'Keyboard int'			
			sys.exit()
def main():
	
	

	ts = threading.Thread(target = serverhand)
	tc = threading.Thread(target = clienthand)

	ts.start()
	tc.start()

#	ts.join()
	while tc.isAlive():
		tc.join(5.0)

if __name__ == '__main__':
	main()