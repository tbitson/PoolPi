#!/usr/bin/python
#
#
#  1-wire temperature measurement thread
#  Since the DS18x20 device take approx 1 second
#  to make measurement, a separate thread is started
#  that continually measures the sensors a 5 second
#  intervals and puts the results in a global vars.
#  This reduces processor time to allow quick responces
#  to button presses and reduces heat.
#
#  version 1.1 - 21Jul20: read spa temp every 20
#  seconds rather than every 30 seconds
#
#
#



import time
import config as c
import globalVars as gv
from w1thermsensor import W1ThermSensor as owtemp
import log


# module constants
OFF     = c.OFF
ON      = c.ON
UNK     = c.UNK
ERROR   = c.ERROR
NOERROR = c.NOERROR

TEMP_ERROR = -99


#module globals
loop = True


def run():
    global loop

    # initialize sensors
    if (init() == NOERROR):

        # read all temps on start
        getSpaTemp()
        time.sleep(1)

        getAirTemp()
        time.sleep(1)

        getControllerTemp()
        time.sleep(1)

        count = 0
        # loop once a second, read temp every other loop
        while (loop == True):
            count += 1
            if (count == 10 or count == 30 or count == 50):
                getSpaTemp()

            elif (count == 20):
                getAirTemp()

            elif (count == 40):
                getControllerTemp()
                count = 0

            else:
                time.sleep(1)

            # if main loop ends, then end this thread
            if (gv.loop == False):
                loop = False

        # end of while loop
        log.log(log.CRITICAL, "owTempThread exiting")
        return


def stop():
    global loop
    loop = False
    return


def init():
    try:
        s = owtemp.get_available_sensors()
    except:
        log.log(log.ERROR, "1-wire get sensors Not Responding, check 1-wire bus")
        return ERROR

    numSensors = len(s)
    log.log(log.INFO, "Found " + str(numSensors) + " Sensors")

    if (numSensors < c.NUM_SENSORS):
        log.log(log.WARNING, "warning: Not All Temp Sensors Responding")

    # find correct sensor for each function
    for i in range(0, numSensors):
        log.log(log.INFO, "Found Sensor %s" % (s[i].id))

        if (s[i].id == c.SPA_TEMP_SENSOR_ID):
        	gv.sensors[0] = s[i]
        	gv.spaSensorEnabled = True

        elif (s[i].id == c.CONTROLLER_TEMP_SENSOR_ID):
        	gv.sensors[1] = s[i]
        	gv.cntrlSensorEnabled = True

        elif (s[i].id == c.AIR_TEMP_SENSOR_ID):
        	gv.sensors[2] = s[i]
        	gv.airSensorEnabled = True

        else:
            log.log(log.ERROR, "No Match for temp sensor - Check Config File. ID = "  + str(s[i].id))
            return ERROR


    for i in range(0, numSensors):
        log.log(log.ALWAYS, "Sensor %d id = %s matched to %s" % (i, str(gv.sensors[i].id), c.TEMP_SENSOR_NAMES[i]))

    log.log(log.ALWAYS, "Sensor Init Complete")
    gv.owInitComplete = True
    return NOERROR





def getSpaTemp():

    if(gv.spaSensorEnabled == False):
        return TEMP_ERROR

    temp  = readTempF(c.SPA_TEMP)
    log.log(log.INFO, "spa temp = " + str(round(temp, 1)))

    # check for errors
    if (temp == TEMP_ERROR):
        gv.owSpaErrors += 1

        # have we exceeded allowed number of errors?
        if (gv.owSpaErrors > c.ALLOWED_ERRORS):
            gv.spaSensorEnabled = False
            log.log(log.ERROR, "Spa 1-wire Errors > limit")
            return TEMP_ERROR

    gv.spaTemp = temp
    return temp



def getControllerTemp():

    if(gv.cntrlSensorEnabled == False):
        return TEMP_ERROR

    temp = readTempF(c.CONTROLLER_TEMP)
    log.log(log.INFO, "Controller temp = " + str(round(temp, 1)))

    # check for errors
    if (temp == TEMP_ERROR):
        gv.owCntrlErrors += 1

        # have we exceeded allowed number of errors?
        if (gv.owCntrlErrors > c.ALLOWED_ERRORS):
            gv.cntrlSensorEnabled = False
            log.log(log.ERROR, "Controller 1-wire Errors > limit")
            return TEMP_ERROR

    gv.controllerTemp = temp
    return temp



def getAirTemp():

    if(gv.airSensorEnabled == False):
        return TEMP_ERROR

    temp = readTempF(c.AIR_TEMP)
    log.log(log.INFO, "air temp = " + str(round(temp, 1)))

    # check for errors
    if (temp == TEMP_ERROR):
        gv.owAirErrors += 1

        # have we exceeded allowed number of errors?
        if (gv.owAirErrors > c.ALLOWED_ERRORS):
            gv.airSensorEnabled = False
            log.log(log.ERROR, "Air 1-wire Errors > limit")
            return TEMP_ERROR

    gv.airTemp = temp
    return temp



def readTempF(sensorID):

    try:
        temp = gv.sensors[sensorID].get_temperature(owtemp.DEGREES_F)
        # print("temp sensor %d = %f.1" % (sensorID, temp))
    except:
        return TEMP_ERROR

    return round(temp, 1)


#---------------------------------------------
if  __name__ == '__main__':

    DEBUG = True

    init()
    print
    print("Spa = ", getSpaTemp())
    print("Controller = ", getControllerTemp())
    print("Air = ", getAirTemp())
