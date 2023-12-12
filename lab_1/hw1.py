from datetime import datetime, date
print("Airi Kokuryo")
time = datetime.now()
print(time.strftime("%H:%M:%S"))
print(date.today())

import 
# #from openmeteo_py.Daily.Marine import Marine as Daily
# from openmeteo_py import OWmanager
# from openmeteo_py.Hourly.HourlyForecast import HourlyForecast
# from openmeteo_py.Daily.DailyForecast import DailyForecast
# from openmeteo_py.Options.ForecastOptions import ForecastOptions
# from openmeteo_py.Utils.constants import *

# # Latitude, Longitude 
# longitude = 33.89
# latitude =  -6.31

# hourly = HourlyForecast()
# daily = DailyForecast()

# #here we provide a bit more information as we want to pull also the data of past days
# options = ForecastOptions(latitude,longitude,False,celsius,kmh,mm,iso8601,utc,2)

# #notice that we had to give the value "None" for the hourly parameter,otherwise you'll be filling the hourly parameter instead of the daily one.
# mgr = OWmanager(options,OWmanager.forecast,hourly.shortwave_radiation(),daily.shortwave_radiation_sum())


# # Download data
# meteo = mgr.get_data(1)

# print(meteo)