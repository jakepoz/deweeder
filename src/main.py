import asyncio
import os
import logging

from .magnetometer import Magnetometer
from .gps import GPS
from .ntrip import NtripClient
from .drive_motor import DriveMotor

logging.basicConfig(level=logging.INFO)

#compass = Magnetometer(i2c_device="/dev/i2c-1", address=0x0C)

ntrip = NtripClient(caster="rtgpsout.unavco.org",
                user=os.getenv('NTRIP_USER'),
                password=os.getenv('NTRIP_PASSWORD'),
                mountpoint="SEAT_RTCM3")                        

# gps = GPS(serial_port="/dev/ttyACM0", ntrip_client=ntrip)

drive = DriveMotor(pwm_chip=2, pwm_line=0)

async def main():
    # await asyncio.gather(gps.run(), 
    #                      ntrip.run(),
    #                      compass.run())
    await asyncio.gather(drive._wear_in_motor())
    

asyncio.run(main())