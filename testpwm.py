#!/usr/bin/python
############################################################
#
# Test PWM outputs (on B+)
#
############################################################

import RPi.GPIO as GPIO
from bottle import route, run

# Speeds in m/s
groundSpeedRequested = 0.0
groudSpeedActual = 0.0

#Angular speeds in radians/s
yawSpeedRequested = 0.0
yawSpeedActual = 0.0

leftPwmPercent = 0.0
rightPwmPercent = 0.0

# v = K p
# - Simple linear relationship....
# p is precentage PWM
# This is the K value - assume top speed is 0.5 m/s
speedToPwmPercent = 0.5 / 100

#==================================================================

def setupPwm():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(32, GPIO.OUT) # Pin 32 on header (GPIO 12) is PWM0
    GPIO.setup(35, GPIO.OUT) # Pin 35 in header - GPIO 19 is PWM1
    global leftPwm = GPIO.PWM(32, 5000)
    global rightPwm = GPIO.PWM(35, 5000)
    leftPwm.start(0)
    rightPwm.start(0)
    
def teardownPwm()
    leftPwm.stop()
    rightPwm.stop()
    GPIO.cleanup()

def setLeftPwm(value):
    leftPwm.ChangeDutyCycle(value)

def setRightPwm(value):
    rightPwm.ChangeDutyCycle(value)

def stopPwm():
    setLeftPwm(0)
    setRightPwm(0)


#==================================================================


# Add 0.1 m/s - up to maximum
@route("/faster")
def faster():
    if leftPwmPercent < 1 and rightPwmPercent < 1:
        groundSpeedRequested = groundSpeedRequested + 0.1
        leftPwmPercent = rightPwmPercent = groundSpeedRequested / speedToPwmPercent
        setLeftPwm(leftPwmPercent)
        setRightPwm(rightPwmPercent)
        return groundSpeedRequested
    else:
        return  { "success" : False, "error" : "Already at top speed" }

@route("/stop")
def stop():
    stopPwm()
    return "OK"
    


#=================================================================

def testPwm():
    setupPwm()




    input('Press any key to stop:')
    teardownPwm()



#=================================================================
if __name__ == "__main__":


    run(host='localhost', port=8080)
