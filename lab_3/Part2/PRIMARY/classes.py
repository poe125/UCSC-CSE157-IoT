#General libraries
import board #General library for GPIO 
import busio #For io usage
#Board specfic libraries
import adafruit_sht31d #Library for temp and humd sensor
from adafruit_seesaw.seesaw import Seesaw
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import simpleio #For mapping voltage values to wind speed
#For files
import os
import matplotlib.pyplot as plt

#Constants for mapping the ADC values 
SENSOR_MIN = 0.41
SENSOR_MAX = 0.76
VALUE_MIN  = 0
VALUE_MAX  = 32.4
#Constants for files
FILE_NAME = "polling-log.txt"
FILE_LOCATION = "~/Desktop/"

class i2c_controller:
    def __init__(self):
        """
        Initialize the controllers for the temp and humd sensor, soil and moisture sensor, and ADC
        """
        #Create a i2c controller for board 
        self.i2c_board = board.I2C()

        #Create a i2c controller for bTemperatureusio
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)

        self.tempHumdContr = self.init_sht31d()
        self.soilMoistContr = self.init_seesaw()
        self.adcContr = self.init_adc()

    def init_sht31d(self):
        #Initialize the i2c device specfic controllers
        #For the temperature and humidity sensor
        try:
            return adafruit_sht31d.SHT31D(self.i2c_board)
        except ValueError:
            return None
        
    def init_seesaw(self):
        #For the soil and moisture sensor
        try:
            return Seesaw(self.i2c_board, addr=0x36)
        except ValueError:
            return None
            
    def init_adc(self):
        #For the ADC
        # don't unplug
        try:
            ads = ADS.ADS1015(self.i2c_bus)
            return AnalogIn(ads, ADS.P0)
        except ValueError:
            return None
        
    def getTemp(self):
        """
        Get the ambient temperature using the temperature and humidity sensor
        """
        #"rtemp:3232"
        # temp = "rtemp" + {:.2f}".format(self.tempHumdContr.temperature)

        try:
            temp = "rtemp:" + "{:.2f}".format(self.tempHumdContr.temperature)
        except:
            temp = "rtemp:ERR"
        return temp

    
    def getHumd(self):
        """
        Get the ambient moisture using the temperature and humidity sensor
        """
        try:
            hum = "rhumd:" + "{:.2f}".format(self.tempHumdContr.relative_humidity)
        except:
            hum = "rhumd:ERR"
        return hum

    def getSoilTemp(self): 
        """
        Get soil tempature using the soil and moisture sensor
        """
        try:
            data = "stemp:" + "{:.2f}".format(self.soilMoistContr.get_temp())
        except:
            data = "stemp:ERR"
        return data
            
    def getSoilMoist(self):
        """
        Get soil moisture using the soil and moisture sensor
        """
            
        try:
            data = "smois:" + "{:.2f}".format(self.soilMoistContr.moisture_read())

        except:
            data = "smois:ERR"
        return data
            
    def map_volt_value(self, voltage):
        """
        Map a voltage to a wind speed value and return it
        """

        try:
            mapped_value = "winds:" + "{:.2f}".format(simpleio.map_range(
                voltage, SENSOR_MIN, SENSOR_MAX, VALUE_MIN, VALUE_MAX))
        except:
            mapped_value = "winds:ERR"
        
        return mapped_value
    
    def getADCValue(self):
        """
        Get the value from the ADC
        """ 
        return self.adcContr.value
    
    def getADCVoltage(self):
        """
        Get the voltage reading from the ADC
        """
        return self.adcContr.voltage

class plotting_data:            
    def find_average(self, list_num):
        #REMOVE THE PRINT 
        try:
            total = sum(list_num)
            average = total/len(list_num)
            return average
        except ZeroDivisionError:
            return "Error: Division by zero occurred. Cannot calculated average for an empty list."
        
    def plot_data(self, number, rtemp_list, rhumd_list, smois_list, speed_list):
        """
        APPEND THE DATA FROM THE OWN RASPBERRY PI
        after receiving data from the two secondary pis but before plotting data
        """
        lables = ['Sec1', 'Sec2', 'Primary', 'Avg']
        #print(f"plot_data: rtemp_ist {rtemp_list}")
        i=0
        for i in range(3):
            if rtemp_list[i] == 'ERR':
                rtemp_list[i] = 0
            if rhumd_list[i] == 'ERR':
                rhumd_list[i] = 0
            if smois_list[i] == 'ERR':
                smois_list[i] = 0
            if speed_list[i] == 'ERR':
                speed_list[i] = 0

        #finding the average of three pi results        
        rtemp_avg = self.find_average(rtemp_list)
        rhumd_avg = self.find_average(rhumd_list)
        smois_avg = self.find_average(smois_list)
        speed_avg = self.find_average(speed_list)        
        
        #adding average to the list
        rtemp_list.append(rtemp_avg)
        rhumd_list.append(rhumd_avg)
        smois_list.append(smois_avg)
        speed_list.append(speed_avg)
 
        fig, axs = plt.subplots(2,2,figsize=(10,8))

        print(f"classes: {rtemp_list}")

        axs[0,0].plot(lables, rtemp_list, marker = 'o')
        axs[0,0].set_title('Temperature Sensor')
        axs[0,0].set_ylabel('Temperature(C)')
        axs[0,0].grid(True)

        axs[0,1].plot(lables, rhumd_list, marker = 'o')
        axs[0,1].set_title('Humidity Sensor')
        axs[0,1].set_ylabel('Humidity(%)')
        axs[0,1].grid(True)

        axs[1,0].plot(lables, smois_list, marker = 'o')
        axs[1,0].set_title('Soil Moisture Sensor')
        axs[1,0].set_ylabel('Soil Moisture')
        axs[1,0].grid(True)

        axs[1,1].plot(lables, speed_list, marker = 'o')
        axs[1,1].set_title('Wind Sensor')
        axs[1,1].set_ylabel('Wind speed(m/s)')
        axs[1,1].grid(True)

        plt.tight_layout()
        plot_folder = 'plotting_data/'
        filename = f'polling-plot-{number}.png'
        return plt.savefig(plot_folder+filename)
