import argparse
import sqlite3
from math import isnan
from statistics import mean
from datetime import datetime
from display import Display
from PiicoDev_BME280 import PiicoDev_BME280
from PiicoDev_VEML6030 import PiicoDev_VEML6030
from PiicoDev_TMP117 import PiicoDev_TMP117

DATABASE_PATH = '/home/controller/data.db'
DATABASE_SCHEMA_PATH = '/home/controller/controller/schema.sql'

def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

def get_temperature(sensor: PiicoDev_TMP117): #Does not fault to an error!
    measurement = sensor.readTempC()
    if isnan(measurement):
        raise ValueError("could not get temperature measurement")
    else:
        return measurement

def get_pressure(sensor: PiicoDev_BME280): #Does not fault to an error!
    _, measurement, _ = sensor.values()
    if isnan(measurement):
        raise ValueError("could not get pressure measurement")
    else:
        return measurement

def get_humidity(sensor: PiicoDev_BME280): #Does not fault to an error!
    _, _, measurement = sensor.values()
    if isnan(measurement):
        raise ValueError("could not get humidity measurement")
    else:
        return measurement

def get_light(sensor: PiicoDev_VEML6030): #Does not fault to an error!
    measurement = sensor.read()
    if isnan(measurement):
        raise ValueError("could not get light measurement")
    else:
        return measurement

# Measure data and average 3 times to limit any outliers in measurement.
def read_data(sample_size=3):
    with Display(mode='r'):
        try:
            # Initialise the sensors.
            bme280 = PiicoDev_BME280()
            veml6030 = PiicoDev_VEML6030()
            tmp117 = PiicoDev_TMP117()

            # Read and assign initial altitude reading.
            zero_alt = bme280.altitude()

            # Initialise sensor value lists.
            temp_C_values = []
            pres_HPa_values = []
            hum_RH_values = []
            light_Lx_values = []

            date_time = get_time()

            for _ in range(sample_size):
                # Read and assign the sensor values.
                temp_C_values.append(get_temperature(tmp117))
                pres_HPa_values.append((get_pressure(bme280))/100)
                hum_RH_values.append(get_humidity(bme280))
                light_Lx_values.append(get_light(veml6030))
            # Find average of measurement values.
            temp_C_ave = round(mean(temp_C_values), 2)
            pres_HPa_ave = round(mean(pres_HPa_values), 2)
            hum_RH_ave = round(mean(hum_RH_values), 2)
            light_Lx_ave = round(mean(light_Lx_values), 2)
        except ValueError as e:
            raise e

    return date_time, temp_C_ave, pres_HPa_ave, hum_RH_ave, light_Lx_ave

def write_data(data: tuple, mode='a'):
        with Display(mode='w'):
            try:
                connection = sqlite3.connect(DATABASE_PATH)
                with open(DATABASE_SCHEMA_PATH, mode='r') as schema:
                    connection.execute(schema.read())
                connection.execute('INSERT INTO measurements VALUES(?, ?, ?, ?, ?, ?)', (data[0], data[1], data[2], data[3], data[4], mode))
                connection.commit()
                connection.close()
            except Exception as e:
                connection.close()
                raise e

if __name__ == '__main__':
    # Initialize the input argument parser, add and parse input arguments.
    parser = argparse.ArgumentParser(description="System Controller")
    parser.add_argument('-r', '--read', help="read measurements to terminal", action='store_true')
    parser.add_argument('-w', '--write', help="write measurements to file", action='store_true')
    parser.add_argument('repeat', nargs='?', help="number of times to read/write", default=1, type=int)
    args = parser.parse_args()

    for _ in range(args.repeat):
        data = read_data()
        if args.write:
            write_data(data)
        if args.read:
            print("Date-Time:\t", data[0])
            print("Temperature:\t", str(data[1]) + "°C")
            print("Pressure:\t", str(data[2]) + "HPa")
            print("Humidity:\t", str(data[3]) + "RH")
            print("Light:\t\t", str(data[4]) + "lx")