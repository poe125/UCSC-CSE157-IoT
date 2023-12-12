import logging
import selectors
import socket
import types

# Set up logging for server.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
slogger = logging.getLogger(f"(srv)")
slogger.setLevel(level=logging.DEBUG)

class Sink_server:
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
            slogger.debug(f"run_listener:self._no_packet = {self._no_packet}")
            while self._no_packet:
                slogger.debug(f"run_listener:self._no_packet = {self._no_packet}")
                try:
                    events = self.sel.select(timeout=5)
                    for key, mask in events:
                        if key.data is None:
                            self.accept_wrapper(key.fileobj)    
                        else:
                            return self.service_connection(key, mask)
                except Exception as error:
                    slogger.error(f"run_listener: error is [{error}]")
                    break
        except KeyboardInterrupt:
            slogger.info("run: Caught keyboard interrupt, exiting...")
        finally:
            #self.sel.close()
            slogger.info("run_listener: finished")

    def accept_wrapper(self, sock):
        """
        Accepts and registers new connections.
        """
        conn, addr = sock.accept()
        slogger.debug(f"accept_wrapper: Accepted connection from {addr}.")

        conn.setblocking(False)

        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        #register the connection with selector
        self.sel.register(conn, events, data = data)

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
                slogger.info(f"handling data: {data.outb}")
                #add twice. list[0],list[1]
                parsed_data = self.packet_parser(data.outb)

                slogger.debug(f"handling_data: parsed_data is [{parsed_data}]")
                
		        # Unregister and close socket.
                self.unregister_and_close(sock)

                #Return the parsed data packet
                return parsed_data
            

    def unregister_and_close(self, sock: socket.socket):
        """
        Unregisters and closes the connection, called at the end of service.
        """
        slogger.info(f"unregister_and_close: starting...")
        self.set_packet_flag()
        slogger.debug("unregister_and_close: Closing connection...")
        try:
            self.sel.unregister(sock)
        except Exception as e:
            slogger.error(f"unregister_and_close: Socket could not be unregistered:\n{e}")

        try:
            sock.close()
        except OSError as e:
            slogger.error(f"unregister_and_close: Socket could not close:\n{e}")

        slogger.info(f"unreigster_and_close: finished")
            

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
        Send a socket message to a specified address and port
        """
        # Create a temporary socket and send a message
        slogger.info(f'send_msg: Attempting msg send to {send_host} on port {send_port}, message is [{msg}]')
        self.set_packet_flag_T()
        try:
            sock = socket.create_connection((send_host, send_port), timeout=2)
            byte_msg = bytes(msg, 'utf-8')
            sock.sendall(byte_msg)
            slogger.debug(f"send_msg: msg is [{byte_msg}]")
            slogger.info(f"send_msg: message sent!")
            return True
        except Exception as error:
            slogger.error(f"send_msg: Error is [{error}]")
            return False
   

    def packet_parser(self, data):
        """
        Parse a "Post Data" packet and sort the sensor polling data from it
        """
        #Decode and split the data 
        slogger.info(f"packet_parser: starting... {data}")
        if(type(data) == bytes):
            str_data = data.decode()
            str_data = str_data[:-1] #removing extra comma 

        data_results = str_data.split(",")
        slogger.debug(f"packet_parser: decode is [{str_data}]")
        slogger.debug(f"packet_parser: data_results is [{data_results}]")

        return data_results