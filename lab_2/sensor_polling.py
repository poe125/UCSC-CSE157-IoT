import time
import board
import busio

from adafruit_seesaw.seesaw import Seesaw
import adafruit_sht31d
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import analogio
import simpleio

from datetime import datetime
from datetime import date

#SoilMoisture.py
def SoilMoisture():
    i2c = board.I2C
    ss = Seesaw(i2c, addr=0x36)
    temperature = ss.get_temp()
    moisture = ss.moisture_read()

#getting information from SHT30 Temperature/Humidity sensor
def TempHumidity():
    i2cTH = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_sht31d.SHT31D(i2cTH)

#getting information from the ADS1015 12-bit ADC
def ADS():
    i2cADS = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1015(i2cADS)
    chan = AnalogIn(ads, ADS.P0)

#getting time and date
def DateTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")


#wind speed
adc = analogio.AnalogIn(board.D4)

def adc_to_wind_speed(val):
    """Returns anemometer wind speed, in m/s.
    :param int val: ADC value
    """
    voltage_val = val / 65535 * 3.3
    return map_range(voltage_val, 0.4, 2, 0, 32.4)

wind_speed = adc_to_wind_speed(adc.value)

#only once
def name():
    print("Airi Kokuryo")

def main():   
    #date and time
    print(current_date, current_time)
    
    #temperatue and etc.
    print('Humidity: {0}%'.format(sensor.relative_humidity))
    print('Temperature: {0}C'.format(sensor.temperature))
    print('Soil Moisture:'+ str(moisture))
    print('Soil Temperature:'+ str(temperature))
    print('Wind Speed:' + str(wind_speed))

 
#print data
name()
while(i2c):
    SoilMoisture()
    TempHumidity()
    ADS()
    DateTime()
    
    main()
