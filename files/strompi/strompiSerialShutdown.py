#!/usr/bin/env python
import serial
import os
import sys
##############################################################################
# Wait this time before the Raspberry PI is shutdown, after powerloss of the 
# primary power source is detected.
# 
# This is realized by the number of read times outs below.
# 
# Units: seconds

##############################################################################
wait_for_shutdowntimer = 10;
##############################################################################

# This is the read time out for the serial port
read_timeout = 1

# Initialize the Serial Port, using values as specified in the documentation of StromPi3.
ser = serial.Serial(
 port='/dev/serial0', 
 baudrate = 38400,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=read_timeout  # Wait on read (seconds)
)

# Statistics
counter=0

print("StromPi service listening on /dev/serial0", file=sys.stderr)

t = 0 # Count Down to timeout.
while True:
    x = ser.readline()
    y = x.decode(encoding='UTF-8',errors='strict')
    if '' != y and y.startswith('xxx') and not y.endswith("xxx\n"): 
        print("Inconsistent results from serial, Raspberry Pi Shutdown initiated")
        print(f"Serial result: '{y}'")
        t = wait_for_shutdowntimer + 1
    if y == 'xxxShutdownRaspberryPixxx\n':
        counter += 1
        print (f"PowerFail - Raspberry Pi Shutdown initiated (#{counter})")
        t = wait_for_shutdowntimer + 1
    elif y == 'xxx--StromPiPowerBack--xxx\n':
        print (f"PowerBack - Raspberry Pi Shutdown aborted (#{counter})")
        t = 0
    if t > 0:
        t -= 1 # Count down
    if t == 1:
        print ("PowerFail - Raspberry Pi Shutdown")
        os.system("shutdown -h now")

