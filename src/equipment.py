#!/usr/bin/python
#
# equipment.py
#
# This version uses gpiozero instead of wiringpi. Any references
# to wiring pi should be assumed to mean gpiozero.
#
# equipment interface module for poolPi
# controls the pool equipment through GPIO
# via gpiozero.
#
# As of version 1.6, the controller box fan is controlled
# by the system (overlay) and is removed from this code
#
#
# version 1.6 threaded  13June2020
#
#   Quick Ref:
#   GPIO   Function
#     22   Pump Power Relay
#     27   Heater Power Relay
#     23   Heat Enable DIN "heat on" relay 1
#     17   Valve Motor 1 Direction
#     24   Valve Motor 2 Direction
#     16   spare
#     20   activity led, return to GPIO 8
#
#

import sys
import time

import gpiozero as gz
import log
import config
import globalVars as gv
import timer
import lcd
#import menu
import owTemp as ow
from threading import Thread



# module constants
OFF     = 0
ON      = 1
UNK     = -1
ERROR   = 1
NOERROR = 0
CCW     = 1
CW      = 0


# suction valve (in), return valve (out)
VALVE_POOL_MODE  = 0  # CW, CW
VALVE_SPA_MODE   = 1  # CCW, CCW
VALVE_FILL_MODE  = 2  # CW, CCW
VALVE_DRAIN_MODE = 3  # CCW, CW
VALVE_UNK_MODE   = 4  # position not yet known


# module globals
global pumpPowerIO, heaterPowerIO, heaterEnableIO, valve1DirIO, valve2DirIO
global sparePowerIO, activityLedIO, activityLedRtnIO

pumpPowerIO      = 0
heaterPowerIO    = 0
heaterEnableIO   = 0
valve1DirIO      = 0
valve2DirIO      = 0
sparePowerIO     = 0
activityLedIO    = 0
activityLedRtnIO = 0



def init():
    global pumpPowerIO, heaterPowerIO, heaterEnableIO, valve1DirIO, valve2DirIO
    global sparePowerIO, activityLedIO, activityLedRtnIO

    try:
        # set up I/O pins
        pumpPowerIO      = gz.DigitalOutputDevice(config.PUMP_PIN,        active_high = True, initial_value = False)
        heaterPowerIO    = gz.DigitalOutputDevice(config.HEATER_PIN,      active_high = True, initial_value = False)
        heaterEnableIO   = gz.DigitalOutputDevice(config.HEATER_EN_PIN,   active_high = True, initial_value = False)
        valve1DirIO      = gz.DigitalOutputDevice(config.VALVE1_DIR_PIN,  active_high = True, initial_value = False)
        valve2DirIO      = gz.DigitalOutputDevice(config.VALVE2_DIR_PIN,  active_high = True, initial_value = False)
        sparePowerIO     = gz.DigitalOutputDevice(config.SPARE_PIN,       active_high = True, initial_value = False)
        activityLedIO    = gz.DigitalOutputDevice(config.LED_PIN,         active_high = True, initial_value = False)
        activityLedRtnIO = gz.DigitalOutputDevice(config.LED_RTN_PIN,     active_high = True, initial_value = False)

        # ensure all are off
        pumpPowerIO.off()
        heaterPowerIO.off()
        heaterEnableIO.off()
        valve1DirIO.off()
        valve2DirIO.off()
        sparePowerIO.off()
        activityLedIO.off()
        activityLedRtnIO.off()

    except:
        log.log(log.ERROR, "Error initializing equipment")
        return ERROR

    # initialize project globals
    gv.pumpPower      = OFF
    gv.heatPower      = OFF
    gv.heatEnable     = OFF
    gv.valveMode      = VALVE_POOL_MODE
    gv.sparePower     = OFF

    log.log(log.ALWAYS, "Equipment init complete")
    return NOERROR



def toggleLED():
    global activityLedIO
    # set activity led to opposite of its current state
    activityLedIO.value = not activityLedIO.value
    return



def spaOn(hours):
    lcd.message("Turning on Spa... ")
    log.log(log.ALWAYS, "SpaOn called with hours = " + str(hours))
    time.sleep(1)

    pumpPower(ON)
    lcd.message("Pump On")
    time.sleep(1)

    heaterPower(ON)
    lcd.message("Heater On")
    time.sleep(1)

    valveControl(VALVE_SPA_MODE)

    heaterEnable(ON)

    gv.systemMode = config.SPA_ON
    timer.setSpaOffEvent(hours)
    log.log(log.ALWAYS, "*** Spa on ***")
    return



def spaOff():
    lcd.message("Turning Off Spa... ")
    log.log(log.ALWAYS, "Turning Spa Off ")

    heaterEnable(OFF)
    heaterPower(OFF)

    timer.setPumpOffEvent(0, 15)
    gv.systemMode = config.COOLDOWN
    gv.lastSpaOnTime = 0
    timer.setTimeRemaining(15)

    valveControl(VALVE_POOL_MODE)
    log.log(log.ALWAYS, "*** Starting Cooldown ***")
    return



def pumpOn(hours):
    lcd.message("Turning on Pump... ")
    pumpPower(ON)
    timer.setPumpOffEvent(hours, 0)
    gv.systemMode = config.MANUAL
    return



def pumpOff():
    lcd.message("Turning Off Pump... ")
    pumpPower(OFF)
    gv.systemMode = config.OFF
    timer.clearPumpOffEvent()
    return



def pumpPower(mode):
    global pumpPowerIO

    log.log(log.ALWAYS, "pumpPower() called with " + mode2str(mode))

    # already on?
    if (mode == gv.pumpPower):
        return

    if (mode == ON):
        pumpPowerIO.on()
        log.log(log.ALWAYS, "*** pump on ***")
        gv.pumpPower = ON
        gv.systemMode = config.PUMP_ON
        return NOERROR

    elif (mode == OFF):
        # todo: only do this if user pushes button
        if (gv.heatPower == ON):
            log.log(log.WARNING, "Turning off Pump with Heater ON!")
            lcd.message("WARNING", "Turning off Pump with Heater ON!")

        if (gv.systemMode == config.MANUAL or gv.systemMode == config.COOLDOWN):
            log.log(log.WARNING, "Heater may not have cooled down yet!")
            lcd.message("WARNING", "Heater may not have cooled down yet!")

        heaterEnable(OFF)
        heaterPower(OFF)
        pumpPowerIO.off()
        log.log(log.ALWAYS, "*** pump off ***")
        gv.pumpPower = OFF
        gv.systemMode = config.SYS_OFF
        return NOERROR
    else:
       log.log(log.ERROR, "pumpPower was passed invalid value: ", str(mode))
    return ERROR



def heaterPower(mode):
    global heaterPowerIO

    log.log(log.ALWAYS, "heaterPower() called with " + mode2str(mode))

    if (mode == gv.heatPower):
        return NOERROR

    if (mode == ON):
        if (gv.pumpPower) == OFF:
            log.log(log.ERROR, "attempting to turn on heater with pump off!")
            lcd.message("ERROR", "Can't turn on heat with Pump off")
            return ERROR

        else:
            heaterPowerIO.on()
            time.sleep(1)
            gv.heatPower = ON
            log.log(log.ALWAYS, "*** Heater power on ***")
            gv.systemMode = config.SPA_ON
            return NOERROR

    elif (mode == OFF):
        heaterPowerIO.off()
        log.log(log.ALWAYS, "*** Heater power off ***")
        gv.heatPower = OFF;
        gv.systemMode = config.COOLDOWN
        return NOERROR

    else:
        log.log(log.ERROR, "heaterPower was passed invalid value: ", (mode))
        return ERROR




def heaterEnable(mode):
    global heaterEnableIO

    log.log(log.ALWAYS, "heaterEnable() called with " + mode2str(mode))

    if (mode == ON):
        if (gv.pumpPower == OFF):
            log.log(log.ERROR, "attempting to Enable heater with pump off!")
            return ERROR
        if (gv.heatPower == OFF):
            log.log(log.ERROR, "attempting to Enable heater with heater Power off")
            return ERROR

        heaterEnableIO.on()
        gv.heatEnable = ON
        log.log(log.ALWAYS, "*** Heater Enable on ***")
        return NOERROR

    elif (mode == OFF):
        heaterEnableIO.off()
        log.log(log.ALWAYS, "*** Heater Enable off ***")
        gv.heatEnable = OFF;
        return NOERROR

    else:
        log.log(log.ERROR, "heaterPower was passed invalid value: ", str(mode))
        return ERROR




def valveControl(mode):
    global valve1DirIO
    global valve2DirIO

    if (mode == VALVE_POOL_MODE):
        valve1DirIO.off()
        valve2DirIO.off()
        log.log(log.ALWAYS, "*** valves set to POOL mode ***")
        gv.valveMode = mode
        return

    elif (mode == VALVE_SPA_MODE):
        valve1DirIO.on()
        valve2DirIO.on()
        log.log(log.ALWAYS, "*** valves set to SPA mode ***")
        gv.valveMode = mode
        return


    elif (mode == VALVE_FILL_MODE):
        valve1DirIO.off()
        valve2DirIO.on()
        log.log(log.ALWAYS, "*** valves set to FILL mode ***")
        gv.valveMode = mode
        return

    elif (mode == VALVE_DRAIN_MODE):
        valve1DirIO.on()
        valve2DirIO.off()
        log.log(log.ALWAYS, "*** valves set to DRAIN mode ***")
        gv.valveMode = mode
        return

    else:
        log.log(log.ERROR, "Unknown/invalid valve command")
        gv.valveMode = -1

    return





def spareRelay(mode):
    global spareRelayIO

    if (mode == ON):
        sparePowerIO.on()
        log.log(log.ALWAYS, "*** spare on ***")
        gv.spareRelay = ON
        return NOERROR

    elif (mode == OFF):
        sparePowerIO.off()
        log.log(log.ALWAYS, "*** spare off ***")
        gv.spareRelay = OFF
        return NOERROR

    else:
        log.log(log.ERROR, "spare() was passed invalid value: ", str(mode))
        return ERROR





def shutdown():
    global pumpPowerIO, heaterPowerIO, heaterEnableIO, sparePowerIO, valve1DirIO, valve2DirIO

    # turn off everything
    log.log(log.ALWAYS, "Shutting Down")

    # ensure everything is off
    # don't use routines as a safety precaution
    pumpPowerIO.off()
    heaterPowerIO.off()
    heaterEnableIO.off()
    valve1DirIO.off()
    valve2DirIO.off()
    sparePowerIO.off()

    try:
        lcd.message("    System Off")
        lcd.setColor(0, 0, 255)
        lcd.closePort()

    except:
        print(sys.exc_info())
        log.log(log.ERROR, "error in lcd during shutdown - ignoring");

    log.log(log.ALWAYS, "Shutdown Complete")
    print("Equipment Off")
    return


# ----------- helper functions ----------------------------


def mode2str(mode):
    if (mode):
        return "On"
    else:
        return "Off"



#### convert to read dio for status
def getValveStatus():
    if (gv.valveMode == VALVE_POOL_MODE):
        return "Pool Mode"
    elif (gv.valveMode == VALVE_SPA_MODE):
        return "Spa Mode"
    elif (gv.valveMode == VALVE_FILL_MODE):
        return "Fill Mode"
    elif (gv.valveMode == VALVE_DRAIN_MODE):
        return "Drain Mode"
    else:
        return "unknown"



#---------------------------------------------------------------------------


if __name__ == '__main__':

    log.init()
    lcd.init()
    init()
    shutdown()
