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
    mySensor = Sensor_server(HOST, PORT)
    try:
        while True:
            #Listen for a packet
            return_packet = mySensor.run_listener()
            logMain.debug(f"SECONDARY:main: return packet [{return_packet}]")
            #React to the packet
            if return_packet != None: 
                # Send the response packet back
                mySensor.send_msg(EXT_HOST, PORT, return_packet)
            else: 
                mySensor.set_packet_flag_T()
    except KeyboardInterrupt:
        return

if __name__ == '__main__':
    main()
