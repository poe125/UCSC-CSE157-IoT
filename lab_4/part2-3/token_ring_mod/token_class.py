import sys
import socket
import selectors
import types
import logging
from time import sleep
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
ACK_MSG = "ACK"


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
            slogger.debug(f"run_listener: self._no_packet = {self._no_packet}")
            while self._no_packet:
                slogger.debug(f"run_listener: self._no_packet = {self._no_packet}")
                try:
                    events = self.sel.select(timeout=5)
                    for key, mask in events:
                        if key.data is None: 
                            """
                            # If key.data is none then its from a listening socket
                            # so we need to accept and register the connection
                            """
                            self.accept_wrapper(key.fileobj)    
                        else:
                            """
                            If key data != none then its already a accepted socket
                            which we service the connection
                            """ 
                            packet = self.service_connection(key, mask)
                            slogger.debug(f"run_listener: packet is [{packet}]")
                            if not packet: 
                                    slogger.debug(f"run_listener: packet is [{packet}], re-running listener")
                                    continue
                            self.set_packet_flag_T()
                            slogger.debug(f"run_listener: packet self._no_packet: {self._no_packet} | packet [{packet}]")
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
        Helper function for accepting and registering new connections on a socket
        """
        # Use sock.accept() to start a connection with another device
        conn, addr = sock.accept()
        slogger.debug(f"accept_wrapper: Accepted connection from {addr}.")
        
        # Disable blocking, so we can accept multiple sockets if needed
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
        #
        sock = key.fileobj
        data = key.data
        # Check if the socket is ready for reading or writiting
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
                Once we finished receiving the packet we send back a ACK
                and return the  
                """
                slogger.info(f"service_connection: WRITE, dats is: {data.outb}")
		        #Send a ACK message back to the sender
                sock.sendall(bytes(ACK_MSG, 'utf-8'))
                # Unregister and close socket.
                self.unregister_and_close(sock)
                #Return the data packet
                return data.outb
        
        slogger.info(f"service_connection: NO DATA")


    def create_token_packet(self):
        """
        Create the token packet for the token ring network
        """ 
        #Define the three main portions of the first token packet
        slogger.info(f"create_token_packet: running...")
        header = TOKEN_HEADER
        footer = "seq:0" # token,seq:1
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
        #split the items from their numbers by the second deliminter
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
    def check_if_token(cls, packet):
        """
        Checks if the packet header is the preset token header
        """
        slogger.debug("check_if_token_packet: starting...")

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
    def check_if_ACK(cls, packet):
        """
        Checks if the packet header is the ACK message
        """
        slogger.debug("check_if_ACK: starting...")
        slogger.debug(f"check_if_ACK: packet: {packet}")

        #Check that the packet is not none
        if packet:
            #Check if the packet is is the ACK message
            if packet == ACK_MSG:
                slogger.debug(f"check_if_ACK: returning True")
                return True
        
        #If the packet fails both checks above its not the ACK message
        slogger.debug(f"check_if_ACK: returning False")
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
        seq_end = 6 #because there can be no more than 9 hosts len",seq:9" = 6 characters
        #Decode the packet and find its length
        if (type(packet) == bytes):
            decoded_packet = self.packet_decoder(packet)
        else:
            decoded_packet = packet
        slogger.debug(f"packet_adder: decoded packet is [{decoded_packet}]")
        packet_length = len(decoded_packet)
        cutoff_point = packet_length - seq_end
        
        #Modifying the packet
        #Get the polling data to be added to the packet
        poll_data = "Data"
        #update the sequence to be +1
        new_seq_num = int(seq_number) + 1 #Seq number is always the last digit
        slogger.debug(f"packet_adder: new sequence number [{new_seq_num}]") 
        #Add the polling data to the packet
        result = decoded_packet[:cutoff_point] + "/" + poll_data + decoded_packet[cutoff_point:-1] + str(new_seq_num)
        slogger.debug(f"packet_adder: result is [{result}]")
        #Step 3 log and return
        slogger.debug(f"packet_adder: finished")
        return result

    def packet_ring_handler(self, packet, seq_number):
        """
        React to what position we are in the seq number when we receive the token based on IP addresses
        """
        slogger.info(f"packet_ring_handler: starting...")
        slogger.debug(f"packet_ring_handler: packet is [{packet}]")

        #Check if the packet is the data packet or a ACK 
        if self.check_if_ACK(packet):
            # If the ACK packet then our message was successfully sent ......
            pass #FIX ME: add action for when is ACK
        else: 
            # If its not the ACK packet then the message is the data packet we need to check the seq #
            self.seq_handler(packet, seq_number)
        
    def find_next_host(self): 
        #Grab data on our device IP and the last (highest digit) device IP 
        host_last_digit = self._host[-1] #Grab our current devices last IP digit
        last_host_ip = HOSTS[-1] #Grab the last device IP address 
        last_host_last_digit = last_host_ip[-1] #Grab the last host's IP address digit
        slogger.debug(f"seq_handler: our digit {host_last_digit}")
        
        #Figure out what device we are sending to next 
        if host_last_digit == last_host_last_digit:
            #Need to send cyclically at the first device if we are the last IP device 
            send_host = HOSTS[0] #Restart the send host cyclical check
            #add our polling data to the packet
            slogger.debug(f"seq_handler: send host {send_host}")
        else: 
            # send cyclically to the next device which is +1 of our IP 
            # Or just our IP last digit since python lists start at 0
            last_digit = int(host_last_digit)
            send_host = HOSTS[last_digit]
            slogger.debug(f"seq_handler: send host {send_host}") 
        
        return send_host
    
    def seq_handler(self, packet, seq_number):
        """
        Handles token ring packets and their sequence number
        """

        # Figure out what device in the IP list we are sending to
        send_device = self.find_next_host()

        if int(seq_number) < int(TOTAL_HOSTS):
            # If our seq # is less than total devices, we are not the internet connected host
            # and we need to append our data to the packet 
            slogger.debug(f"seq_handler: seq_num {seq_number} less than")
              
            # Append our device data to the packet and update the sequence number
            new_packet = self.packet_adder(packet, seq_number)
            
            #Send the message to the next host after we checked which host
            self.send_msg(send_device, PORT, new_packet)

        else: 
            """
            If our seq # is equal to total devices, we are the internet connected host
            and we need to append our data and send the packet to the database 
            and create a new packet to send throughout the token ring
            """
            slogger.debug("seq_handler: Handling as original token bearer")
            slogger.info("seq_handler: preparing to send to database")
            # FIX ME: Add code here to send packet to database 
            slogger.debug("seq_handler: Starting new token packet")
            token_packet = self.create_token_packet()
            new_packet = self.packet_adder(token_packet, 0)
            slogger.debug("seq_handler: sending packet to next host")
            self.send_msg(send_device, PORT, new_packet)
            slogger.info("seq_handler: info send to database and new token sent")



        slogger.info(f"seq_handler: finished")

    def send_msg(self, send_host, send_port, msg):
        """
        Send a socket message to a specfied address and port
        """
        
        # Create a temporary socket and send a message
        slogger.info(f'Attempting msg send to {send_host} on port {send_port}, message is [{msg}]')
        packet_not_sent = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while packet_not_sent:
            # Try to connect to the host
                try:
                    s.connect((send_host, send_port))
                    s.sendall(bytes(msg, 'utf-8'))
                    slogger.debug(f"send_msg: msg is [{msg}]")
                    
                    ACK_msg = s.recv(1024)
                    slogger.debug(f"send_msg: ACK is: {ACK_msg}")
                    #Check if we recieved the ACK, otherwise re-transmit recursively
                    if not self.check_if_ACK(self.packet_decoder(ACK_msg)):
                        #self.send_msg(send_host, send_port, msg)
                        sleep(0.1)
                        pass
                #If the connection doesnt work print the failure
                except Exception as error:
                    slogger.error(f"send_msg: Error is [{error}]")
                    #self.send_msg(send_host, send_port, msg)
                    sleep(0.1)
                    pass
                slogger.info(f"send_msg: message sent!")
                packet_not_sent = False

    def unregister_and_close(self, sock:socket.socket):
        """
        Unregisters and closes the connection, called at the end of service.
        """

        # Set the self._no_packet flag to false because a packet was sent
        self.set_packet_flag_F()
        slogger.info(f"unregister_and_close: running...")
        slogger.debug("unregister_and_close: Closing connection... No_data: " + str(self._no_packet))
        # Unregister the connection.
        try:
            self.sel.unregister(sock)
        except Exception as e:
            slogger.error(f"unregister_and_close: Socket could not be unregistered:\n{e}")
            self.unregister_and_close(sock)
        # Close the connection.
        try:
            sock.close()
        except OSError as e:
            slogger.error(f"unregister_and_close: Socket could not close:\n{e}")
            self.unregister_and_close(sock)
        
        slogger.info("unregister_and_close: finished")
