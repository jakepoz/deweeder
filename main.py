import time
from bitstruct import pack, unpack
from periphery import GPIO, I2C


i2c = I2C("/dev/i2c-1")
magnetometer_address = 0x0C

magnetometer_burst = "b1b1b1b1b1b1u2" + "s16" * 4


while True:
    # Start measurement
    msgs = [I2C.Message([0x3F]), I2C.Message([0x00], read=True)]
    i2c.transfer(magnetometer_address, msgs)
    time.sleep(0.2)

    # Read measurement
    msgs = [I2C.Message([0x4F]), I2C.Message([0x00] * 9, read=True)]
    i2c.transfer(magnetometer_address, msgs)
    burst_mode, woc_mode, sm_mode, error, single_error_detected, reset, d, t, x, y, z = unpack(magnetometer_burst, bytes(msgs[1].data))

    print(burst_mode, error, t, msgs[1].data[1], msgs[1].data[2])
    print(x, y, z)
    print("")


i2c.close()