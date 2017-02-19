import socket
import sys
import time

class UDPserver:
	'Class that defines a simple UDP server'

	def __init__(self, serverhost, serverport):
		self.serverport = int(serverport)
		self.serverhost = serverhost
		self.serveraddr = (self.serverhost, self.serverport)
		self.shutdown   =  False

	def makeserversocket(self):
		#Creating socket (UDP)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP socket
		#Bind socket to a port
		print 'Starting up on %s port %d' % self.serveraddr
		sock.bind(self.serveraddr)
		return sock

	def start(self):
		sock = self.makeserversocket()

		while not self.shutdown:
			try:
				#print '\nWaiting to receive message'
				data, addr = sock.recvfrom(512)

				print 'received %s bytes from %s' % (len(data), addr)
				print data

				if data:
					sent = sock.sendto(data,addr)
#					print 'sent %s bytes back to %s' % (sent,addr)
			except KeyboardInterrupt:
				self.shutdown = True
		sock.close()
		print '\nServer closed by Keyboard interruption'




def main():
	server1 = UDPserver('localhost', 5000)
	server1.start()

if __name__ == '__main__':
	main()