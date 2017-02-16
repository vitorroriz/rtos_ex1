#Exercise 3 in Python

import socket
import sys
import time
from threading import Thread

def receive():	
	print "Init receive!\n"
	port = 33546
	host = "129.241.187.255" # '' means all available interfaces
	host = "129.0.0.43" # '' means all available interfaces
	host = "129.241.187.43" 
	#TCP (datagram) socket creation
	try:
		s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print "Socket RCV created with host: " + host
	except	socket.error, msg:
		print "Failed to create scoket for RCV. Error code: " + str(msg[0]) + "Message " + msg
		sys.exit()

	server_addr = (host,port)
	s1.connect(server_addr)

	data_size_received = 0
	max_data_size = 1024
	data = ""

	while 1:
#		s1.send("Hello TCP World\0")

#		while "/0" not in data:

		while(data.find('\0')==-1):
			new_data = s1.recv(max_data_size)
			data = data + new_data
		print data
		data = ""
		s1.send("Hello TCP World\0")
#		data_size_received = len(data)
#		print data
#		data = ""
		time.sleep(2)
	s.close()













def send_read():
	print "Init send!"
	n = 23
	port = 20000 + n
	host = "129.241.187.48" 
	server_addr = "129.241.187.43"
	
		#UDP (datagram) socket creation
	try:
		s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		print "Socket SND created with host: " + host
	except	socket.error, msg:
		print "Failed to create socket for SND. Error code: " + str(msg[0]) + "Message " + msg
		sys.exit()


	#Trying to bind to a local host and port
	try:
		s2.bind((host,port))
	except socket.error, msg:
		print "Bind failed in SND. Error code. " + str(msg[0]) + msg[1]
		sys.exit()

	print "Socket bind complete for SND!"	

	full_server_addr = (server_addr,port)

	while 1:
		#try:
		print "Sending to port: " + str(full_server_addr[1])
		s2.sendto("Hello Socket World!", full_server_addr)

		data, addr = s2.recvfrom(1024)
		print "Message from: " + addr[0] + ":" + str(addr[1]) + ":"
		print data
		#except:
		#print "Failed to send!"
		#	sys.exit()

		time.sleep(3)

def main():

	print "Starting program!"
	rcv_thread = Thread(target = receive, args = (),)
	snd_thread = Thread(target = send_read, args = (),)


	rcv_thread.start()
	#snd_thread.start()

	rcv_thread.join()
	#snd_thread.join()


	"Program finished!"



main()









