import socket
import sys
import time

class UDPclient:
	'Class that defines a simple UDP client '

	def __init__(self, serverhost, serverport):
		self.serverport = int(serverport)
		self.serverhost = serverhost
		self.serveraddr = (self.serverhost, self.serverport)
		
	
	def send(self, message = 'This is the client default message :D!'):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#		sock.bind(self.)

		try:
#		print 'Sending "%s"' % message
			sent = sock.sendto(message, self.serveraddr)

#			print 'Waiting to receive'
			data, server = sock.recvfrom(512)
#			print 'received "%s" from %s' % (data,server)

		finally:
#			print 'closing client socket'
			sock.close()

def main():
	client1 = UDPclient('localhost', 5000)
	while True:
		message = raw_input('-> ')
		client1.send(message)

if __name__ == '__main__':
	main()