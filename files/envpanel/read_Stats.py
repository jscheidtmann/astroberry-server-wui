# Copyright (C) 2021 Jens Scheidtmann
# I herewith put this file into public domain

# run this file using:
# $ python3 read_Stats.py

import psutil
import os

# print(psutil.sensors_fans()) # Empty on Raspi 4
# print(psutil.loadavg()) # In docs, but throws error

print(psutil.sensors_temperatures())
print(psutil.cpu_percent())
print(os.getloadavg()) # avg number of process in run queue in last 1, 5 and 15 min.