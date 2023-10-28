import time
import board
import busio

from adafruit_seesaw.seesaw import Seesaw
import adafruit_sht31d
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import simpleio

from datetime import datetime
from datetime import date

I2C = busio.I2C(board.SCL, board.SDA)

#SoilMoisture.py
def SoilMoisture():
    i2c = board.I2C()
    ss = Seesaw(i2c, addr=0x36)
    temperature = ss.get_temp()
    moisture = ss.moisture_read()
    print('Soil Moisture:'+ str(moisture))
    print('Soil Temperature:'+ str(temperature))
    
#getting information from SHT30 Temperature/Humidity sensor
def TempHumidity():
    sensor = adafruit_sht31d.SHT31D(I2C)
    print('Humidity: {0}%'.format(sensor.relative_humidity))
    print('Temperature: {0}C'.format(sensor.temperature))
    
#getting information from the ADS1015 12-bit ADC
def WindSpeed():
     ads = ADS.ADS1015(I2C)
     chan = AnalogIn(ads, ADS.P0)
     max_number = 0;
     print("ADS:",chan.value, chan.voltage)
     while True:
         voltage = chan.voltage
         wind_speed = simpleio.map_range(voltage,	 #Actual read value
                                      0.40, 0.78, #sensor min and max 
                                      0, 32) #map min and max 
#          if(max_number < voltage):
#              max_number = voltage
         print('Wind Speed:' + str(wind_speed)+ ' max:' + str(max_number) + " volt: " + str(voltage))
     
#getting time and date
def DateTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    print(current_date, current_time)

#only once
def name():
    print("Airi Kokuryo")

def main():   
    DateTime()
   # SoilMoisture()
    TempHumidity()
    WindSpeed()
    time.sleep(5)
    
main()