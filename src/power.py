#!/usr/bin/python
#
# power.py  (replaces battery.py)
#
# monitor power and provides piJuice battery backup control
# provide up to 3 hours of UPS time for RPi only
#
# version 1.2  23Jul20  updated to V1.4 of PiJuice Firmware
#


import time
import json
from subprocess import call


import globalVars as gv
import config as c
import log
from pijuice import PiJuice


# module constants
OFF     = c.OFF
ON      = c.ON
UNK     = c.UNK
ERROR   = c.ERROR
NOERROR = c.NOERROR

AC_POWER = 0
BATTERY_POWER = 1

# Pre-defined LED Colors
LED_RED = [0xFF, 0x00, 0x00]
LED_GRN = [0x00, 0xFF, 0x00]
LED_BLU = [0x00, 0x00, 0xFF]
LED_WHT = [0xFF, 0xFF, 0xFF]
LED_OFF = [0x00, 0x00, 0x00]


# module globals
pj = PiJuice(c.PJ_BUS, c.PJ_ADDR)



def init():
    # assume we're starting on AC Power
    getFirmwareVersion()
  
    if (getPowerState() == BATTERY_POWER):
        log.log(log.CRITICAL, "Power Status indicates running on Battery")
        return ERROR

    log.log(log.ALWAYS, "pijuice init complete")

    # blink led twice  to show we're running
    pj.status.SetLedState('D2', LED_OFF)
    time.sleep(0.1)
    pj.status.SetLedBlink('D2', 10, LED_GRN, 500, LED_OFF, 500)

    gv.powerMode = AC_POWER
    return NOERROR



def resetFault():
    pj.status.ResetFaultFlags(['powerOffFlag', 'sysPowerOffFlag'])
    return


# call tbis periodically to check power status (1 - 15 seconds)
def checkPowerStatus():
    if (not gv.piJuicePresent):
        return UNK

    # on battery power?
    if (getPowerState() == BATTERY_POWER):
        # already shutdown?
        if (gv.powerStatus == AC_POWER):
            log.log(log.WARNING, "Power Failure Detected")
            lcd.setBrightness(128)
            lcd.setColor(0xFF, 0x00, 0x00)
            if (c.SHUTDOWN_ON_POWER_FAIL):
                equipment.shutdown()
                gv.systemMode = c.STANDBY
            gv.powerStatus = BATTERY_POWER
            return BATTERY_POWER
        else:
            log.log(log.WARNING, "Power Failure Detected")
            log.log(log.WARNING, "Battery at " + str(getChargeStatus()))
            return BATTERY_POWER
    else:
        # on AC
        if (gv.powerStatus == BATTERY_POWER):
            log.log(log.WARNING, "Power Restored")
            gv.powerStatus = AC_POWER
            lcd.setBrightness(255)
            lcd.setColor(0xFF, 0xFF, 0xFF)
            gv.systemMode = OFF
            return AC_POWER



def getPowerState():
    # Gets current state of power: AC or Battery
    status = pj.status.GetStatus()
    status = status['data'] if status['error'] == 'NO_ERROR' else status['error']
    log.log(log.ALWAYS, "powerInput: " + str(status['powerInput']))
    log.log(log.ALWAYS, "battery   : " + str(status['battery']))
    if (status['powerInput'] == 'NOT_PRESENT'):
        print("*** Warning: Battery NOT Charging ***")
        return BATTERY_POWER
    else:
        return AC_POWER



def getFirmwareVersion():
    try:
        # log firmware version
        fw = pj.config.GetFirmwareVersion()
        fw = str(fw['data']['version'])
        log.log(log.DEBUG, "pj firmware version " + fw)
        gv.pjfwVersion = fw
        return fw
    except:
        log.log(log.CRITICAL, "PiJuice Not Responding")
        return ERROR


def getChargeLevel():
    charge = pj.status.GetChargeLevel()
    charge = charge['data'] if charge['error'] == 'NO_ERROR' else charge['error']
    log.log(log.DEBUG, "Charge = " + str(charge) + " %")
    return charge


def getBatteryTemp():
    temp =  pj.status.GetBatteryTemperature()
    temp = temp['data'] if temp['error'] == 'NO_ERROR' else temp['error']
    log.log(log.DEBUG, "Temp = " + str(temp) + " degC")
    return temp


def getBatteryVoltage():
    vbat = pj.status.GetBatteryVoltage()
    vbat = vbat['data'] if vbat['error'] == 'NO_ERROR' else vbat['error']
    log.log(log.DEBUG, "Vbat = " + str(vbat / 1000.0) + " volts")
    return vbat / 1000.0;


def getBatteryCurrent():
    ibat = pj.status.GetBatteryCurrent()
    ibat = ibat['data'] if ibat['error'] == 'NO_ERROR' else ibat['error']
    log.log(log.DEBUG, "Ibat = " + str(ibat) + " milliamps")
    return ibat


def getBatteryIOVolts():
    vio =  pj.status.GetIoVoltage()
    vio = vio['data'] if vio['error'] == 'NO_ERROR' else vio['error']
    log.log(log.DEBUG, "Vio = " + str(vio/1000) + " volts")
    return vio/1000.0


def getBatteryIOCurrent():
    iio = pj.status.GetIoCurrent()
    iio = iio['data'] if iio['error'] == 'NO_ERROR' else iio['error']
    log.log(log.DEBUG, "Iio = " + str(iio) + " milliamps")
    return iio


def getBatteryTempSenseConfig():
    tsc = pj.config.GetBatteryTempSenseConfig()
    tsc = tsc['data'] if tsc['error'] == 'NO_ERROR' else tsc['error']
    log.log(log.DEBUG, "Temp Sense config = " + str(tsc))
    return str(tsc)


def shutdown():
    if (not gv.piJuicePresent):
        return

    print("*** Powering off in 10 seconds!!! ***")
    lcd.message("Power off in 10 sec!")
    log.log(log.CRITICAL, "initiating power shutdown")
    pj.power.SetPowerOff(10)
    call("sudo shutdown -h now", shell=True)
    return



def setWatchdog():
    return


def clearWatchdog():
    return


def getWatchdogStatus():
    return


# ----- main ------------------------------------------------
if __name__ == '__main__':

    log.init()
    if (init() == NOERROR):
        print("FW Version      = " + getFirmwareVersion())
        print("Charge Level    = " + str(getChargeLevel())      + "%")
        print("Battery Temp    = " + str(getBatteryTemp())      + " deg C")
        print("Battery Voltage = " + str(getBatteryVoltage())   + " volts")
        print("Battery Current = " + str(getBatteryCurrent())   + " ma")
        print("Battery IO V    = " + str(getBatteryIOVolts())   + " volts")
        print("Battery IO I    = " + str(getBatteryIOCurrent()) + " ma")
        print("Temp Config     = " + getBatteryTempSenseConfig())
        #shutdown()
        print("done")
    else:
        print("PiJuice not detected")
