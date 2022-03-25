import time
from periphery import GPIO, I2C


i2c = I2C("/dev/i2c-1")
magnetometer_address = 0x0C


while True:
    # Start measurement
    msgs = [I2C.Message([0x3F]), I2C.Message([0x00], read=True)]
    i2c.transfer(magnetometer_address, msgs)
    time.sleep(0.2)

    # Read measurement
    msgs = [I2C.Message([0x4F]), I2C.Message([0x00] * 9, read=True)]
    i2c.transfer(magnetometer_address, msgs)
    print(msgs[1].data)


i2c.close()