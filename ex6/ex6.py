#exercise 6: backup
import sys
import socket
import select
import os
import time

from networkUDP import networkUDP

def work(i=0):
	i = i+1
	print i
	time.sleep(1)
	return i

def create_backup():
	os.system('gnome-terminal -x python ex6.py 0')

def main():
	isPrimary = int(sys.argv[1])
	time_out_s = 2
	server_add = ('localhost', 27023)
	i = 0


	if not isPrimary:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		sock.bind(server_add)
		#socket.setblocking(0)

		while not isPrimary:
			ready = select.select([sock],[],[], time_out_s)
			if ready[0]:
				data, addr = sock.recvfrom(512)
				i = int(data)
			else:
				sock.close()
				i = i + 1
				isPrimary = True
	if isPrimary:
		create_backup()
		while True:
			i = work(i)
			sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock2.sendto(str(i), server_add)			













if __name__ == '__main__':
	main()