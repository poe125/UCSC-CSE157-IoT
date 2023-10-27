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
def NameADS():
     ads = ADS.ADS1015(I2C)
     chan = AnalogIn(ads, ADS.P0)
     print(chan.value, chan.voltage)

#getting time and date
def DateTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    print(current_date, current_time)

#getting wind speed
def WindSpeed():
     wind_speed = simpleio.map_range(150, 0, 255, 0, 1023)
     print('Wind Speed:' + str(wind_speed))

#only once
def name():
    print("Airi Kokuryo")

def main():   
    DateTime()
    SoilMoisture()
    TempHumidity()
    NameADS()
    WindSpeed()
    
main()