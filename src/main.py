import os

from .magnetometer import Magnetometer
from .gps import GPS
from .ntrip import NtripClient

compass = Magnetometer(i2c_device="/dev/i2c-1", address=0x0C)
#compass.run()

ntrip = NtripClient(caster="rtgpsout.unavco.org",
                    user=f"{os.getenv('NTRIP_USER')}:{os.getenv('NTRIP_PASSWORD')}",
                    verbose=True)

ntrip.readData()                    

gps = GPS(serial_port="/dev/ttyACM0")
#gps.run()