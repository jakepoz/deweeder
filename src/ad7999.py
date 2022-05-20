import asyncio
import logging
from math import atan2, pi
import time
import numpy as np
import dataclasses
from bitstruct import pack, unpack
from periphery import GPIO, I2C

logger = logging.getLogger(__name__)

configure = lambda: [I2C.Message([0xF0])]
read_all_channels = lambda: [I2C.Message([0x00] * 8, read=True)] 
    

@dataclasses.dataclass
class AD7999Packet:
    bitpacking = "u2u2u12"

    status_reserved_0: int
    channel: int
    data: int

    def __str__(self) -> str:
        return f"ADC Ch{self.channel} = {self.data}"

class AD7999:
    def __init__(self, i2c_device="/dev/i2c-1", address=0x00, vref=5.0, ch_dividers={}) -> None:
        self.i2c = I2C(i2c_device)
        self.vref = vref
        self.ch_dividers = ch_dividers
        self.address = address
        self.channels = []
        
    async def setup(self):
        self.i2c.transfer(self.address, configure())

    async def run(self):
        while True:
            await asyncio.sleep(1.0)
            msgs = read_all_channels()
            self.i2c.transfer(self.address, msgs)
            
            self.channels = [
                AD7999Packet(*unpack(AD7999Packet.bitpacking, bytes(msgs[0].data)[0:2])),
                AD7999Packet(*unpack(AD7999Packet.bitpacking, bytes(msgs[0].data)[2:4])),
                AD7999Packet(*unpack(AD7999Packet.bitpacking, bytes(msgs[0].data)[4:6])),
                AD7999Packet(*unpack(AD7999Packet.bitpacking, bytes(msgs[0].data)[6:8])),
            ]
            
            print(self)
    
    def __getitem__(self, key):
        return self.channels[key].data / (2 ** 12) * self.vref / self.ch_dividers[key]

    def __str__(self) -> str:
        s = ""
        for i in range(len(self.channels)):
            s += f"Ch {i} = {self[i]:0.2f}v "
        
        return s


