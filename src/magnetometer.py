import asyncio
import logging
from math import atan2, pi
import time
import numpy as np
import dataclasses
from bitstruct import pack, unpack
from periphery import GPIO, I2C

logger = logging.getLogger(__name__)

reset = lambda: [I2C.Message([0xFF]), I2C.Message([0x00], read=True)]
start_burst_mode = lambda: [I2C.Message([0x1F]), I2C.Message([0x00], read=True)]
stop_burst_mode =  lambda: [I2C.Message([0x80]), I2C.Message([0x00], read=True)]
start_measurement =  lambda: [I2C.Message([0x3F]), I2C.Message([0x00], read=True)]
read_measurement = lambda: [I2C.Message([0x4F]), I2C.Message([0x00] * 9, read=True)]
write_register = lambda addr, val: [I2C.Message([0b01100000, (val >> 8) & 0xFF, val & 0xFF, addr << 2]), I2C.Message([0x00], read=True)]

@dataclasses.dataclass
class MagnetometerStatus:
    bitpacking = "b1b1b1b1b1b1u2"

    burst_mode: bool
    woc_mode: bool
    sm_mode: bool
    error: bool
    single_error_detected: bool
    reset: bool
    data_bytes: int

@dataclasses.dataclass
class MagnetometerReading(MagnetometerStatus):
    bitpacking = "b1b1b1b1b1b1u2u16s16s16s16"

    raw_t: int
    raw_x: int
    raw_y: int
    raw_z: int

    @property
    # Return temperature in degrees C
    def temp_c(self):
        #45.2 LSB per deg C
        #46244 LSB at 25C
        return (self.raw_t - 46244) / 45.2 + 25

    @property
    # Return reading in microTesla
    def vec(self):
        # Hallconf = 0xC by default
        # setup() sets the max OSR and DIG_FILT values
        return np.array((self.raw_x / .751,
                self.raw_y / .751,
                self.raw_z / 1.210))

    @property
    def heading(self):
        head = atan2(self.vec[1], self.vec[0]) * 180 / pi

        return head
    

class Magnetometer:
    def __init__(self, i2c_device="/dev/i2c-1", address=0x0C) -> None:
        self.i2c = I2C(i2c_device)
        self.address = address

        
    async def setup(self):
        # reset
        self.i2c.transfer(self.address, reset())
        time.sleep(0.25)

        # Set max digital filtering and oversampling,  expect 200ms per reading
        self.i2c.transfer(self.address, write_register(0x02, 0b0000000000011111))



    async def run(self):
        while True:
            self.i2c.transfer(self.address, start_measurement())
            await asyncio.sleep(1.0)

            # Read measurement
            msgs = read_measurement()
            self.i2c.transfer(self.address, msgs)
            reading = MagnetometerReading(*unpack(MagnetometerReading.bitpacking, bytes(msgs[1].data)))

            logger.info(reading)


