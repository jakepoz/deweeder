import asyncio
import os
import logging

from .magnetometer import Magnetometer
from .gps import GPS
from .ntrip import NtripClient
from .drive_motor import DriveMotor
from .steer_motor import SteeringMotor
from .imu import IMU
from .heater import Heater
from .ad7999 import AD7999
from .web import webapp

from uvicorn import Config, Server

logging.basicConfig(level=logging.INFO)

compass = Magnetometer(i2c_device="/dev/i2c-1", address=0x1E)
imu = IMU(i2c_device="/dev/i2c-1", address=0x6A)
heater = Heater(gpio_chip="/dev/gpiochip4", gpio_line=13)
cell_volts = AD7999( i2c_device="/dev/i2c-1", address=0x29, vref=5.0, ch_dividers={
    0: 249 / (249 + 499),
    1: 249 / (249 + 249),
    2: 1000 / (1 + 1000),
    3: 40.2 / (162 + 40.2),
})

#gps = GPS(serial_port="/dev/ttyACM0")

#ntrip = NtripClient(caster="rtgpsout.unavco.org",
#                    user=os.getenv('NTRIP_USER'),
#                    password=os.getenv('NTRIP_PASSWORD'),
#                    mountpoint="SEAT_RTCM3",
#                    gps=gps)                        

drive = DriveMotor(pwm_chip=2, pwm_line=0)
steer = SteeringMotor(pwm_chip=0, pwm_line=0, gpio_enable_chip="/dev/gpiochip0", gpio_enable_line=8)

server = Server(config=Config(webapp, host='0.0.0.0', port=8000, loop="asyncio"))

async def robot_main(*modules):
    await asyncio.wait([module.setup() for module in modules], return_when=asyncio.ALL_COMPLETED)
    await asyncio.wait([module.run() for module in modules], return_when=asyncio.FIRST_EXCEPTION)

async def main():
    await asyncio.wait([robot_main(cell_volts), server.serve()], return_when=asyncio.FIRST_COMPLETED)

if __name__ == "__main__":
    asyncio.run(main())