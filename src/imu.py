import asyncio
import logging
from math import atan2, pi
import time
import numpy as np
import dataclasses
from bitstruct import pack, unpack
from periphery import GPIO, I2C

logger = logging.getLogger(__name__)


    

class IMU:
    def __init__(self, i2c_device="/dev/i2c-1", address=0x0C) -> None:
        self.i2c = I2C(i2c_device)
        self.address = address
        
    def setup(self):
        pass


    async def run(self):
        while True:
            await asyncio.sleep(1.0)


