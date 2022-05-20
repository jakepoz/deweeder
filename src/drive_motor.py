import asyncio
import logging
import numpy as np
import random

from periphery import PWM


logger = logging.getLogger(__name__)

PWM_PERIOD = 1/50.0 #20 ms
PWM_ZERO = .0015
PWM_MIN = .0010
PWM_MAX = .0020

class DriveMotor:
    def __init__(self, pwm_chip=0, pwm_line=0) -> None:
        self.pwm_chip = pwm_chip
        self.pwm_line = pwm_line
        self.pwm = PWM(pwm_chip, pwm_line)

    async def setup(self):
       self.pwm.frequency = 1 / PWM_PERIOD
       self.pwm.duty_cycle = PWM_ZERO / PWM_PERIOD
       self.pwm.enable()

    async def _calibrate(self):
        logger.warning("Starting ESC calibration process, enabling neutral PWM signal")
        logger.warning("Press power key continously")
        input("press enter")

        logger.warning("Press power key to set neutral")
        input("press enter")

        logger.warning("Press power key to set forward position")
        self.pwm.duty_cycle = PWM_MAX / PWM_PERIOD
        input("press enter")

        logger.warning("Press power key to set backward position")
        self.pwm.duty_cycle = PWM_MIN / PWM_PERIOD
        input("press enter")

        self.pwm.duty_cycle = PWM_ZERO / PWM_PERIOD
        self.pwm.disable()

    async def _wear_in_motor(self):
        new_duty = PWM_ZERO / PWM_PERIOD
        self.pwm.duty_cycle = new_duty  
        await asyncio.sleep(1)

        while True:
            target_duty = random.uniform(PWM_MIN / PWM_PERIOD, PWM_MAX / PWM_PERIOD)

            for i in range(400):
                new_duty = new_duty + 0.03 * (target_duty - new_duty)
                print(f"New duty cycle {new_duty}")
                self.pwm.duty_cycle = new_duty
                await asyncio.sleep(0.02)
    