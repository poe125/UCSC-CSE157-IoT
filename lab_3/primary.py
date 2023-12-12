"""
This file runs the primary server file that collects data from other IoT devices
"""
from sink_server import Sink_server
import logging
import threading
from time import sleep
HOST = "192.168.1.1" #Current device IP address
HOSTS = ["192.168.1.2", "192.168.1.3"] #Other IoT device IP addresses
PORT = 1024 #All IP addresses use the same port


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
logMain = logging.getLogger(f"(srv)")
logMain.setLevel(level=logging.INFO)

def main():
	loop_number = 0

	#start our sink server
	mySink = Sink_server(HOST, PORT)
	#Define our request data message
	request_data_msg = "Requesting Data"
	while True:
		#Send data request to host 1

		loop_number += 1

		msg_sent = mySink.send_msg(HOSTS[0], PORT, request_data_msg)
		logMain.debug(f"PRIMARY:main: msg_sent {msg_sent} to host 1")

		#Wait and listen for host 1 to send back a data packet
		if msg_sent == True:
			data_packet_1 = mySink.run_listener()
			logMain.debug(f"PRIMARY:main: data #1 is [data_packet_1]")
		else:
			logMain.debug(f"PRIMARY:main: no message sent #1")
		sleep(2)

		#Send data request to host 2
		if msg_sent == True:
			data_packet_2 = mySink.run_listener()
			logMain.debug(f"PRIMARY:main: data #2 is [data_packet_2]")
		else:
			logMain.debug(f"PRIMARY:main: no message sent #2")
		sleep(2)

		#Read I2C from own pi and append it to the data list

		#run this into the polling-plot-loop_number.png
		mySink.plot_data(loop_number)
		mySink.reset_data

		#ADD LATER: Processing data_packet_1 and data_packet_2

if __name__ == '__main__':
	main()
