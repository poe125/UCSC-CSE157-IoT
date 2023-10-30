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
    soilMoisture = "Soil Moisture:" + str(moisture) + "\n" + "Soil Temperature:" + str(temperature) + "\n"
#     print('Soil Moisture:'+ str(moisture))
#     print('Soil Temperature:'+ str(temperature))
    return soilMoisture

#getting information from SHT30 Temperature/Humidity sensor
def TempHumidity():
    sensor = adafruit_sht31d.SHT31D(I2C)
#     print('Humidity: {0}%'.format(sensor.relative_humidity))
#     print('Temperature: {0}C'.format(sensor.temperature))
    tempHumidity = "Temperature:" + str(sensor.temperature) + "\n" + "Humidity:" + str(sensor.relative_humidity) + "\n"    
    return tempHumidity

#getting information from the ADS1015 12-bit ADC
def WindSpeed():
     ads = ADS.ADS1015(I2C)
     chan = AnalogIn(ads, ADS.P0)
     map_speed = simpleio.map_range(chan.voltage, 0.40, 0.78, 0, 32) #map min and max 
     #print('Wind Speed:' + str(wind_speed))
     windSpeed = "Wind Speed:" + str(map_speed)
     return windSpeed
    
#getting time and date
def DateTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    dateTime = current_date + "\n" + current_time + "\n"
    return dateTime

def main():   
    with open('/home/akokuryo/Documents/gitHub/UCSC-CSE157-IoT/lab_2/polling-log.txt', 'w') as f:
        f.write("AiriKokuryo")
    
    while True:
        print("write start")
        returnDateTime = DateTime()
        returnSoilMoisture = SoilMoisture()
        returnTempHumidity = TempHumidity()
        returnWindSpeed = WindSpeed()       
        time.sleep(5)
        print("complete")
        
        with open('/home/akokuryo/Documents/gitHub/UCSC-CSE157-IoT/lab_2/polling-log.txt', 'a') as f:
            f.write(returnDateTime)
            f.write(returnSoilMoisture)
            f.write(returnTempHumidity)
            f.write(returnWindSpeed)
            f.write("\n")

main()
