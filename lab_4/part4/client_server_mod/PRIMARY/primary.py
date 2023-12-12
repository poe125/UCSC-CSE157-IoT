"""
This file runs the primary server file that collects data from other IoT devices
"""
from sink_server import Sink_server
import logging
from time import sleep
from web_app import mySQL
from classes import file_manager
from emergency_handler import send_emergency, flask_handler
from wildfire_calc import calc_wildfire_percent_risk, calc_wildfire_risk_stage
HOST = "192.168.1.1" #Current device IP address 
HOSTS = ["192.168.1.2", "192.168.1.3"] #Other IoT device IP addresses
PORT = 1024 #All IP addresses use the same port
MAX_WILDFIRE_CHANCE = 50 


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
logMain = logging.getLogger(f"(srv)")
logMain.setLevel(level=logging.DEBUG)
def check_emergency(percent): 
	"""
	Check if we need to send the emergency packet by calculating if we are 
	half or above the max wildfire chance
	"""
	
	if percent >= (MAX_WILDFIRE_CHANCE * (1/2)):
		return True
	return False

def reset_list(list):
	logMain.debug(f"PRIMARY: reset_list: list is {list}")
	if list:
		for i in enumerate(list): 
			list[i[0]] = 0
	return list 

def append_wildfire_and_send_sql(data_packet, sql, table): 
	if(data_packet != None):
			risk_percent = calc_wildfire_percent_risk(data_packet[0], data_packet[1], data_packet[2])
			risk_stage   = calc_wildfire_risk_stage(risk_percent)
			data_packet.append(risk_stage)
			data_packet.append(risk_percent)
			logMain.debug(f"PRIMARY: calling insert_update, table is {table}") 
			logMain.debug(f"	PRIMARY: packet is {data_packet}")
			sql.insert_update(table, data_packet)
			return risk_percent
	else: 
		return 0

def main(): 
	noData = []

	#start our sink server 
	mySink = Sink_server(HOST, PORT)
	#Define our request data message
	request_data_msg = "Requesting Data" 

	# init file_manager for data reading purposes
	manager = file_manager()
	emergency_not_sent = True
	msg_handler = flask_handler()
	sql = mySQL()
	tables = ["sensor_readings1", "sensor_readings2", "sensor_readings3"]
	# Create empty lists to hold the sensor and packet header data
	data_packet_1 = [0,0,0,0,0,0] # 5 items when polling from another device
	data_packet_2 = [0,0,0,0,0,0] # 5 items when polling from another device 
	data_packet_3 = [0,0,0,0,0] # 4 items when polling from your own device
	risk_percents = [0,0,0] # 3 risk percents because 3 devices we poll data from

	while True: 
		#Send data request to host 1
		msg_sent = mySink.send_msg(HOSTS[0], PORT, request_data_msg)
		logMain.debug(f"PRIMARY:main: msg_sent {msg_sent} to host 1")
		#Wait and listen for host 1 to send back a data packet
		data_packet_1 = reset_list(data_packet_1) 
		if msg_sent == True: 
			data_packet_1 = mySink.run_listener()
			logMain.debug(f"PRIMARY:main: data #1 is [{data_packet_1}]")
			if data_packet_1:
				data_packet_1.pop(0) # Remove the network header from the list
		else: 
			logMain.debug(f"PRIMARY:main: no message sent #1")
			logMain.debug(f"PRIMARY:main: data #2 is after pop [{data_packet_1}]")
		mySink.set_packet_flag_T()
		sleep(2)
		
		#Send data request to host 2_
		msg_sent = mySink.send_msg(HOSTS[1], PORT, request_data_msg)
		logMain.debug(f"PRIMARY:main: msg_sent {msg_sent} to host 2")
		#Wait and listen for host 2 to send back a data packet
		data_packet_2 = reset_list(data_packet_2)
		if msg_sent == True: 
			data_packet_2 = mySink.run_listener()
			logMain.debug(f"PRIMARY:main: data #2 is [{data_packet_2}]")
			if data_packet_2:
				data_packet_2.pop(0) # Remove the network header from list
				logMain.debug(f"PRIMARY:main: data #2 is after pop [{data_packet_2}]")
		else: 
			logMain.debug(f"PRIMARY:main: no message sent #2")
		mySink.set_packet_flag_T()
		sleep(2)
		
		#Grab our own devices sensor data
		data_packet_3 = reset_list(data_packet_3)
		# Grab our own Pis sensor data
		data_packet_3 = manager.read_line() # read the line we are using the mimic sensor data
		data_packet_3 = data_packet_3.split(",") # Split it into a list
		logMain.debug(f"PRIMARY:main: data_packet_3 to wildfire is: [{data_packet_3}]")

		# Calculate wildfire numbers, append them, and send to sql database
		risk_percents[0] = append_wildfire_and_send_sql(data_packet_1, sql, tables[0]) # send [1:] removes header string
		risk_percents[1] = append_wildfire_and_send_sql(data_packet_2, sql, tables[1])
		risk_percents[2] = append_wildfire_and_send_sql(data_packet_3, sql, tables[2])
				
		# Checking if any data breaches the emergency threshold
		if emergency_not_sent:
			for percent in risk_percents:
				if check_emergency(percent): 
					# SEND EMERGENCY RIGHT HERE!!!!!!!!!!
					logMain.debug(f"PRIMARY:main: EMERGENCY ERMGNERNCY SDKJSDKJASOIASDJOI")
					emergency_not_sent = False
					send_emergency(msg_handler)
					break
					
		

if __name__ == '__main__': 
	main()
