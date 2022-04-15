import asyncio
import os
import signal
import logging
from typing import Optional

from .magnetometer import Magnetometer
from .gps import GPS
from .ntrip import NtripClient
from .drive_motor import DriveMotor


from uvicorn import Config, Server
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

logging.basicConfig(level=logging.INFO)


#compass = Magnetometer(i2c_device="/dev/i2c-1", address=0x0C)

ntrip = NtripClient(caster="rtgpsout.unavco.org",
                user=os.getenv('NTRIP_USER'),
                password=os.getenv('NTRIP_PASSWORD'),
                mountpoint="SEAT_RTCM3")                        

gps = GPS(serial_port="/dev/ttyACM0", ntrip_client=ntrip)

drive = DriveMotor(pwm_chip=2, pwm_line=0)


async def homepage(request):
    return JSONResponse({'hello': 'world'})


async def robot_main():
    await asyncio.gather(gps.run(), 
                         ntrip.run())
                        # compass.run())

app = Starlette(debug=True, routes=[
    Route('/', homepage),
])
server = Server(config=Config(app, host='0.0.0.0', port=8000, loop="asyncio" ))

async def main():
    await asyncio.wait([robot_main(), server.serve()], return_when=asyncio.FIRST_COMPLETED)

if __name__ == "__main__":
    asyncio.run(main())