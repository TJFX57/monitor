# Monitor

Monitor is a program to monitor the environment via sensors attached to a raspberry pi with data viewable via a web interface

## Installation

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