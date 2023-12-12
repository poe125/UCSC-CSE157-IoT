import asyncio 
from flask import Flask, request 
import requests
import logging 
from time import sleep

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
logEmer = logging.getLogger(f"(srv)")
logEmer.setLevel(level=logging.INFO)

IP = "169.233.161.85"
PORT = "5000"
DIRECTORY = "/emergency"
URL = "http://" + IP + ":" + PORT + DIRECTORY
MESSAGE = "EMERGENCY"


class flask_handler: 
    def __init__(self):
        """
        Start the flask server
        """
        self._app  = Flask(__name__)
        
    def send_post(self, URL, message):
        """
        Send a message to the sql server, this uses a predefined global URL defined in this file
        """
        #URL must be in the form of http://<IP address>:<port>/<directory>
        logEmer.debug(f"Flask: Preparing payload")
        payload = {'message': message}
        try: 
            logEmer.debug(f"Flask: trying post")
            response = requests.post(URL, json=payload)
            logEmer.debug(f"Flask: payload sent, is {payload}")
            logEmer.debug(f"Flask: response status code {response.status_code} type: {type(response.status_code)}")
            return response.status_code
        except Exception as error:
            logEmer.debug(f"Flask: error is {error}")

        
         

def send_emergency(message_handler):
    """
    Blocking function that tries to send the emergency packet to the SQL server and doesnt stop until it gets a reply back
    it was received. This uses HTTP protocol.
    """
    while True:
        logEmer.debug("EMERG: Preparing to send emergency packet")
        logEmer.debug(f"EMERG: URL is [{URL}]")
        status_code = message_handler.send_post(URL, MESSAGE)
        logEmer.debug(f"EMERG: attempt finished")

        # If we get a status code of 200, which is OK, the packet has been received 
        if status_code == 200:
            break
        sleep(1)
    
    return 