#!/usr/bin/python
#
# webControl.py - interface to the pool equipment
# from web page controls
#
# version 2.0  24jul20
#
#
#
#


import os
import time
import datetime
import sys
import subprocess

import log
import config as c
import globalVars as gv
import timer
import equipment as equip
import owTemp as ow
import power


# module constants
OFF     = c.OFF
ON      = c.ON
UNK     = c.UNK
ERROR   = c.ERROR
NOERROR = c.NOERROR
UP      = 1.0
DOWN    = -1.0
TEMP_STEP = 1.0

VALVE_POOL_MODE  = 0  # CW, CW
VALVE_SPA_MODE   = 1  # CCW, CCW
VALVE_FILL_MODE  = 2  # CW, CCW
VALVE_DRAIN_MODE = 3  # CCW, CW



# --- WEB FUNCTIONS ------------------------

def tempControl(mode):
    if (mode == UP):
        log.log(log.ALWAYS, "web cmd: incTemp")
        if (gv.spaSetPoint < c.HEATER_MAX_TEMP):
            gv.spaSetPoint += TEMP_STEP
            log.log(log.ALWAYS, "spa setpoint = " + str(gv.spaSetPoint))

    elif (mode == DOWN):
        log.log(log.ALWAYS, "web cmd: decTemp")
        if (gv.spaSetPoint > c.HEATER_MIN_TEMP):
            gv.spaSetPoint -= TEMP_STEP
            log.log(log.ALWAYS, "spa setpoint = "+ str(gv.spaSetPoint))
    return



def timeAdjust(mode):
    if (mode == UP):
        timer.incSpaOffTime()
        log.log(log.ALWAYS, "web cmd: incTime")
    elif (mode == DOWN):
        log.log(log.ALWAYS, "web cmd: decTime")
    return



def pumpControl(mode):
    if (mode == ON):
        log.log(log.ALWAYS, "web cmd: pump on")
        equip.pumpOn(c.DEFAULT_DURATION)
    elif (mode == OFF):
        log.log(log.ALWAYS, "web cmd: pump off")
        equip.pumpOff()
    return


def spaControl(mode):
    if (mode == ON):
        log.log(log.ALWAYS, "web cmd: spa on")
        equip.spaOn(c.DEFAULT_DURATION)
    elif (mode == OFF):
        log.log(log.ALWAYS, "web cmd: spa off")
        equip.spaOff()
    return


def valveControl(mode):
    if (mode == VALVE_POOL_MODE):
        log.log(log.ALWAYS, "web cmd: valves pool")
        equip.valveControl(VALVE_POOL_MODE)
    elif (mode == VALVE_SPA_MODE):
        log.log(log.ALWAYS, "web cmd: valves spa")
        equip.valveControl(VALVE_SPA_MODE)
    elif (mode == VALVE_FILL_MODE):
        log.log(log.ALWAYS, "web cmd: valves spa")
        equip.valveControl(VALVE_FILL_MODE)
    elif (mode == VALVE_DRAIN_MODE):
        log.log(log.ALWAYS, "web cmd: valves spa")
        equip.valveControl(VALVE_DRAIN_MODE)
    return



def exit():
    log.log(log.ALWAYS, "web cmd: exit")
    # set flag so main loop dies on next loop
    gv.loop = False
    # how do i stop flask thread???
    return


def reboot():
    log.log(log.ALWAYS, "web cmd: reboot")
    equip.shutdown()
    sys.reboot()
    return


def powerOff():
    log.log(log.ALWAYS, "web cmd: poweroff")
    equip.shutdown()
    power.setPowerOff()
    # should never get here
    sys.exit()
    return


# --- helpers ------------------------------------------


def status2str(mode):
    if (mode == OFF):
        return "Off"
    elif (mode == ON):
        return "On"
    else:
        return "UNK"




def powerMode2str(mode):
    if (mode == c.AC_POWER):
        return "AC Power"
    elif (mode == c.BATTERY_POWER):
        return "Battery Power"
    else:
        return "Unknown"


#-------------------------------------------------

if __name__ == '__main__':

    print("webControl main")
    print("done")
