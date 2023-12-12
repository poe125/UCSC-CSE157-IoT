import mysql.connector
import logging as log
import os
from flask import Flask, render_template
import logging 

SQL_IP = '169.233.161.85'
SQL_PORT = '3306'

# Set up logging for web app
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
slogger = logging.getLogger(f"(srv)")
slogger.setLevel(level=logging.DEBUG)
log.basicConfig(level=log.DEBUG)

class mySQL:
    """
    create connection with MySQL and handle tables
    """
    def __init__(self):
        self.conn = None
        self.data_array = []
        
    def create_connection(self):
        """
        Create connection with MySQL database
        """
        self.conn = mysql.connector.connect(host=SQL_IP, database='pisensedb', user='root', password='')

    def insert_update(self,sensor, data_list):
        """
        Insert data into the database table

        Args:
            sensor (string): name of the table
            data (float): list of data to insert into the table
        """
        try:
            self.create_connection()
            cursor = self.conn.cursor()
            
            #insert_query = (f"INSERT INTO {sensor} (Temperature, Humidity, WindSpeed, SoilMoisture) VALUES ({data[0]}, '{data[1]}', '{data[2]}', '{data[3]}')")
            sql_format = "("
            for data in data_list:
                sql_format += "'" + str(data) + "', "
            sql_format = sql_format[:-2]  # Removing the extra "', " at the end from the for loop
            insert_query = f"INSERT INTO {sensor} (Temperature, Humidity, SoilMoisture, WindSpeed, Risk_stage, Risk) VALUES {sql_format})"
            slogger.debug(f"SQL CLASS: attempting to send [{insert_query}]")
            cursor.execute(insert_query)
            log.debug("data sent")
            self.conn.commit()
            cursor.close()
            self.close_connection()
        except mysql.connector.Error as e:
            log.debug(f'insert_update: Error inserting data: {e}')

    def print_table(self, sensor):
        """
        Print out tables from the database
        
        Args:
            sensor (string): name of the table        
        """
        self.data_array = []
        try:
            self.create_connection()
            cursor = self.conn.cursor()
            select_query = (f"SELECT * FROM {sensor}")
            cursor.execute(select_query)
            row = cursor.fetchone()
            while row is not None:
                self.data_array.append(row)
                #print(row)
                row = cursor.fetchone()
            self.conn.commit()
            cursor.close()
            self.close_connection()
        except mysql.connector.Error as e:
            log.debug(f'print_table:Error fetching data: {e}')
        return self.data_array    
            
    def clear_table(self, sensor):
        """
        Clear all data from the table

        Args:
            sensor (_type_): name of the table
        """
        try:
            self.create_connection()
            cursor = self.conn.cursor()
            clear_query = (f"DELETE FROM {sensor}")
            cursor.execute(clear_query)
            self.conn.commit()
            log.debug('table cleared')
            cursor.close()
            self.close_connection()
        except mysql.connector.Error as e:
            log.debug(f'clear_table:Error clearing table: {e}')

    def close_connection(self):
        """
        Close connection with MySQL database
        """
        try:
            if self.conn.is_connected():
                self.conn.close()
        except mysql.connector.Error as e:
            log.debug(f'close_connection:Error closing connection: {e}')

class GetFlask:
    """
    Make a website using the imported data
    The website url will be "http://127.0.0.1:5000/" or "http://localhost:5000/"
    Either could be used.
    
    ^C to close connection
    """
    app = Flask(__name__)
    
    #Homepage
    @app.route('/')
    def check():
        return render_template("index.html")

    #Page for Sensor1
    @app.route('/sensor1')
    def sensor1():
        #receive data from mySQL and put it in the "array"
        mysql = mySQL()
        array = mysql.print_table("sensor_readings1")
        #using the data "array", create the web page using the html file
        return render_template("sensor1.html", content=array)
    

    #Page for Sensor2
    @app.route('/sensor2')
    def sensor2():
        mysql = mySQL()
        array = mysql.print_table("sensor_readings2")
        return render_template("sensor2.html", content=array)
    
    #Page for Sensor3
    @app.route('/sensor3')        
    def sensor3():
        mysql = mySQL()
        array = mysql.print_table("sensor_readings3")
        return render_template("sensor3.html", content=array)
 
def main():
    #insert and update data (make this dynamic)
    mysql = mySQL()
    mysql.clear_table("sensor_readings1")
    
    mysql.insert_update("sensor_readings1", [1.0,2.0,3.0,4.0, "low", 10])
    mysql.insert_update("sensor_readings2", [1.0,2.2,3.3,4.4, "low", 10])
    mysql.insert_update("sensor_readings1", [1.0,2.2,3.3,4.4, "low", 10])

if __name__ == "__main__":
    main()
