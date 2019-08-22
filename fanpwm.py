#!/usr/bin/env python3

import os
import time


def cpu_temp(temp_file='/sys/class/thermal/thermal_zone0/temp'):
    '''Get cpu temp from /sys'''
    with open(temp_file) as fh:
        temperature = fh.readline()
        
    return float(temperature)
    

class PWMPin:
    PIN2SYS = {2: '/sys/class/pwm/pwmchip0/pwm0'}
    def __init__(self, pin: int=32, frequency: int=25000):
        self.pin = pin
        self.frequency = frequency
        self.period = 1 / frequency
        self.setup()

    @property
    def gpio_sys_path(self):
        return self.PIN2SYS[self.pin]

    def setup(self):
        chip_dir = os.path.dirname(self.gpio_sys_path)  # export is one dir up
        os.system(f'echo 0 > {chip_dir}/export')
        time.sleep(4)
        os.system(f'echo {self.period} > {self.gpio_sys_path}/period')
        self.set_duty_cycle(100)
        os.system(f'echo 1 > {self.gpio_sys_path}/enable')

    def _percent_to_duty_cycle(self, percentage)
        if percent < 0 or percent > 100:
            print('Percent must be in [0, 100]')
            return self.period  # 100% load
        
        return percentage / 100 * self.period
        
    def set_duty_cycle(self, percent):
        '''percent must be from 0 to 100'''
        duty_period = self._percent_to_duty_cycle(percent)
        os.system(f'echo {duty_period} > {self.gpio_sys_path}/duty_cycle')
