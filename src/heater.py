import asyncio
import logging
from math import atan2, pi
import time
import numpy as np
import dataclasses
from bitstruct import pack, unpack
from periphery import GPIO, I2C

logger = logging.getLogger(__name__)


    

class Heater:
    def __init__(self, gpio_chip="/dev/gpiochip4", gpio_line=13) -> None:
        self.gpio = GPIO(gpio_chip, gpio_line, "out")

    async def setup(self):
        self.gpio.write(False)

    async def run(self):
        while True:
            await asyncio.sleep(2.0)
            self.gpio.write(False)
            await asyncio.sleep(2.0)
            self.gpio.write(True)


