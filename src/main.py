import asyncio
import os

from .magnetometer import Magnetometer
from .gps import GPS
from .ntrip import ntrip_client

compass = Magnetometer(i2c_device="/dev/i2c-1", address=0x0C)
#compass.run()

                                

gps = GPS(serial_port="/dev/ttyACM0")
#gps.run()

async def main():
    ntrip = await ntrip_client(caster="rtgpsout.unavco.org",
                        user=os.getenv('NTRIP_USER'),
                        password=os.getenv('NTRIP_PASSWORD'),
                        mountpoint="SEAT_RTCM3")
    

asyncio.run(main())