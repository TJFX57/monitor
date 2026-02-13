from flask import current_app as app
from flask import render_template
from flask import send_file
from flask import redirect
from flask import url_for

from application import database

from crontab import CronTab
from os import getlogin
from subprocess import run
from socket import gethostname
import csv
import monitor

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "instance" / "image.jpeg"
CSV_PATH = BASE_DIR / "data.csv"

def get_connection_strength():
    link_start = 'Link Quality='
    link_end = '/70'
    signal_start = 'Signal level='
    signal_end   = ' dBm'

    result = run(['iwconfig','wlan0'], text=True, capture_output=True)

    link_index_start = result.stdout.find(link_start)
    link_index_end = result.stdout.find(link_end, link_index_start)
    signal_index_start = result.stdout.find(signal_start)
    signal_index_end = result.stdout.find(signal_end, signal_index_start)
    index_link_start = link_index_start+len(link_start)
    index_link_end = link_index_end
    index_signal_start = signal_index_start+len(signal_start)
    index_signal_end = signal_index_end

    return(int(result.stdout[index_link_start:index_link_end]), int(result.stdout[index_signal_start:index_signal_end]))

def get_logging_job():
    cron = CronTab(user=getlogin())
    for job in cron.find_command('monitor.py -w'):
        return job, cron

def get_version_hash():
    return run(['git', 'rev-parse', '--short', 'main'], cwd=BASE_DIR, text=True, capture_output=True).stdout

@app.route('/')
def index():
    job, _ = get_logging_job()
    wifi_quality, wifi_strength = get_connection_strength()
    version = get_version_hash()
    date_time, temperature, pressure, humidity, light = monitor.read_data()

    rows = database.query_database('SELECT * FROM measurements ORDER BY "date time" DESC LIMIT 1440')

    time_data = []
    temperature_data = []
    pressure_data = []
    humidity_data = []
    light_data = []

    for row in rows:
        time_data.insert(0, row[0][11:16])
        temperature_data.insert(0, row[1])
        pressure_data.insert(0, row[2])
        humidity_data.insert(0, row[3])
        light_data.insert(0, row[4])

    return render_template(
        'index.html',
        date_time = date_time,
        temperature = temperature,
        pressure = pressure,
        humidity = humidity,
        light = light,
        time_data = time_data,
        temperature_data = temperature_data,
        pressure_data = pressure_data,
        humidity_data = humidity_data,
        light_data = light_data,
        logging_ability = job.is_enabled(),
        wifi_quality = wifi_quality,
        wifi_strength = wifi_strength,
        hostname = gethostname(),
        version = version)

@app.route('/logging_ability')
def change_logging_ability():
    job, cron = get_logging_job()
    if job.is_enabled():
        job.enable(False)
    else:
        job.enable()
    cron.write()
    return redirect(url_for('index'))

@app.route('/download_data') #TODO Stream file rather than create an intermediate file & add header to CSV
def download_data():
        rows = database.query_database('SELECT * FROM measurements', names=True)
        with open(CSV_PATH, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        return send_file(CSV_PATH, mimetype='text/csv', as_attachment=True, max_age=0)

@app.route('/delete_data')
def delete_data():
    database.execute_database('DELETE FROM measurements')
    return redirect(url_for('index'))

@app.route('/log_data')
def log_data():
    monitor.write_data(monitor.read_data(), mode='m')
    return redirect(url_for('index'))

@app.route('/capture_image')
def capture_image():
     run(['rpicam-still', '--nopreview', '--output', IMAGE_PATH])
     return redirect(url_for('index'))

@app.route('/delete_image')
def delete_image():
    run(['rm', IMAGE_PATH])
    return redirect(url_for('index'))

@app.route('/reboot_monitor')
def reboot_monitor():
    run(["sudo", "shutdown", "-r", "1"])
    return redirect(url_for('index'))

@app.route('/update_monitor')
def update_monitor():
    run(["git", "pull"], cwd=BASE_DIR)
    return redirect(url_for('index'))