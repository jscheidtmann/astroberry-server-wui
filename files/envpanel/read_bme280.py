# Copyright (C) 2021 Jens Scheidtmann
# I herewith put this file into public domain

# Run this file using:
# $ pyhton3 read_bme280.py


import smbus2
import bme280

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

data = bme280.sample(bus, address, calibration_params)

print(data)
