import sys
import socket
import selectors
import types
import logging
from classes import i2c_controller


# Set up logging for server.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
slogger = logging.getLogger(f"(srv)")
slogger.setLevel(level=logging.DEBUG)


class Sensor_server:
    def __init__(self, host, port):
        """
        Our server will use a host (its own address) and port to listen 
        for connections. It must also use a selector to monitor for events 
        on the socket.
        """
        slogger.info("__init__: Initializing server...")
        # Set up selector.
        self.sel = selectors.DefaultSelector()
        # Set host and port.
        self._host = host
        self._port = port
        self._no_packet = True
        self.i2c_cont = i2c_controller() # i2c controller
        
        
        """
        Setting up the actual server using socket library
        """
        # Mandatory start for setting server socket connections
        slogger.info("__init__: Starting server...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Binding actual host and port.
        slogger.info("__init__: \tSetting socket...")
        sock.bind((self._host, self._port))
        
        """
        The socket is all set up and ready to listen for connections.
        """
        sock.listen()
        slogger.info(f"__init__: Listening from port {self._port}.")
        sock.setblocking(False) #dont block the program while we wait on callee-"not busy waiting"
        slogger.info("__init__: Server initialized.")
        
        """
        As mentioned before, we use selectors to monitor for new events 
        by monitoring the socket for changes.
        """
        # Register the socket to be monitored.
        self.sel.register(sock, selectors.EVENT_READ, data=None)
        slogger.info("__init__: Monitoring set __init__ complete.")

    
    def set_packet_flag(self):
        """
        Set the packet received flag to false
        """
        self._no_packet = False

    def set_packet_flag_T(self):
        """
        Set the packet received flag to true
        """
        self._no_packet = True

    def send_msg(self, send_host, send_port, msg):
        """
        Send a socket message to a specfied address and port
        """
        
        # Create a temporary socket and send a message
        slogger.info(f'Attempting msg send to {send_host} on port {send_port}, message is [{msg}]')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Try to connect to the host
            try:
                s.connect((send_host, send_port))
                byte_msg = bytes(msg, 'utf-8')
                s.sendall(byte_msg)
                slogger.info(f"send_msg: message sent!")
            
            #If the connection doesnt work print the failure
            except Exception as error:
                slogger.error(f"send_msg: Error is [{error}]")


    
    # Run the packet listener function        
    def run_listener(self):
        """
        Starts listening for connections and starts the main event loop. 
        This method works as the main "run" function for the server, 
        kicking off the other methods of this service.
        """
        
        # Event loop.
        slogger.info(f"run_listener: starting...")
        slogger.debug(f"run_listener: self._no_packet is [{self._no_packet}]")

        while self._no_packet:
            slogger.debug(f"run_listener: while loop self._no_packet is {self._no_packet}")
            try:
                events = self.sel.select(timeout=2)


                for key, mask in events:
                    if key.data is None:
                        """
                        Here, we accept and register new connections.
                        """
                        slogger.debug(f"entering accept_wrapper")
                        self.accept_wrapper(key.fileobj) 
                    else:
                        """
                        Here, we service existing connections. This is 
                        the method where we will include our event-handling
                        code.
                        """
                        slogger.debug(f"entering service_connection")
                        service_return = self.service_connection(key, mask)
                        slogger.debug(f"run_listener: service_return is [{service_return}]")
                        return service_return
            except Exception as error: 
                slogger.error(f"run_listener: error is [{error}]")
                break

        slogger.info(f"run_listener: finished")
    # Helper functions for accepting wrappers, servicing connections, and closing.
    def accept_wrapper(self, sock):
        """
        Accepts and registers new connections.
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
        slogger.info(f"service_connection: Servicing connection from: {key}, {mask}")
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
                slogger.debug(f"service_connection: EVENT_WRITE data is: {data.outb}")

                

                # Unregister and close socket.
                self.unregister_and_close(sock)
                # React to the packet
                handler_return = self.packet_handler(data.outb)
                slogger.debug(f"service_connection: packet_handler return [{handler_return}]")
                return handler_return
                
    def packet_handler(self, binary_packet):
        """
        Handles packet depending on what is in the header (begining of the packet)"
        """
        #Check what the packet is asking for
        slogger.info(f"packet_handler: binary_packet is {binary_packet}")
        #If the binary_packet is not none decode the packet to a string
        if binary_packet:
            packet = binary_packet.decode()
            slogger.debug(f"packet_handler: packet is {packet}")
            #If the packet is requesting data then send the post msg back
            if packet == "Requesting Data":
                return self.packet_post_encapsulator()
            else: 
            #Else return a empty packet because we have no other events 
                return None
        else: 
            slogger.debug(f"packet_handler: packet is None")
    def packet_post_encapsulator(self):
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
        post_packet = "Post Data,"
        
        #compile all the sensor data into one packet
        for data in polling_list:
            slogger.debug(f"post_encap: pre-Data [{data}]")
            slogger.debug(f"    post_encap: pre-post-packet[{post_packet}]")
            data += ","
            post_packet += data

            slogger.debug(f"post_encap: post-post-packet[{post_packet}]")

        slogger.info("packet_post_encapsulator: finished")
        return post_packet


    def poll_all(self):
        """
        Poll all 5 sensors and append their data to a list and return 
        """
        #Create a empty list to append the sensor results too
        slogger.info(f"poll_all: running...")
        poll_list = [] 

        #Poll all 5 of the sensors and append them each to the list
        poll_list.append(self.i2c_cont.getTemp())
        poll_list.append(self.i2c_cont.getHumd())
        poll_list.append(self.i2c_cont.getSoilTemp())
        poll_list.append(self.i2c_cont.getSoilMoist())
        poll_list.append(self.i2c_cont.map_volt_value(self.i2c_cont.getADCVoltage()))
        
        #Return the poll list
        slogger.info("poll_all: finished")
        return poll_list

    def unregister_and_close(self, sock:socket.socket):
        """
        Unregisters and closes the connection, called at the end of service.
        """
        # Set the self._no_packet flag to false because a packet was sent
        slogger.info(f"unregister_and_close: running...")
        self.set_packet_flag()
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
"""
Using this simple server class, you should be able to create a server 
that can accept multiple socket connections from multiple clients and 
handle incoming messages.
"""



