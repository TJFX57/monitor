# Monitor

Monitor is a program to monitor the environment via sensors attached to a raspberry pi

## Installation

git clone https://github.com/TJFX57/monitor.git
create venv
install requirements.txt


## Usage
python3 monitor.py -w -> read and write data to database
python3 monitor.py -r -> read measurements to terminal

## Todo
- Use systemd instead of cron