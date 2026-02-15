from flask import current_app as app
from flask import render_template
from flask import send_file
from flask import redirect
from flask import url_for
from flask import flash
from flask import jsonify

from application import database

from crontab import CronTab
from os import getlogin
from subprocess import run
from socket import gethostname
import csv
import monitor
import re

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR.parent / "instance" / "image.jpeg"
CSV_PATH = BASE_DIR.parent / "instance" / "data.csv"

def get_connection_strength():
    try:
        result = run(['iwconfig', 'wlan0'], text=True, capture_output=True, check=True)
        quality = int(re.search(r'Link Quality=(\d+)', result.stdout).group(1))
        strength = int(re.search(r'Signal level=(-?\d+)', result.stdout).group(1))
        return quality, strength
    except Exception:
        return 0, 0

def get_logging_job():
    cron = CronTab(user=getlogin())
    for job in cron.find_command('monitor.py -w'):
        return job, cron

def get_version_hash():
    try:
        result = run(['git', 'rev-parse', '--short', 'main'], cwd=BASE_DIR, text=True, capture_output=True, check=True)
        return result.stdout.strip()
    except Exception:
        return "unknown"

@app.route('/')
def index():
    job, _ = get_logging_job()
    wifi_quality, wifi_strength = get_connection_strength()
    version = get_version_hash()
    date_time, temperature, pressure, humidity, light = monitor.read_data()

    rows = database.query_database('SELECT * FROM measurements ORDER BY "date time" ASC LIMIT 1440')

    time_data = []
    temperature_data = []
    pressure_data = []
    humidity_data = []
    light_data = []

    for row in rows:
        time_data.append(row[0][11:16])
        temperature_data.append(row[1])
        pressure_data.append(row[2])
        humidity_data.append(row[3])
        light_data.append(row[4])

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
    try:
        job, cron = get_logging_job()
        if job.is_enabled():
            job.enable(False)
        else:
            job.enable()
        cron.write()
        flash('Logging ability changed', 'success')
    except Exception as e:
        flash(f'Error changing logging ability: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/download_data') #TODO Stream file rather than create an intermediate file & add header to CSV
def download_data():
        try:
            CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
            rows = database.query_database('SELECT * FROM measurements', names=True)
            with open(CSV_PATH, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
            return send_file(CSV_PATH, mimetype='text/csv', as_attachment=True, max_age=0)
        except Exception as e:
            flash(f'Error downloading data: {str(e)}', 'error')
            return redirect(url_for('index'))

@app.route('/delete_data')
def delete_data():
    try:
        database.execute_database('DELETE FROM measurements')
        flash('Data deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting data: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/log_data')
def log_data():
    try:
        monitor.write_data(monitor.read_data(), mode='m')
        flash('Data logged successfully', 'success')
    except Exception as e:
        flash(f'Error logging data: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/capture_image', methods=['POST'])
def capture_image_api():
    try:
        IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        run(['rpicam-still', '--nopreview', '--output', str(IMAGE_PATH)], check=True)
        flash('Image captured successfully', 'success')
    except Exception as e:
        flash(f'Error capturing image: {str(e)}', 'error')

@app.route('/get_image')
def get_image():
    if not IMAGE_PATH.exists():
        return "No image available", 404
    return send_file(IMAGE_PATH, mimetype='image/jpeg')

@app.route('/delete_image')
def delete_image():
    try:
        if IMAGE_PATH.exists():
            IMAGE_PATH.unlink()
        flash('Image deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting image: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/reboot_monitor')
def reboot_monitor():
    try:
        run(["sudo", "shutdown", "-r", "1"], check=True)
        flash('System rebooting...', 'success')
    except Exception as e:
        flash(f'Error rebooting: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/update_monitor')
def update_monitor():
    try:
        run(["git", "pull"], cwd=BASE_DIR, check=True)
        flash('Updates pulled successfully', 'success')
    except Exception as e:
        flash(f'Error updating: {str(e)}', 'error')
    return redirect(url_for('index'))