from classes import i2c_controller
from classes import plotting_data
from time import sleep
import logging
from token_class import token_server

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
logMain = logging.getLogger(f"(srv)")
logMain.setLevel(level=logging.DEBUG)


#Setting global defaults current Pi's ip address 
HOST_IP = "192.168.1.1"
PORT = 1024 


def user_question():
    """
    Ask the user if they start with the token or not
    """
    #Ask the user if the are the first token server
    print("Are you the token bearer? Y or y for Yes | N or n for No")
	#Wait for user input
    user_input = input()
	#Turn the user input lowercase
    user_input = user_input.lower()
	#React to the user input
    if user_input == "y":
        return True
    else: 
        return False


def main(): 
    """
    Run the main event of our token server
    """
    #Ask at the start of the token server if the current one starts with a token
    #Note: Only one user should start with the token, logic is not implemented for 
    #multiple tokens
    user_answer = user_question()
    #Create the token server instance
    my_server = token_server(HOST_IP, PORT)
    #If the current Pi is the first token server then start with sending a message
    if user_answer == True: 
        #Create the first token packet
        token_packet = my_server.create_token_packet()
        #Send the token_packet to the next host using the packet_ring_handler function
        my_server.packet_ring_handler(token_packet, 1)
        
    #If the current Pi isnt the first token or sent the token already then wait and listen 
    #for the token
    while True: 
        packet = my_server.run_listener() #Wait and listen for the encoded packet
        seq_num = my_server.check_seq_number(packet)
        my_server.packet_ring_handler(packet, seq_num)
        #start listener
        #once listener ends react to add and send token or plot and reset token
          


if __name__ == '__main__': 
=======
from classes import i2c_controller
from classes import plotting_data
from time import sleep
import logging
from token_class import token_server

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
logMain = logging.getLogger(f"(srv)")
logMain.setLevel(level=logging.DEBUG)


#Setting global defaults current Pi's ip address 
HOST_IP = "192.168.1.1"
PORT = 1024 


def user_question():
    """
    Ask the user if they start with the token or not
    """
    #Ask the user if the are the first token server
    print("Are you the token bearer? Y or y for Yes | N or n for No")
	#Wait for user input
    user_input = input()
	#Turn the user input lowercase
    user_input = user_input.lower()
	#React to the user input
    if user_input == "y":
        return True
    else: 
        return False


def main(): 
    """
    Run the main event of our token server
    """
    #Ask at the start of the token server if the current one starts with a token
    #Note: Only one user should start with the token, logic is not implemented for 
    #multiple tokens
    user_answer = user_question()
    #Create the token server instance
    my_server = token_server(HOST_IP, PORT)
    #If the current Pi is the first token server then start with sending a message
    if user_answer == True: 
        #Create the first token packet
        token_packet = my_server.create_token_packet()
        #Send the token_packet to the next host using the packet_ring_handler function
        my_server.packet_ring_handler(token_packet, 1)
        
    #If the current Pi isnt the first token or sent the token already then wait and listen 
    #for the token
    while True: 
        packet = my_server.run_listener() #Wait and listen for the encoded packet
        seq_num = my_server.check_seq_number(packet)
        my_server.packet_ring_handler(packet, seq_num)
        #start listener
        #once listener ends react to add and send token or plot and reset token
          


if __name__ == '__main__': 
    main()