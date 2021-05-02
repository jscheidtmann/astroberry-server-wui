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
import time, base64, math, io, sys

__author__ = 'Jens Scheidtmann'
__copyright__ = 'Copyright 2021  Jens Scheidtmann'
__license__ = 'GPL-3'
__version__ = '0.1.0'

app = Flask(__name__, static_folder='assets')
socketio = SocketIO(app)
thread = None


def background_thread():
	""" Read Raspi status & environmental data. 

	The minimally read sensors are : 
	- CPU, memory and disk usage (percentages)
	- Load for 1, 5 and 15 minutes
	
	If further sensors are attached to the I2C bus:
	- BME280: Environmental temperature, pressure and relative humidity
	- INA260: Voltage, Current and Power.

	"""
	for new_data in 
		if new_data:
			# TODO: Read output from BME280.
			pass
		else:
			time.sleep(5)


	# from gpspanel, see there
	# encode and return
	imgdata = io.BytesIO()
	img.save(imgdata, format="PNG")
	imgdata_encoded = base64.b64encode(imgdata.getvalue()).decode()
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

	try:
		socketio.run(app, host='0.0.0.0', port = 8627, debug=False)
	except KeyboardInterrupt:
		shut_down()
