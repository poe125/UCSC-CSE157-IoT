#General libraries
import os
import logging

# Set up logging for server.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
slogger = logging.getLogger(f"(srv)")
slogger.setLevel(level=logging.DEBUG)

#Constants for mapping the ADC values 
SENSOR_MIN = 0.41
SENSOR_MAX = 0.76
VALUE_MIN  = 0
VALUE_MAX  = 32.4
#Constants for files
FILE_NAME = "sensor_data.txt"
FILE_LOCATION = "sensor_data/"

class file_manager: 
    def __init__(self): 
        # Start our first read line at 0 for a file 
        self._current_line = 1 
        # Save the path our file is in 
        save_path = os.path.expanduser(FILE_LOCATION)
        self._save_path = os.path.join(save_path, FILE_NAME)

    def update_curr_line(self): 
        """
        This functions updates the current line we want by 1 
        """
        self._current_line = self._current_line + 1 

    def reset_curr_line(self): 
        self._current_line = 1 

    
    def read_line(self): 
        # We always read from the start of the file
        count = 0 
        
        # Then we set our read object (file)
        while True:
            with open(self._save_path, "r") as file: 
                # While we have not found the line we want, read the next one
                while True: 
                    count += 1 

                    # If we run into a EOF error or something else we start reading at the begining again
                    try:
                        line = file.readline()
                        line = line.rstrip()
                    except Exception as Error:
                        slogger.error(f"classes.py:read_line: error is {Error}")
                        self.reset_curr_line()
                        count = 1
                    slogger.debug(f"classes.py:read_line: count[{count}] curr[{self._current_line}] line is: {line}")
                    # If the count is the current line we want, we update current line to the next for the
                    # next call and return the current line
                    if line == "": 
                        self.reset_curr_line()
                        count = 0
                        break
                    elif count == self._current_line: 
                        slogger.debug(f"classes.py:read_line: return is: {line} type:{type(line)}")
                        
                        self.update_curr_line()
                        return line
