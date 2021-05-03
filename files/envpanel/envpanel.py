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
	'LINE1:l1#D3D3D3:Load Avg. (1 min)',
	'LINE1:l5#000000:Load Avg. (5 min)',
	'LINE1:l15#FF0000:Load Avg. (15 min)'
]

conf_cputemp = [
	"--start", duration,
	"DEF:cput=%s:cputemp:AVERAGE"%(cpu),
	'LINE1:cput#FF0000:"CPU Temperature / °C"'
]

###############
# Emit graphs

def background_thread():
	""" 
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
	sleep_time = 10
	while True:
		# print("Emit")
		envdata = rrdtool.lastupdate(env)
		compdata = rrdtool.lastupdate(cpu)
		pdata= rrdtool.lastupdate(power)

		socketio.emit('environdata', {
			't': "{:.1f}°C".format(envdata['ds']['temp']),
			'p': "{:.0f} mbar".format(envdata['ds']['pressure']),
			'h': "{:.1f}%".format(envdata['ds']['humidity']),
			'temperature': create_graph(conf_temperature),
			'pressure': create_graph(conf_pressure),
			'humidity': create_graph(conf_humidity),
			'v' : "{:.1f} V".format(pdata['ds']['voltage']),
			'c' : "{:.3f} A".format(pdata['ds']['current']),
			'pow' : "{:.1f} W".format(pdata['ds']['power']),
			'voltage': create_graph(conf_voltage),
			'current': create_graph(conf_current),
			'power': create_graph(conf_power),
			'cpu_percent': "{:.1f} %".format(compdata['ds']['cpu']),
			'mem_percent': "{:.1f} %".format(compdata['ds']['mem']),
			'disk_percent': "{:.1f} %".format(compdata['ds']['disk']),
			'percents': create_graph(conf_percents), 
			'loadvals': "{:.1f}, {:.1f}, {:.1f}".format(compdata['ds']['load1'],compdata['ds']['load5'],compdata['ds']['load15']),
			'loads': create_graph(conf_loads),
			'cputempval': "{:.1f}°C".format(compdata['ds']['cputemp']),
			'cputemp': create_graph(conf_cputemp)
		}) 

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
	if not os.path.exists(env) or not os.path.exists(cpu) or not os.path.exists(power):
		print("Can't find RRDtool databases for astroberry. (Check /var/local/astroberry)")
		sys.exit(1)

	try:
		socketio.run(app, host='0.0.0.0', port = 8627, debug=False)
	except KeyboardInterrupt:
		shut_down()
