import time

from .magnetometer import Magnetometer
from .gps import GPS

compass = Magnetometer(i2c_device="/dev/i2c-1", address=0x0C)
#compass.run()

gps = GPS(serial_port="/dev/ttyACM0")
gps.run()