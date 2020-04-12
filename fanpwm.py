#!/usr/bin/env python3
'''Script to control devices with pwm'''

import os
import sys
import time
import argparse

from numpy import interp


class PWMPin:
    '''udev rules have to be set so that it runs without sudo'''
    PWMCHIP_DIR = '/sys/class/pwm/pwmchip0'
    PIN2CHANNEL = {32: 0, 33: 1, 16: 3}  # on up2

    def __init__(self, pin: int=32, frequency: int=25000):
        self.pin = pin
        self.channel = self.PIN2CHANNEL[self.pin]
        self.frequency = frequency
        self.period = int(10**9 / frequency)  # in nanoseconds

    @property
    def gpio_sys_path(self):
        return os.path.join(self.PWMCHIP_DIR, f'pwm{self.channel}')

    def setup(self):
        export_file = os.path.join(self.PWMCHIP_DIR, 'export')
        os.system(f'echo {self.channel} > {export_file}')
        time.sleep(4)
        os.system(f'echo {self.period} > {self.gpio_sys_path}/period')
        self.set_duty_cycle(100)
        os.system(f'echo 1 > {self.gpio_sys_path}/enable')

    def _percent_to_duty_period(self, percentage):
        if percentage < 0 or percentage > 100:
            print('Percent must be in [0, 100]')
            return self.period  # 100% load

        return int(percentage / 100 * self.period)

    def set_duty_cycle(self, percent):
        '''percent must be from 0 to 100'''
        duty_period = self._percent_to_duty_period(percent)
        os.system(f'echo {duty_period} > {self.gpio_sys_path}/duty_cycle')

    def cleanup(self):
        os.system(f'echo 0 > {self.gpio_sys_path}/enable')
        time.sleep(1)
        unexport_file = os.path.join(self.PWMCHIP_DIR, 'unexport')
        os.system(f'echo {self.channel} > {unexport_file}')


class Control:
    REFRESH_TIME = 1  # seconds

    def __init__(self, pwm: PWMPin, t_range=(40, 60), pwm_range=(40, 100)):
        self.pwm = pwm
        self.t_range = t_range
        self.pwm_range = pwm_range

    def run(self):
        self.pwm.setup()
        try:
            while True:
                self.change_duty()
                time.sleep(self.REFRESH_TIME)
        except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
            sys.exit(0)
        finally:
            self.pwm.cleanup()

    def change_duty(self):
        cpu_temp = self.cpu_temp
        pwm_percentage = interp(cpu_temp, self.t_range, self.pwm_range)
        # print(f'CPU temp: {cpu_temp}, pwm percentage set to: {pwm_percentage}')
        self.pwm.set_duty_cycle(pwm_percentage)

    @property
    def cpu_temp(self, temperature_file='/sys/class/thermal/thermal_zone0/temp'):
        '''Get cpu temp from /sys'''
        with open(temperature_file, 'r') as fh:
            temperature = fh.read()
        return float(temperature) / 1000  # kernel outputs temp in millidegree Celsius


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('run', choices=['start', 'stop'])
    args = parser.parse_args()
    if args.run == 'start':
        start()
    else:
        stop()


def start():
    pwm = PWMPin()
    Control(pwm).run()


def stop():
    PWMPin().cleanup()


if __name__ == '__main__':
    main()
