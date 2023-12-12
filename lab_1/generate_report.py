import requests
import json

from datetime import datetime
from datetime import date

#print("Airi Kokuryo")

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
#print(current_time)

current_date = now.strftime("%Y-%m-%d")
#print(current_date)

# Define the API endpoint URL
url = "https://api.open-meteo.com/v1/forecast?latitude=37&longitude=-122.06&daily=temperature_2m_max&timezone=UTC&forecast_days=7"

# Define the parameters
params = {

}

#the GET request to the API
response = requests.get(url, params=params)

# Check if the request was successful (status code 200)
if response.status_code == 200:

    data = response.json()
    print(data)
    # Make the data type to string
    current_data = json.dumps(data)

else:
    # Handle the case where the request was
    print("API request failed with status code:", response.status_code)
    print("API response content:", response.text)
 
# Write out the text document    
with open('/home/akokuryo/Documents/report.txt', 'w') as f:
    f.write("AiriKokuryo")
    f.write(current_date)
    f.write(current_time)
    f.write(current_data)
