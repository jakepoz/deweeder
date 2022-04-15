import asyncio
import os
import logging

from .magnetometer import Magnetometer
from .gps import GPS
from .ntrip import NtripClient
from .drive_motor import DriveMotor
from .web import webapp

from uvicorn import Config, Server

logging.basicConfig(level=logging.INFO)


#compass = Magnetometer(i2c_device="/dev/i2c-1", address=0x0C)

gps = GPS(serial_port="/dev/ttyACM0")

ntrip = NtripClient(caster="rtgpsout.unavco.org",
                    user=os.getenv('NTRIP_USER'),
                    password=os.getenv('NTRIP_PASSWORD'),
                    mountpoint="SEAT_RTCM3",
                    gps=gps)                        

drive = DriveMotor(pwm_chip=2, pwm_line=0)

server = Server(config=Config(webapp, host='0.0.0.0', port=8000, loop="asyncio"))

async def robot_main(*modules):
    await asyncio.wait([module.setup() for module in modules], return_when=asyncio.ALL_COMPLETED)
    await asyncio.wait([module.run() for module in modules], return_when=asyncio.FIRST_EXCEPTION)

async def main():
    await asyncio.wait([robot_main(ntrip, gps), server.serve()], return_when=asyncio.FIRST_COMPLETED)

if __name__ == "__main__":
    asyncio.run(main())