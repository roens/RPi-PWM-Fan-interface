#!/usr/bin/python
#
# Bit & pieces borrowed from:
#   https://github.com/cyoung/stratux/blob/d4ed2d1b0cba2172c702e82ab3b40516db2a792d/image/fancontrol.py
#   https://github.com/lanefu/WiringPi-Python-OP/blob/master/examples/softpwm.py
#
# Uses softPwm to drive fan at GPIO.1 based on SOC temperature.
#
#
# Requires:
#   https://github.com/lanefu/WiringPi-Python-OP/
#
# I also found the default Armbian kernel needed to be replaced with one built
# for the particular board I'm using:
#   Orange Pi Plus (H3, 1GB RAM, 8GB eMMC, WiFi)
#   https://docs.armbian.com/Developer-Guide_Using-Vagrant/

import wiringpi
import time
import os

from daemon import runner

OUTPUT = 1
PIN_TO_PWM = 1

class FanControl():
    # Return CPU temperature as float
    def getCPUtemp(self):
#       cTemp = os.popen('vcgencmd measure_temp').readline()
        cTemp = os.popen('cat /etc/armbianmonitor/datasources/soctemp').readline()
        return float(cTemp.replace("temp=","").replace("'C\n",""))

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/fancontrol.log'
        self.stderr_path = '/var/log/fancontrol.log'
        self.pidfile_path = '/var/run/fancontrol.pid'
        self.pidfile_timeout = 5
    def run(self):
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(PIN_TO_PWM,OUTPUT)

        # Setup PWM using: pin, initial value, and range
        wiringpi.softPwmCreate(PIN_TO_PWM,0,100)

        # Set fan full speed then stop
        wiringpi.softPwmWrite(PIN_TO_PWM,100)
        wiringpi.softPwmWrite(PIN_TO_PWM,0)

        while True:
            CPU_temp = self.getCPUtemp()
            if CPU_temp > 40:
                wiringpi.softPwmWrite(PIN_TO_PWM,100)
            elif CPU_temp > 35:
                wiringpi.softPwmWrite(PIN_TO_PWM,70)
            elif CPU_temp > 28:
                wiringpi.softPwmWrite(PIN_TO_PWM,33)
            elif CPU_temp < 27:
                wiringpi.softPwmWrite(PIN_TO_PWM,0)
            time.sleep(5)

# Fan starts at 30%
# lowest quiet  33%
#               50%
#               70%
#               80%
#              100%

fancontrol = FanControl()
daemon_runner = runner.DaemonRunner(fancontrol)
daemon_runner.do_action()
