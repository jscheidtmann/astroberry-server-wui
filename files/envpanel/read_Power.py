from ina260.controller import Controller

# Read Voltage and Current readings from hte ina260 board, that is connected via I2C to your RaspPi
# 0x40 is the standard address used by the device, if you're using a different adress, change it here.
# Check which address your device is using by running:
# $ i2cdetect -y 1

c = Controller(address=0x40)

print(c.voltage())
print(c.current())
print(c.power())

