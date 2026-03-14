# Monitor

Monitor is a program to monitor the environment via sensors attached to a raspberry pi with data viewable via a web interface

## Installation

use raspberry pi imager to image sd card to raspberry pi os
	select apprporate settings to allow for headless start up
	use raspberry pi connect to allow for IP finding if not connected on owned network
git clone https://github.com/TJFX57/monitor.git
create venv
install cronjobs
install requirements.txt
activate i2c on pi
reboot

## Usage
python3 monitor.py -w -> read and write data to database
python3 monitor.py -r -> read measurements to terminal

## Todo
- Use systemd instead of cron
- make display useable on it's own
- update should check the requirements list and update if needed