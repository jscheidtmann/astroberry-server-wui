# Copyright (C) 2021 Jens Scheidtmann
# I herewith put this file into public domain

# run this file using:
# $ python3 read_Stats.py

import psutil
import os

# print(psutil.sensors_fans()) # Empty on Raspi 4
# print(psutil.loadavg()) # In docs, but throws error

info = psutil.sensors_temperatures() 
print(info)
print(info['cpu_thermal'][0].current)
print(psutil.cpu_percent())

avgs = os.getloadavg()
print(avgs) # avg number of process in run queue in last 1, 5 and 15 min.
print(avgs[0])

print("CPU%", psutil.cpu_percent())
print("MEM%", psutil.virtual_memory().percent)
print("Disk%", psutil.disk_usage('/').percent)