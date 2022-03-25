import time

from .magnetometer import Magnetometer

compass = Magnetometer(i2c_device="/dev/i2c-1", address=0x0C)

compass.run()