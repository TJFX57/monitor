import argparse
import sqlite3
from math import isnan
from statistics import mean
from datetime import datetime
from flask import current_app
from display import Display
from PiicoDev_BME280 import PiicoDev_BME280
from PiicoDev_VEML6030 import PiicoDev_VEML6030
from PiicoDev_TMP117 import PiicoDev_TMP117
from PiicoDev_ENS160 import PiicoDev_ENS160
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "instance" / "data.db"
DATABASE_SCHEMA_PATH = BASE_DIR / "application" / "schema.sql"

# Initialise sensors once
bme280 = PiicoDev_BME280()
veml6030 = PiicoDev_VEML6030()
tmp117 = PiicoDev_TMP117()
ens160 = PiicoDev_ENS160()

def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

# Get temperature data from TMP117 or BME280
def get_temperature(sensor):
    if isinstance(sensor, PiicoDev_TMP117):
        measurement = sensor.readTempC()

    elif isinstance(sensor, PiicoDev_BME280):
        measurement, _, _ = sensor.values()

    else:
        raise TypeError("Unsupported sensor type")

    if isnan(measurement):
        raise ValueError("could not get temperature measurement")

    return measurement

# Get pressure data from BME280
def get_pressure(sensor: PiicoDev_BME280):
    _, measurement, _ = sensor.values()
    if isnan(measurement):
        raise ValueError("could not get pressure measurement")
    else:
        return measurement

# Get humidity data from BME280
def get_humidity(sensor: PiicoDev_BME280):
    _, _, measurement = sensor.values()
    if isnan(measurement):
        raise ValueError("could not get humidity measurement")
    else:
        return measurement

# Get altitude data from BME280
def get_altitude(sensor: PiicoDev_BME280, zero_alt=0):
    measurement = sensor.altitude(zero_alt)
    if isnan(measurement):
        raise ValueError("could not get altitude measurement")
    else:
        return measurement

# Get light data from VEML6030
def get_light(sensor: PiicoDev_VEML6030):
    measurement = sensor.read()
    if isnan(measurement):
        raise ValueError("could not get light measurement")
    else:
        return measurement

# Get air quality data from ENS160
def get_aqi(sensor: PiicoDev_ENS160):
    measurement = sensor.aqi.value
    if isnan(measurement):
        raise ValueError("could not get AQI measurement")
    else:
        return measurement

# Get total volatile organic compounds data from ENS160
def get_tvoc(sensor: PiicoDev_ENS160):
    measurement = sensor.tvoc
    if isnan(measurement):
        raise ValueError("could not get TVOC measurement")
    else:
        return measurement

# Get equivalent CO2 data from ENS160
def get_eco2(sensor: PiicoDev_ENS160):
    measurement = sensor.eco2.value
    if isnan(measurement):
        raise ValueError("could not get eCO2 measurement")
    else:
        return measurement

# Get operational mode data from sensor
def get_mode(sensor):
    if (sensor is PiicoDev_ENS160):
        measurement = sensor.operation
        if isnan(measurement):
            raise ValueError("could not get operational mode measurement")
        else:
            return measurement
    else:
        raise TypeError("Unsupported sensor type")

# Measure data and average 3 times to limit any outliers in measurement
def read_data(sample_size=3):
    with Display(mode='r'):
        try:
            # Initialise sensor value lists
            temp_C_values = []
            pres_HPa_values = []
            hum_RH_values = []
            light_Lx_values = []
            aqi_values = []
            tvoc_values = []
            eco2_values = []

            date_time = get_time()

            for _ in range(sample_size):
                # Read and assign the sensor values
                temp_C_values.append(get_temperature(tmp117))
                pres_HPa_values.append((get_pressure(bme280))/100)
                hum_RH_values.append(get_humidity(bme280))
                light_Lx_values.append(get_light(veml6030))
                aqi_values.append(get_aqi(ens160))
                tvoc_values.append(get_tvoc(ens160))
                eco2_values.append(get_eco2(ens160))

            # Find average of measurement values
            temp_C_ave = round(mean(temp_C_values), 2)
            pres_HPa_ave = round(mean(pres_HPa_values), 2)
            hum_RH_ave = round(mean(hum_RH_values), 2)
            light_Lx_ave = round(mean(light_Lx_values), 2)
            aqi_ave = round(mean(aqi_values), 2)
            tvoc_ave = round(mean(tvoc_values), 2)
            eco2_ave = round(mean(eco2_values), 2)

        except ValueError as e:
            raise e

    return date_time, temp_C_ave, pres_HPa_ave, hum_RH_ave, light_Lx_ave, aqi_ave, tvoc_ave, eco2_ave

def write_data(data: tuple, mode='a'):
        with Display(mode='w'):
            try:
                connection = sqlite3.connect(DATABASE_PATH)
                with open(DATABASE_SCHEMA_PATH, mode='r') as schema:
                    connection.execute(schema.read())
                connection.execute('INSERT INTO measurements VALUES(?, ?, ?, ?, ?, ?, ?, ?)', (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]))
                connection.commit()
                connection.close()
            except Exception as e:
                connection.close()
                raise e

if __name__ == '__main__':
    # Initialize the input argument parser, add and parse input arguments
    parser = argparse.ArgumentParser(description="Monitor")
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
            print("AQI:\t\t", str(data[5]))
            print("TVOC:\t\t", str(data[6]) + "ppb")
            print("eCO2:\t\t", str(data[7]) + "ppm")