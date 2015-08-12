#!/usr/bin/python
############################################################
#
# Test PWM outputs (on B+)
#
############################################################

import os

import RPi.GPIO as GPIO
import pigpio
from bottle import route, run, static_file




class motorControlBase:
    def __init__(self):
        # Speeds in m/s
        self.groundSpeedRequested = 0.0
        self.groudSpeedActual = 0.0

        #Angular speeds in radians/s
        self.yawSpeedRequested = 0.0
        self.yawSpeedActual = 0.0

        self.leftPwmPercent = 0.0
        self.rightPwmPercent = 0.0

        # v = K p
        # - Simple linear relationship....
        # p is precentage PWM
        # This is the K value - assume top speed is 0.5 m/s
        self.speedToPwmPercent = 0.5 / 100
        self.setupPwm()

    def stopPwm(self):
        self.setLeftPwm(0)
        self.setRightPwm(0)

    def faster(self, steps = 0.1):
        if self.leftPwmPercent < 1 and self.rightPwmPercent < 1:
            self.groundSpeedRequested = self.groundSpeedRequested + steps
            self.leftPwmPercent = self.rightPwmPercent = self.groundSpeedRequested / self.speedToPwmPercent
            self.setLeftPwm(self.leftPwmPercent)
            self.setRightPwm(self.rightPwmPercent)
            return self.groundSpeedRequested
        else:
            raise Exception("Already at speed limit")

#==================================================================

class motorControlGpio(motorControlBase):
    def __init__(self):
        motorControlBase.__init__()

    def setupPwm(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(32, GPIO.OUT) # Pin 32 on header (GPIO 12) is PWM0
        GPIO.setup(35, GPIO.OUT) # Pin 35 in header - GPIO 19 is PWM1
        self.leftPwm = GPIO.PWM(32, 5000)
        self.rightPwm = GPIO.PWM(35, 5000)
        self.leftPwm.start(0)
        self.rightPwm.start(0)

    def teardownPwm(self):
        self.leftPwm.stop()
        self.rightPwm.stop()
        GPIO.cleanup()

    def setLeftPwm(self, value):
        self.leftPwm.ChangeDutyCycle(value)

    def setRightPwm(self, value):
        self.rightPwm.ChangeDutyCycle(value)

#==================================================================
class motorControlPig(motorControlBase):
    def __init__(self):
        super(motorControlPig, self).__init__()
        self.pig = pigpio.pi()

    def teardownPwm(self):
        setLeftPwm(0)
        setRightPwm(0)
        self.pig.stop()

    def setupPwm(self):
        setLeftPwm(0)
        setRightPwm(0)

    def setLeftPwm(self, value):
        value = value * 255 / 100
        self.pig.set_PWM_dutycycle(32, value)

    def setRightPwm(self, value):
        value = value * 255 / 100
        self.pig.set_PWM_dutycycle(35, value)


#==================================================================


# Add 0.1 m/s - up to maximum
@route("/faster")
def faster():
    try:
        ctl.faster()
    except:
        return  { "success" : False, "error" : "Already at top speed" }

@route("/stop")
def stop():
    ctl.stopPwm()
    return "OK"

@route("/")
def baseFile():
    localpath = os.path.realpath(__file__)
    return static_file('index.html', root=localpath, download='index.html')






#=================================================================
if __name__ == "__main__":
    ctl = motorControlPig()

    run(host="0.0.0.0", port=8080)
    ctl.teardownPwm()
