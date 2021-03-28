# Copyright (C) 2021 Jens Scheidtmann
# I herewith put this file into public domain

# Run this file using:
# $ pyhton3 read_Environment.py

import smbus2
import bme280

# Connect to the bme280 sensor connected on the I2C bus (SMBus)
# The standard address is given here. 0x76 is the standard address of a bme280. If you used a different one,
# check which address is used by running 
# $ i2cdetect -y 1
 
port = 1
address = 0x76  
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

# the sample method will take a single reading and return a
# compensated_reading object
data = bme280.sample(bus, address, calibration_params)

# the compensated_reading class has the following attributes
print(data.id)
print(data.timestamp)
print(data.temperature)
print(data.pressure)
print(data.humidity)

# there is a handy string representation too
print(data)
