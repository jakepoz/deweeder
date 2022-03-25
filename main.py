import time
import dataclasses
from bitstruct import pack, unpack
from periphery import GPIO, I2C


i2c = I2C("/dev/i2c-1")
magnetometer_address = 0x0C

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




while True:
    # Start measurement
    msgs = [I2C.Message([0x3F]), I2C.Message([0x00], read=True)]
    i2c.transfer(magnetometer_address, msgs)
    time.sleep(0.2)

    # Read measurement
    msgs = [I2C.Message([0x4F]), I2C.Message([0x00] * 9, read=True)]
    i2c.transfer(magnetometer_address, msgs)
    reading = MagnetometerReading(*unpack(MagnetometerReading.bitpacking, bytes(msgs[1].data)))
    # burst_mode, woc_mode, sm_mode, error, single_error_detected, reset, d, t, x, y, z = unpack(magnetometer_burst, bytes(msgs[1].data))

    # print(burst_mode, error, t, msgs[1].data[1], msgs[1].data[2])
    # print(x, y, z)
    # print("")
    print(reading.temp_c)


i2c.close()