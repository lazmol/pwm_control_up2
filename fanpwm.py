#!/usr/bin/env python3

import os
import time
from numpy import interp

    
class PWMPin:
    '''udev rules have to be set so that it runs without sudo'''
    PIN2SYS = {32: '/sys/class/pwm/pwmchip0/pwm0'}
    def __init__(self, pin: int=32, frequency: int=25000):
        self.pin = pin
        self.frequency = frequency
        self.period = 10**9 / frequency  # in nanoseconds
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

    def _percent_to_duty_period(self, percentage)
        if percent < 0 or percent > 100:
            print('Percent must be in [0, 100]')
            return self.period  # 100% load
        
        return percentage / 100 * self.period
        
    def set_duty_cycle(self, percent):
        '''percent must be from 0 to 100'''
        duty_period = self._percent_to_duty_period(percent)
        os.system(f'echo {duty_period} > {self.gpio_sys_path}/duty_cycle')

        
class Control:
    REFRESH_TIME = 2  # seconds
    def __init__(self, pwm: PWMPin, t_range=(40, 70), pwm_range=(10, 100)):
        self.pwm = pwm
	self.t_range = t_range
	self.pwm_range = pwm_range
        self.cpu_temp = cpu_temp()
    
    def run(self):
        try:
            while True:
		self.change_duty()
		time.sleep(self.REFRESH_TIME)
        except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt 
            sys.exit(0)
            
    def change_duty(self):
        self.cpu_temp = cpu_temp()
	pwm_percentage = interp(self.cpu_temp, self.t_range, self.pwm_range)
	self.pwm.set_duty_cycle(pwm_percentage)
        
    @property
    def cpu_temp(temp_file='/sys/class/thermal/thermal_zone0/temp'):
        '''Get cpu temp from /sys'''
        with open(temp_file) as fh:
            temperature = fh.readline()
        return float(temperature)

def main():
    pwm = PWMPin()
    Control(pwm).run()


if __name__ == '__main__':
    main()
