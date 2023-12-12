"""
This file runs the primary server file that collects data from other IoT devices
"""
from sink_server import Sink_server
import logging
from time import sleep
from web_app import mySQL
from classes import file_manager
HOST = "192.168.1.1" #Current device IP address 
HOSTS = ["192.168.1.2", "192.168.1.3"] #Other IoT device IP addresses
PORT = 1024 #All IP addresses use the same port


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
logMain = logging.getLogger(f"(srv)")
logMain.setLevel(level=logging.DEBUG)

def send_sql(data_packet, sql, table): 
	if(data_packet != None):
			logMain.debug(f"PRIMARY: calling insert_update, table is {table}") 
			logMain.debug(f"	PRIMARY: packet is {data_packet}")
			sql.insert_update(table, data_packet)
			return 
	else: 
		return
	

def main(): 
	noData = []

	#start our sink server 
	mySink = Sink_server(HOST, PORT)
	#Define our request data message
	request_data_msg = "Requesting Data" 

	# init file_manager for data reading purposes
	manager = file_manager()
	sql = mySQL()
	tables = ["sensor_readings1", "sensor_readings2", "sensor_readings3"]
	data_packet_1 = [0,0,0,0,0,0] # 5 items when polling from another device
	data_packet_2 = [0,0,0,0,0,0] # 5 items when polling from another device 
	data_packet_3 = [0,0,0,0,0] # 4 items when polling from your own device
	

	while True: 
		#Send data request to host 1

		msg_sent = mySink.send_msg(HOSTS[0], PORT, request_data_msg)
		logMain.debug(f"PRIMARY:main: msg_sent {msg_sent} to host 1")

		#Wait and listen for host 1 to send back a data packet
		if msg_sent == True: 
			data_packet_1 = mySink.run_listener()
			if data_packet_1:
				data_packet_2.pop(0)
			logMain.debug(f"PRIMARY:main: data #1 is [{data_packet_1}]")
		else: 
			logMain.debug(f"PRIMARY:main: no message sent #1")
		mySink.set_packet_flag_T()
		sleep(2)
		
		#Send data request to host 2
		msg_sent = mySink.send_msg(HOSTS[1], PORT, request_data_msg)
		logMain.debug(f"PRIMARY:main: msg_sent {msg_sent} to host 2")
		
		if msg_sent == True: 
			data_packet_2 = mySink.run_listener()
			if data_packet_2:
				data_packet_2.pop(0)
			logMain.debug(f"PRIMARY:main: data #2 is [{data_packet_2}]")
		else: 
			logMain.debug(f"PRIMARY:main: no message sent #2")
		mySink.set_packet_flag_T()
		sleep(2)

		#Read I2C from own pi and append it to the data list
		logMain.debug(f"I2C_data")
		#adding i2c data to the list (ex. rtemp)
		# FIX ME: ADD GET I2C DATA HERE FROM 
		data_packet_3 = manager.read_line() # read the line
		data_packet_3 = data_packet_3.split(",")

		# ADD HERE, APPEND THE THREE PI DATA INTO ONE, THEN SEND IT.
		##run this into the polling-plot-loop_number.png
		logMain.info("Sending data to database") 

		

		# send pi1 data
		send_sql( data_packet_1, sql, tables[0])
		# send pi2 send_sqldata
		send_sql(data_packet_2, sql, tables[1])
		# send pi3 data
		send_sql(data_packet_3, sql, tables[2])
                
		"""
		for i, table_name in enumerate(tables):
		logMain.debug(f"seq_handler: inputting into table {table_name} with {list_data[1:]}")
		sql.insert_update(table_name, list_data[1:])
        """


if __name__ == '__main__': 
	main()
