import asyncio
import logging
import numpy as np
import random

from periphery import PWM, GPIO


logger = logging.getLogger(__name__)

PWM_PERIOD = 1/50.0 #20 ms
PWM_ZERO = .0015
PWM_MIN = .0010
PWM_MAX = .0020

class SteeringMotor:
    def __init__(self, pwm_chip=0, pwm_line=0, gpio_enable_chip="/dev/gpiochip0", gpio_enable_line=0) -> None:
        self.pwm_chip = pwm_chip
        self.pwm_line = pwm_line
        self.pwm = PWM(pwm_chip, pwm_line)
        self.gpio_enable = GPIO(gpio_enable_chip, gpio_enable_line, "out")

    async def setup(self):
       self.pwm.frequency = 1 / PWM_PERIOD
       self.pwm.duty_cycle = PWM_ZERO / PWM_PERIOD
       self.pwm.enable()

       self.gpio_enable.write(True)

    async def run(self):
        while True:
            await asyncio.sleep(1)
            target_duty = random.uniform(PWM_MIN / PWM_PERIOD, PWM_MAX / PWM_PERIOD)
            self.pwm.duty_cycle = target_duty
