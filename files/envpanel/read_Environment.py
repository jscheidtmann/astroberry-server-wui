# Copyright (C) 2021 Jens Scheidtmann
# I herewith put this file into public domain

# Run this file using:
# $ pyhton3 read_Environment.py

# This will create rrd databases in /var/local/astroberry for computer health measures 
# like Cpu%, Mem%, Diak%, Load for 1,5 and 15 min and sensor reading from different sensors
# and fill these databases.

# Check, if a RRDTool database exists, if not, create it

import os.path
import rrdtool

env = '/var/local/astroberry/environment.rrd'
cpu = '/var/local/astroberry/computer.rrd'
power = '/var/local/astroberry/power.rrd'

# Environmental readings (temperature, pressure and humidity) are collected every ten seconds.

if not os.path.exists(env):
    print("Creating environment.rrd")
    rrdtool.create(env, '--start', 'now', '--step', '10s', 
        'DS:temp:GAUGE:30s:-80:80',
        'DS:pressure:GAUGE:30s:0:3000',
        'DS:humidity:GAUGE:30s:0:100',
        'RRA:AVERAGE:0.5:1:1d',
        'RRA:AVERAGE:0.5:5m:14d',
        'RRA:AVERAGE:0.5:15m:60d',
        'RRA:AVERAGE:0.5:30m:180d')

if not os.path.exists(cpu):
    print("Creating computer.rrd")
    rrdtool.create(cpu, '--start', 'now', '--step', '1s',
        'DS:cpu:GAUGE:5s:0:100',
        'DS:mem:GAUGE:5s:0:100',
        'DS:disk:GAUGE:5s:0:100',
        'DS:cputemp:GAUGE:5s:U:U',
        'DS:load1:GAUGE:5s:0:U',
        'DS:load5:GAUGE:5s:0:U',
        'DS:load15:GAUGE:5s:0:U',
        'RRA:AVERAGE:0.5:1:1d',
        'RRA:AVERAGE:0.5:1m:7d',
        'RRA:AVERAGE:0.5:5m:14d',
        'RRA:AVERAGE:0.5:15m:60d',
        'RRA:AVERAGE:0.5:30m:180d')

if not os.path.exists(power):
    print("Creating power.rrd")
    rrdtool.create(power, '--start', 'now', '--step', '1s',
        'DS:voltage:GAUGE:5s:U:U',
        'DS:current:GAUGE:5s:U:U',
        'DS:power:GAUGE:5s:U:U',
        'RRA:AVERAGE:0.5:1:1d',
        'RRA:AVERAGE:0.5:5m:14d',
        'RRA:AVERAGE:0.5:15m:60d',
        'RRA:AVERAGE:0.5:30m:180d')

import smbus2
import bme280
import time

###################
#   Environment   #
###################
# 
# Connect to the bme280 sensor connected on the I2C bus (SMBus)
# The standard address is given here. 0x76 is the standard address of a bme280. If you used a different one,
# check which address is used by running 
# $ i2cdetect -y 1
 
port = 1
address = 0x76  
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

#####################
#   Power Reading   #
#####################

from ina260.controller import Controller

# Read Voltage and Current readings from hte ina260 board, that is connected via I2C to your RaspPi
# 0x40 is the standard address used by the device, if you're using a different adress, change it here.
# Check which address your device is using by running:
# $ i2cdetect -y 1

c = Controller(address=0x40)

#######################
#   State of the PI   #
#######################

import psutil
import os

############################
#   Collect informations   # 
############################
# 
# ad infinitum
#  
i = 0
while True:
    # Every 10 power samples, sample once the environment.
    if i % 10 == 0: 
        # the sample method will take a single reading and return a
        # compensated_reading object
        data = bme280.sample(bus, address, calibration_params)

        # print(f"{data.timestamp}: t={data.temperature}, p={data.pressure}, h={data.humidity}")
        rrdtool.update(env, f'N:{data.temperature}:{data.pressure}:{data.humidity}')

    # Power
    rrdtool.update(power, f'N:{c.voltage()}:{c.current()}:{c.power()}')

    # Pi State
    info= psutil.sensors_temperatures()
    avgs = os.getloadavg()
    rrdtool.update(cpu, f"N:{psutil.cpu_percent()}:{psutil.virtual_memory().percent}:{psutil.disk_usage('/').percent}:{info['cpu_thermal'][0].current}:{avgs[0]}:{avgs[1]}:{avgs[2]}")

    i = i+1
    time.sleep(1)

