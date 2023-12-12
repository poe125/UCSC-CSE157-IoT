import sys
import socket
import selectors
import types
import logging
from time import sleep
from classes import i2c_controller
from classes import plotting_data
# Set up logging for server.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
slogger = logging.getLogger(f"(srv)")
slogger.setLevel(level=logging.DEBUG)
#Setting global defaults like all IP addresses, number of devices, and ports
#NOTE: because of the logic in ring_handler this version does not support more than 9 hosts
#NOTE: KEEP THE HOSTS LIST ORDERED FROM SMALLEST TO LARGEST ON LAST DIGIT OR DOESNT WORK
#NOTE: The code in ring_handler assumes the hosts last digit count up +1 
HOSTS = ["192.168.1.1","192.168.1.2","192.168.1.3"]
TOTAL_HOSTS = 3 
PORT = 1024
TOKEN_HEADER = "token"


class token_server:
    def __init__(self, host, port):
        """
        Initialization of the server class.
        """
        slogger.info(f"__init__: starting...")
        self.sel = selectors.DefaultSelector()
        self._host = host
        self._port = port
        self._no_packet = True
        self.i2c_cont = i2c_controller() # i2c controller
        self.counter = 1
        self._rtemp_list = []
        self._rhumd_list = []
        self._smois_list = []
        self._speed_list = []
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self._host, self._port))

        sock.listen()
        sock.setblocking(False)
        self.sel.register(sock, selectors.EVENT_READ, data=None)
        slogger.info(f"__init__: finished")

    
    def run_listener(self):
        """
        Starts listening for connections and starts the main event loop.
        """
        slogger.info("run_listener: starting...")
        try:
            slogger.debug(f"run_listener:self._no_packet = {self._no_packet}")
            while self._no_packet:
                slogger.debug(f"run_listener:self._no_packet = {self._no_packet}")
                try:
                    events = self.sel.select(timeout=5)
                    for key, mask in events:
                        if key.data is None:
                            self.accept_wrapper(key.fileobj)    
                        else:
                            packet = self.service_connection(key, mask)
                            slogger.debug(f"run_listener: packet is [{packet}]")
                            return packet
                except Exception as error:
                    slogger.error(f"run_listener: error is [{error}]")
                    break
        except KeyboardInterrupt:
            slogger.info("run: Caught keyboard interrupt, exiting...")
        finally:
            #self.sel.close()
            slogger.info("run_listener: finished")
    

    def set_packet_flag_F(self):
        """
        Set the packet received flag to false
        """
        self._no_packet = False


    def set_packet_flag_T(self):
        """
        Set the packet received flag to true
        """
        self._no_packet = True


    def accept_wrapper(self, sock):
        """
        Helper function for accepting and registering new connections
        """
        # Use sock.accept() to start a connection with another device
        conn, addr = sock.accept()
        slogger.debug(f"accept_wrapper: Accepted connection from {addr}.")
        
        # Disable blocking.
        conn.setblocking(False)
        
        # Create data object to monitor for read and write availability.
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        slogger.info(f"accept_wrapper: {data} | {conn} | {type(conn)}")
        
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        # Register connection with selector.
        self.sel.register(conn, events, data=data)


    def service_connection(self, key:selectors.SelectorKey, mask):
        """
        Services the existing connection and calls to unregister upon completion.
        """
        slogger.debug(f"service_connection: Servicing connection from: {key}, {mask}")
        sock = key.fileobj
        data = key.data
        # Check for reads or writes.
        """
        In this model, we are first waiting for new messages from the 
        client connections, so we are reading for data as it arrives 
        and until it stops arriving (end of message). We then switch 
        to writing to the client, sending a reply.
        """
        if mask & selectors.EVENT_READ:
            # At event, it should be ready for read.
            recv_data = sock.recv(1024)
            # As long as data comes in, append it.
            if recv_data:
                data.outb += recv_data
            # When data stops, close the connection.
            else:
                slogger.debug(f"Closing connection to {data.addr}")
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            # At event, it should be ready to write.
            if data.outb:
                """
                EVENT HANDLING CODE HERE:

                At this point, you have received a complete message from 
                one of the client connections and it is stored in 
                data.outb. You can now handle the message however you 
                like. It is good practice to make a new method to handle 
                the message, and then call it here.
                """
                slogger.info(f"service_connection: {data.outb}")
		        # Unregister and close socket.
                self.unregister_and_close(sock)

                #Return the parsed data packet
                return data.outb
        
        slogger.info(f"service_connection: NO DATA")


    def poll_data_to_string(self):
        """
        Creates a new Post Data and adds all the polling data to it
        """
        # Get the polling list (list with all the sensor reads)
        slogger.info(f"packet_post_encapsulator: running...")
        polling_list = self.poll_all()


        #Calculate the entire length of the post packet
        polling_length = len(polling_list)
        header_length = len("Post Data")
        num_commas = 5 # We poll 5 sensors so we need 5 commas as delimiter
        
        #Define the header msg of the packet
        post_packet = ""
        
        #compile all the sensor data into one packet
        for data in polling_list:
            slogger.debug(f"post_encap: pre-Data [{data}]")
            slogger.debug(f"    post_encap: pre-post-packet[{post_packet}]")
            data += ","
            post_packet += data

            slogger.debug(f"post_encap: post-post-packet[{post_packet}]")

        slogger.info("packet_post_encapsulator: finished")
        return post_packet
    
    def create_token_packet(self):
        """
        Create the token packet for the token ring network
        """ 
        #Define the three main portions of the first token packet
        slogger.info(f"create_token_packet: running...")
        header = TOKEN_HEADER
        footer = "seq:1" # token,seq:1
        deliminter = ","
        #Combine the token packet parts into one
        combined = header + deliminter + footer
        slogger.debug(f"create_token_packet: msg is [{combined}]")
        slogger.info(f"create_token_packet: finished")
        #Return the token packet
        return combined
    
    @classmethod
    def packet_splitter(cls, packet):
        """
        Split the packet into a list of lists
        """        
        #Create empty list to be used later
        split_list = []
        #Split the packet by the first deliminter
        item_split = packet.split(",")
        slogger.debug(f"packet_splitter: item_split [{item_split}]")
        #split the items from their numbers
        for item in item_split:
            temp = item.split(":")
            split_list.append(temp)
        slogger.debug(f"packet_splitter: split_list [{split_list}]")
        #Return the split list
        return split_list

    @classmethod
    def check_seq_number(cls, packet):
        """
        Helper function to check what the sequence number of the current packet is
        """
        slogger.info("check_seq_number: starting...")
        #If the packet is not empty
        slogger.debug(f"check_seq_number: packet is [{packet}]")
        if packet:
            #Set two empty strings to be used later
            seq_check = "" 
            seq_num = ""
            #Split the packet items from eachother
            packet = cls.packet_decoder(packet)
            split_list = cls.packet_splitter(packet)

            #Find the length of the list
            list_length = len(split_list)
            
            #Check the seq # which should be the last item in the list
            seq_item = split_list[list_length - 1] # Should look like [seq, <#>]
            slogger.debug(f"check_seq_number: seq_item [{seq_item}]") 
            if seq_item[0] == "seq":
                slogger.info("check_seq_number: finished")
                slogger.debug(f"check_seq_number: returned number is [{seq_item[1]}]")
                return seq_item[1]
        
        #If it is a empty packet or something else errors return None
        slogger.info("check_seq_number: finished")
        return None


    @classmethod
    def check_if_token_packet(cls, packet):
        """
        Checks if the packet header is the preset token header
        """
        slogger.info("check_if_token_packet: starting...")

        #Check that the packet is not none
        if packet:
            split_list = cls.packet_splitter()
            slogger.debug(f"check_if_token_packet: split_list is [{split_list}]")

            if split_list[0] == TOKEN_HEADER: 
                slogger.debug(f"check_if_token_packet: returning True")
                return True
        
        slogger.debug(f"check_if_token_packet: returning False")
        return False
    
    
    @classmethod
    def packet_decoder(cls, packet):
        """
        Decode a packet from binary to string type 
        """ 
        return packet.decode()

    def packet_adder(self, packet, seq_number):
        """
        Updates the polling data and sequence number in the packet
        """
        slogger.info(f"packet_adder: starting")
        #Find the position before seq number
        #Step 1 finding needed lengths
        seq_end = 6 #because there can be no more than 9 hosts len",seq:9" = 6 always
        #Decode the packet and find its length
        if (type(packet) ==bytes):
            decoded_packet = self.packet_decoder(packet)
        else:
            decoded_packet = packet
        slogger.debug(f"packet_adder: decoded packet is [{decoded_packet}]")
        packet_length = len(decoded_packet)
        cutoff_point = packet_length - seq_end - 1 # -1 to account for 0 in starting position
        
        #Modifying the packet
        #Get the polling data to be added to the packet
        poll_data = self.poll_data_to_string()
        #update the sequence to be +1
        new_seq_num = int(seq_number) + 1 #Seq number is always the last digit
        slogger.debug(f"packet_adder: new sequence number [{new_seq_num}]") 
        #Add the polling data to the packet
        result = decoded_packet[:cutoff_point] + "/" + poll_data + decoded_packet[cutoff_point:-1] + str(new_seq_num)
        slogger.debug(f"packet_adder: result is [{result}]")
        #Step 3 log and return
        slogger.debug(f"packet_adder: finished")
        return result

        # update the sequence number b'token....seq:5' 

    def packet_ring_handler(self, packet, seq_number):
        """
        React to what position we are in the seq number 
        """
        slogger.info(f"packet_ring_handler: starting...")
        slogger.debug(f"packet_ring_handler: packet is [{packet}]")
        
        plottool = plotting_data
        if int(seq_number) < int(TOTAL_HOSTS):
            slogger.debug(f"packet_ring_handler: seq_num {seq_number} less than")
            #If less than total_hosts we are not the plotting host only last one is
            host_last_digit = self._host[-1] #Grab our current hosts last IP digit
            last_host_ip = HOSTS[-1] #Grab the last host IP address 
            last_host_last_digit = last_host_ip[-1] #Grab the last host's IP address digit
            slogger.debug(f"packet_ring_handler: our digit {host_last_digit}")
            #Prepare the packet to be sent
            new_packet = packet
            if int(seq_number) != TOTAL_HOSTS: 
                new_packet = self.packet_adder(packet, seq_number)
            
            #Check which host we are sending to next
            if host_last_digit == last_host_last_digit:
                #Need to send cyclically at the first host 
                send_host = HOSTS[0] #Restart the send host cyclical check
                #add our polling data to the packet
                slogger.debug(f"packet_ring_handler: send host {send_host}")
            else: 
                # send cyclically to the next host in front of it which is +1 on the last digit
                last_digit = int(host_last_digit)
                send_host = HOSTS[last_digit]
                slogger.debug(f"packet_ring_handler: send host {send_host}")
            
            #Send the message to the next host after we checked which host
            self.send_msg(send_host, PORT, new_packet)

        else: 
            slogger.debug("packet_ring_handler: received _data")
            #add data to self._listname
            self.received_data(packet)
            self.get_i2c_data()
            plottool.plot_data(self.counter, self._rtemp_list, self._rhumd_list, self._smois_list, self._speed_list)
            self.counter += 1
            self.reset_data()

        slogger.info(f"packet_ring_handler: finished")
    
    def send_msg(self, send_host, send_port, msg):
        """
        Send a socket message to a specfied address and port
        """
        
        # Create a temporary socket and send a message
        slogger.info(f'Attempting msg send to {send_host} on port {send_port}, message is [{msg}]')
        #self.set_packet_flag_T()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Try to connect to the host
            packet_not_sent = True
            while packet_not_sent:
                slogger.debug(f"send_msg: packet not sent is {packet_not_sent}")
                try:
                    s.connect((send_host, send_port))
                    s.sendall(bytes(msg, 'utf-8'))
                    slogger.debug(f"send_msg: msg is [{msg}]")
                    slogger.info(f"send_msg: message sent!")
                    packet_not_sent = False
                    sleep(2)

                #If the connection doesnt work print the failure
                except OSError: 
                    slogger.error(f"send_msg: OSError!")
                except Exception as error:
                    slogger.error(f"send_msg: Error is [{error}]")


    def unregister_and_close(self, sock:socket.socket):
        """
        Unregisters and closes the connection, called at the end of service.
        """
        # Set the self._no_packet flag to false because a packet was sent
        slogger.info(f"unregister_and_close: running...")
        self.set_packet_flag_T()
        slogger.debug("unregister_and_close: Closing connection... No_data" + str(self._no_packet))
        # Unregister the connection.
        try:
            self.sel.unregister(sock)
        except Exception as e:
            slogger.error(f"unregister_and_close: Socket could not be unregistered:\n{e}")
        # Close the connection.
        try:
            sock.close()
        except OSError as e:
            slogger.error(f"unregister_and_close: Socket could not close:\n{e}")
        
        slogger.info("unregister_and_close: finished")
    
    def poll_all(self):
        """
        helper function to poll all 5 sensors and append their data to a 
        list and return it 
        """
        #Create a empty list to append the sensor results too
        slogger.info(f"poll_all: running...")
        poll_list = [] 
        #Poll all 5 of the sensors and append them each to the list
        poll_list.append(self.i2c_cont.getTemp())
        poll_list.append(self.i2c_cont.getHumd())
        poll_list.append(self.i2c_cont.getSoilTemp())   
        poll_list.append(self.i2c_cont.getSoilMoist())
        try:
            poll_list.append(self.i2c_cont.map_volt_value(self.i2c_cont.getADCVoltage()))
        except:
            poll_list.append("winds:ERR") # in the case init adc returns a None
            
        #Return the poll list
        slogger.info(f"poll_all: finished")
        return poll_list
    
    def get_i2c_data(self):
        """
        Poll your own raspberry Pi's data data and properly encasulate it
        """
        try:
            #Grab the current Pi's I2C data
            i2cdata = self.poll_all()
            #properly parse the data
            parsedData = self.packet_parser(i2cdata)
            #Take out the float data and put it in a instance variable
            self.result_to_list(parsedData)
        except Exception as error:
            #Create a empty return list when there is an error
            noData = []
            #Take out the "float data" and put it in a instance variable
            self.result_to_list(noData)
            slogger.info(f"get_i2c_data: i2c error:{error}")

    def result_to_list(self, data):
        """
        Inputs data from the list of lists to a single instance variable list for plotting data
        """
        slogger.debug(f"result_to_list: {data}")
        if len(data) != 0:
            self._rtemp_list.append(data[0][1])
            self._rhumd_list.append(data[1][1])
            self._smois_list.append(data[3][1])
            self._speed_list.append(data[4][1])
        else:
            #exception for ERR
            self._rtemp_list.append(0)
            self._rhumd_list.append(0)
            self._smois_list.append(0)
            self._speed_list.append(0)

    def reset_data(self):
        """
        Resets instance variable list that is used for plotting data
        """
        print("is in reset_data")
        self._rtemp_list = []
        self._rhumd_list = []
        self._smois_list = []
        self._speed_list = []

    #do this first
    def received_data(self, data):
         """
         split the data into two
         """
         str_data = data.decode()
         divide_by_packet = str_data.split("/")
         slogger.debug(f"received_data: divided_by_packet; {divide_by_packet}")
         del divide_by_packet[0]
         slogger.debug(f"received_data: divided_by_packet; {divide_by_packet}")
         first_data = divide_by_packet[0].split(",")
         slogger.debug(f"received_data: first_data; {first_data}")         
         second_data = divide_by_packet[1].split(",")
         slogger.debug(f"second_data: first_data; {second_data}")         
         
         print(first_data)
         del first_data[0]
         del first_data[-1]
         del first_data[-1]
         del second_data[0]
         del second_data[-1]
         del second_data[-1]

         data_result_split = []

         for combined in first_data:
            #Split the association string from the poll reading (should be a number)
            association, value = combined.split(":")
            #If the poll reading isnt a number we keep it as a string and add to temp_list
            try: 
                value = float(value)
                temp_list = [association, value]
            except ValueError:
                temp_list = [association, value]

            #Append to the main results list
            data_result_split.append(temp_list)
            #Clear the temp list
            self.result_to_list(data_result_split)
            temp_list = [] 
            data_result_split = []

         for combined in second_data:
            #Split the association string from the poll reading (should be a number)
            association, value = combined.split(":")
            #If the poll reading isnt a number we keep it as a string and add to temp_list
            try: 
                value = float(value)
                temp_list = [association, value]
            except ValueError:
                temp_list = [association, value]

            #Append to the main results list
            data_result_split.append(temp_list)
            self.result_to_list(data_result_split)

    #do this second
    def packet_parser(self, data):
        """
        Resets instance variable list that is used for plotting data
        """
        print("is in reset_data")
        self._rtemp_list = []
        self._rhumd_list = []
        self._smois_list = []
        self._speed_list = []