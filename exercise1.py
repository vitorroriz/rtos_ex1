# Python 3.3.3 and 2.7.6
# python helloworld_python.py

from threading import Thread

i = 0

def increase():
	global i
	for j in range(1000000):
		i=i+1

def decrease():
	global i
    	for j in range(1000000):
		i=i-1

# Potentially useful thing:
#   In Python you "import" a global variable, instead of "export"ing it when you declare it
#   (This is probably an effort to make you feel bad about typing the word "global")
    

def main():
	global i

    	increaseThread = Thread(target = increase, args = (),)
	decreaseThread = Thread(target = decrease, args = (),)

    	increaseThread.start()
	decreaseThread.start()
    
    	increaseThread.join()
	decreaseThread.join()

    	print("Hello from main!")
	print("final value of i = "+str(i))

main()
