from classes import i2c_controller
from time import sleep

rpi = i2c_controller()

while True:
    #Rtemp sensor 
    print(rpi.getTemp())
    
    #RHumd Sensor
    print(rpi.getHumd())

    #Stemp sensor
    print(rpi.getSoilTemp())

    #Smois sensor
    print(rpi.getSoilMoist())

    #Wind sensor
    print(rpi.map_volt_value(rpi.getADCVoltage()))

    sleep(2)
