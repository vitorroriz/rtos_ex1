#Exercise 3 in Python

import socket


def main():
	#byte[1024] buffer
	
	print "Init 2:\n"
	port = 30000
	addr = "129.241.187.255"
	s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s1.bind((addr,port))
	print "waiting on port:", port
	while 1:
		data, addr = s1.recvfrom(1024)
		print "Message received from:\n" + str(addr)
		print data
		print dir(socket.AF_INET)


main()	
