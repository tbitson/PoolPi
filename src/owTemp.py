#!/usr/bin/python
#
#
#  1-wire temperature routines
#  one-wire support for DS18b20
#
#    version 1.4   11-02-18
#
#
#



import time
import config as c
import globalVars as gv
from w1thermsensor import W1ThermSensor as owtemp
import log
import equipment
import owTempThread
from threading import Thread



# module constants
OFF     = c.OFF
ON      = c.ON
UNK     = c.UNK
ERROR   = c.ERROR
NOERROR = c.NOERROR

TEMP_ERROR = -99


#module globals
lastHeaterOffTime = 0
thread = Thread()



def init():
    # init temps to ambient
    gv.spaTemp = 70
    gv.controllerTemp = 70
    gv.airTemp = 70
    return


def start():
    global thread

    log.log(log.ALWAYS,"starting OW temp thread")
    thread = Thread(target=owTempThread.run)
    thread.start()
    return


def stop():
    global thread
    thread.stop()


def getSpaTemp():
    return gv.spaTemp


def getAirTemp():
    return gv.airTemp


def getControllerTemp():
    return gv.controllerTemp


def getDeviceID(i):
    if (i >= 0 and i < 3):
        return str(gv.sensors[i].id)
    else:
        return ("invalid getDeviceID() index")


def isThreadRunning():
    global thread
    return thread.isAlive()


def checkForFreeze():
    # already in freeze mode?
    if (gv.systemMode == c.FREEZE):
        return

    # if its freezing, turn on pump for an hour then check again
    # should I use both air and water temp??
    #if (getAirTemp() < c.FREEZE_TEMP and getSpaTemp() < 38):
    if (getAirTemp() < c.FREEZE_TEMP):
        log.log(log.CRITICAL, "Freeze detected at air: %f  spa: %f" % (getAirTemp(), getSpaTemp()))
        equipment.pumpOn(1)
        gv.systemMode = c.FREEZE
    return



def thermostat():
    global lastHeaterOffTime

    secs = int(time.mktime(time.localtime()))
    temp = getSpaTemp()

    # is spa on?
    if (gv.systemMode == c.SPA_ON):
        # check for sensor error
        if (gv.spaSensorEnabled == False):
            equipment.spaOff()
            log.log(log.ERROR, "Spa Temp Sensor not detected")
            return ERROR

        # check for over temp
        if (temp > c.HEATER_MAX_TEMP):
            equipment.heaterEnable(OFF)
            equipment.heaterPower(OFF)
            log.log(log.ERROR, "ERROR: Spa over max temp: " + str(temp))
            return ERROR

        else:
            log.log(log.INFO, "Spa Temp  = " + str(temp))

            if (temp > gv.spaSetPoint):
                if (gv.heatEnable == ON):
                    log.log(log.ALWAYS, "Spa at temp, turning off heat at " + str(temp))
                    equipment.heaterEnable(OFF)
                    lastHeaterOffTime = secs

            elif (temp < (gv.spaSetPoint - c.HEATER_DELTA_TEMP)):
                if (gv.heatEnable == OFF):
                    # check for minimum heater off time
                    if ((secs - lastHeaterOffTime) < c.HEATER_LOCKOUT_TIME):
                        log.log(log.ALWAYS, "heater lockout: %i remaining" % (c.HEATER_LOCKOUT_TIME - (secs - lastHeaterOffTime)))
                        return NOERROR
                    log.log(log.ALWAYS, "Spa less than setpoint, turning on heat at " + str(temp))
                    equipment.heaterEnable(ON)
                return NOERROR
    else:
        return NOERR



def resetErrors():
    gv.owAirErrors   = 0
    gv.owCntrlErrors = 0
    gv.owAirErrors   = 0
    gv.spaSensorEnabled  = True
    gv.airSensorEnabled   = True
    gv.cntrlSensorEnabled = True

    log.log(log.INFO, "1-wire errors cleared")
    return

#---------------------------------------------
if  __name__ == '__main__':

    DEBUG = True

    init()
    print
    print("Spa = ", getSpaTemp())
    print("Controller = ", getControllerTemp())
    print("Air = ", getAirTemp())
