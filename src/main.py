import asyncio
import os
import logging

from .magnetometer import Magnetometer
from .gps import GPS
from .ntrip import ntrip_client

logging.basicConfig(level=logging.INFO)

compass = Magnetometer(i2c_device="/dev/i2c-1", address=0x0C)
#compass.run()

ntrip = ntrip_client(caster="rtgpsout.unavco.org",
                user=os.getenv('NTRIP_USER'),
                password=os.getenv('NTRIP_PASSWORD'),
                mountpoint="SEAT_RTCM3")                        

gps = GPS(serial_port="/dev/ttyACM0", ntrip_client=ntrip)
#gps.run()

async def main():
    await asyncio.gather(gps.run(), 
                         compass.run())
    

asyncio.run(main())