from web_app import mySQL

def main():
    #insert and update data (make this dynamic)
    mysql = mySQL()
    mysql.clear_table("sensor_readings1")
    mysql.clear_table("sensor_readings2")
    mysql.clear_table("sensor_readings3")

if __name__ == "__main__":
    main()
