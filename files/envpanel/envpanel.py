#!/usr/bin/env python3
# coding=utf-8

#  Copyright(c) 2017 Radek Kaczorek  <rkaczorek AT gmail DOT com>
#  Copyright(c) 2021 Jens Scheidtmann <Jens.Scheidtmann AT gmail DOT com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License version 3 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this library; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

# from gevent import monkey; monkey.patch_all()
from flask import Flask, render_template
from flask_socketio import SocketIO
from PIL import Image, ImageDraw
import time, base64, math, io, sys, psutil

__author__ = 'Jens Scheidtmann'
__copyright__ = 'Copyright 2021  Jens Scheidtmann'
__license__ = 'GPL-3'
__version__ = '0.1.0'

app = Flask(__name__, static_folder='assets')
socketio = SocketIO(app)
thread = None

import os.path
import rrdtool
import smbus2

env = '/var/local/astroberry/environment.rrd'
cpu = '/var/local/astroberry/computer.rrd'
power = '/var/local/astroberry/power.rrd'

duration="now-10h"

#########
# BME280

# Environmental readings (temperature, pressure and humidity) are collected every ten seconds.

import bme280

port = 1
address = 0x76  
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

#########
# INA260

from ina260.controller import Controller

# Read Voltage and Current readings from hte ina260 board, that is connected via I2C to your RaspPi
# 0x40 is the standard address used by the device, if you're using a different adress, change it here.
# Check which address your device is using by running:
# $ i2cdetect -y 1

ina260 = Controller(address=0x40)

############
# Graph configurations

conf_temperature = [
	"--start", duration,
	"DEF:envt=%s:temp:AVERAGE"%(env),
	'LINE1:envt#FF0000:Temperature / °C'
]

conf_pressure = [
	"--start", duration,
	"DEF:envp=%s:pressure:AVERAGE"%(env),
	'LINE1:envp#00FF00:Pressure / mbar'
]

conf_humidity = [
	"--start", duration,
	"DEF:envh=%s:humidity:AVERAGE"%(env),
	'LINE1:envh#0000FF:rel. Humidity / %'
]

conf_voltage = [
	"--start", duration,
	"DEF:powv=%s:voltage:AVERAGE"%(power),
	'LINE1:powv#FF0000:Voltage / V'
]

conf_current = [
	"--start", duration,
	"DEF:powc=%s:current:AVERAGE"%(power),
	'LINE1:powc#00FF00:Current / A'
]

conf_power = [
	"--start", duration,
	"DEF:powp=%s:power:AVERAGE"%(power),
	'LINE1:powp#0000FF:Power / W'
]

conf_percents = [
	"--start", duration,
	"DEF:cpu=%s:cpu:AVERAGE"%(cpu),
	"DEF:mem=%s:mem:AVERAGE"%(cpu),
	"DEF:disk=%s:disk:AVERAGE"%(cpu),
	'LINE1:cpu#FF0000:CPU / %',
	'LINE1:mem#00FF00:Memory / %',
	'LINE1:disk#0000FF:Disk / %'
]

conf_loads  = [
	"--start", duration,
	"DEF:l1=%s:load1:AVERAGE"%(cpu),
	"DEF:l5=%s:load5:AVERAGE"%(cpu),
	"DEF:l15=%s:load15:AVERAGE"%(cpu),
	'LINE1:l1#FF0000:Load Avg. 1 min',
	'LINE1:l5#00FF00:Load Avg. 5 min',
	'LINE1:l15#0000FF:Load Avg. 15 min'
]

conf_cputemp = [
	"--start", duration,
	"DEF:cput=%s:cputemp:AVERAGE"%(cpu),
	'LINE1:cput#FF0000:"CPU Temperature / °C"'
]

###############
# Store values and emit graphs

def background_thread():
	""" Read Raspi status & environmental data. 

	The minimally read sensors are : 
	- CPU, memory and disk usage of '/' (as percentages)
	- Load for 1, 5 and 15 minutes
	- CPU Temperature
	
	If further sensors are attached to the I2C bus:
	- BME280: Environmental temperature, pressure and relative humidity
	- INA260: Voltage, Current and Power.

	Every 10 seconds, new graphs are created and emitted to be displayed.
	"""

	# Every ten seconds:
	wait = 10
	slow = 10
	sleep_time = 1.0
	count = 0
	while True:
		# Pi State
		info= psutil.sensors_temperatures()
		avgs = os.getloadavg()
		rrdtool.update(cpu, f"N:{psutil.cpu_percent()}:{psutil.virtual_memory().percent}:{psutil.disk_usage('/').percent}:{info['cpu_thermal'][0].current}:{avgs[0]}:{avgs[1]}:{avgs[2]}")

		# Power
		rrdtool.update(power, f'N:{ina260.voltage()}:{ina260.current()}:{ina260.power()}')

		if (count % slow) == 0:
			data = bme280.sample(bus, address, calibration_params)

			# print(f"{data.timestamp}: t={data.temperature}, p={data.pressure}, h={data.humidity}")
			rrdtool.update(env, f'N:{data.temperature}:{data.pressure}:{data.humidity}')

		if (count % wait) == 0:
			# print("Emit")
			socketio.emit('environdata', {
				'temperature': create_graph(conf_temperature),
				'pressure': create_graph(conf_pressure),
				'humidity': create_graph(conf_humidity),
				'voltage': create_graph(conf_voltage),
				'current': create_graph(conf_current),
				'power': create_graph(conf_power),
				'percents': create_graph(conf_percents), 
				'loads': create_graph(conf_loads),
				'cputemp': create_graph(conf_cputemp)
			}) 

		count = count+1
		socketio.sleep(sleep_time)	

def create_graph(conf):
	data = rrdtool.graphv("-", *conf)
	imgdata_encoded = base64.b64encode(data['image']).decode()
	return imgdata_encoded

def shut_down():
    print('Keyboard interrupt received\nTerminated by user\nGood Bye.\n')
    sys.exit(1)

@app.route('/')
def main():
	return render_template('main.html')

@socketio.on('connect')
def handle_connect():
	global thread
	if thread is None:
		thread = socketio.start_background_task(target=background_thread)

if __name__ == '__main__':
	# TODO: Create rrdtool files, not overwriting them
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

	try:
		socketio.run(app, host='0.0.0.0', port = 8627, debug=False)
	except KeyboardInterrupt:
		shut_down()
