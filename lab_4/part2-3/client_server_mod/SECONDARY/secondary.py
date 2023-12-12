# Wait to receive string "Requesting Data"
# Reply with sensor measurements

from sensor_server import Sensor_server
from os import system
import logging
HOST = "192.168.1.3"
PORT = 1024
EXT_HOST = "192.168.1.1"

logMain = logging.getLogger(f"(srv)")
logMain.setLevel(level=logging.DEBUG)

def main():
    """
    Main() is the main runner of our program that defines how our sensor server acts
    """
    # Create the sensor_server object
    mySensor = Sensor_server(HOST, PORT)
    try:
        # Start the main event loop
        while True:
            # Wait and listen for a packet
            return_packet = mySensor.run_listener()
            logMain.debug(f"SECONDARY:main: return packet [{return_packet}]")
            # React to the packet
            # If the packet is not none, then we need to poll our sensors and send the data to the sink server 
            if return_packet != None: 
                # Send the response packet back
                mySensor.send_msg(EXT_HOST, PORT, return_packet)
            else: 
            # If our packet is none then an error occured and we need to set _no_packet to true, then we go back to the listener     
                mySensor.set_packet_flag_T()
    except KeyboardInterrupt:
        return

if __name__ == '__main__':
    main()
