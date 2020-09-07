#!/usr/bin/python
#
# timer.py
# timing and event module for poolPi
# sets power & spa on and off events and
# provides an interface to check if an
# event time is reached
#
#
#

# VERSION = "1.8  18Jul20"

#  4 events: 2 recurring, 1 manual, 1 spa off
# version 1.1 added one-shot events to
# prevent one-time on or off events from
# re-triggering 24 hours later. ONCE of RECURRING
# is passed to the call to make an events
#
# to do: when converting events to objects, the type
# needs to be part of the item
#

from datetime import timedelta
import time

import config as c
import globalVars as gv
import equipment
import log
import lcd



# module constants
OFF       = c.OFF
ON        = c.ON
UNK       = c.UNK
ERROR     = c.ERROR
NOERROR   = c.NOERROR
ONCE      = c.ONCE
RECURRING = c.RECURRING

NO_EVENT       = 0
PUMP_ON_EVENT  = 1
PUMP_OFF_EVENT = 2
SPA_OFF_EVENT  = 3
UNKNOWN_EVENT  = 4


# module globals
# init time to the past
zeroTime = 0    # timedelta(hours=0, minutes=0)

pumpOnTime1   = zeroTime
pumpOffTime1  = zeroTime
pumpOnTime2   = zeroTime
pumpOffTime2  = zeroTime
pumpOnTime3   = zeroTime
pumpOffTime3  = zeroTime

spaOffTime = zeroTime
lastPumpOn = 0
nextPumpOffTime = 0



def init():
    clearAllEvents()
    # set timer event 1 and 2 from config
    setPumpTimerEvent(1, c.event1[0], c.event1[1], c.event1[2], RECURRING)
    setPumpTimerEvent(2, c.event2[0], c.event2[1], c.event2[2], RECURRING)
    return




def timeNow():
    # returns a timeDelta object
    ts = time.localtime()
    now = timedelta(hours = ts[3], minutes = ts[4], seconds = ts[5])
    return now



def setPumpTimerEvent(num, h, m, dur, type):
    global pumpOnTime1, pumpOffTime1, pumpOnTime2, pumpOffTime2

    # setup event
    if (h >= 0 and h <= 24 and m >= 0 and m < 60):
        if (dur == 0):
            log.log(log.WARNING, "Duration for event %i is 0, skipping" %num)
            return NOERROR

        log.log(log.DEBUG, "Setting Event %i for %i:%i with duration %i" % (num, h, m, dur))

        if (num == 1):
            pumpOnTime1 = timedelta(hours=h, minutes=m)
            pumpOffTime1  = timedelta(hours=h, minutes=m + dur)
            log.log(log.ALWAYS, "setEvent1: pumpOnTime1 = " + str(pumpOnTime1))
            log.log(log.ALWAYS, "setEvent1: pumpOffTime1 = " + str(pumpOffTime1))

        elif (num == 2):
            pumpOnTime2 = timedelta(hours=h, minutes=m)
            pumpOffTime2  = timedelta(hours=h, minutes=m + dur)
            log.log(log.ALWAYS, "setEvent2: pumpOnTime = " + str(pumpOnTime2))
            log.log(log.ALWAYS, "setEvent2: pumpOffTime = " + str(pumpOffTime2))

        elif (num == 3):
            pumpOnTime3 = timedelta(hours=h, minutes=m)
            pumpOffTime3  = timedelta(hours=h, minutes=m + dur)
            log.log(log.ALWAYS, "setEvent3: pumpOnTime = " + str(pumpOnTime3))
            log.log(log.ALWAYS, "setEvent3: pumpOffTime = " + str(pumpOffTime3))
        return NOERROR
    else:
        log.log(log.ERROR, "Error: setEvent Input Error h,m,dur = " + str(h) + "," + str(m) + "," + str(dur))
        return ERROR




# pumpOff events have no start time, pump assumed on and are always considered ONCE.
# Use timer 3 so we don't overwrite the recurring events.
def setPumpOffEvent(hrs, mins):
    global pumpOffTime3, nextPumpOffTime

    if (hrs > 0 or mins > 0):
        ts = time.localtime()
        pumpOffTime3  = timedelta(hours=ts[3] + hrs, minutes=ts[4] + mins)
        nextPumpOffTime = pumpOffTime3
        log.log(log.ALWAYS, "setPumpOffEvent3: Time = " + str(pumpOffTime3))
        return NOERROR
    else:
        log.log(log.ALWAYS, "Error: setPumpOffEvent3 time h = " + str(h) + " t = " + str(t))
        return ERROR


def clearPumpOffEvent():
    global pumpOffTime3, nextPumpOffTime

    pumpOffTime3 = zeroTime
    nextPumpOffTime = zeroTime
    log.log(log.ALWAYS, "pumpOffTime3 cleared")
    return



# spa events have no start time, heater assumed on
# spaOff events are always considered ONCE (i.e. one-shot)
def setSpaOffEvent(hours):
    global spaOffTime

    # event time cannot be 0 or longer than 12 hours
    if (hours > 0 and hours < 12):
        ts = time.localtime()
        spaOffTime  = timedelta(hours=ts[3] + hours, minutes=ts[4])
        log.log(log.ALWAYS, "setSpaOffEvent:  = " + str(spaOffTime))
        return NOERROR

    else:
        log.log(log.ERROR, "Error: setSpaEvent Input Error hrs = " + str(hrs))
        return ERROR



# increase spaOff events by 1 hour
def incSpaOffTime():
    global spaOffTime

    # event time cannot be 0 or longer than 12 hours
    ts = time.localtime()
    spaOffTime += timedelta(hours=1)
    log.log(log.ALWAYS, "incSpaOff:  = " + str(spaOffTime))
    return NOERROR



def checkEvents():
    global spaOffTime, pumpOnTime1, pumpOffTime1, pumpOnTime2, pumpOffTime2
    global pumpOnTime3, pumpOffTime3, lastPumpOn, nextPumpOffTime

    # get local time
    now = timeNow()
    #log.log("Checking events at " + str(now))

    # timer events return non-zero if executed
    # ----------- timer set 1 ------------------
    if (pumpOnTime1 == now):
        log.log(log.ALWAYS, "PumpOnEvent1 fired")
        if (gv.pumpPower == OFF):
            equipment.pumpPower(ON)
            lastPumpOn = pumpOnTime1
            nextPumpOffTime = pumpOffTime1
            return 1

    if (pumpOffTime1 == now):
        log.log(log.ALWAYS, "PumpOffEvent1 fired")
        # don't turn off if in spa mode
        if (gv.systemMode != c.SPA_ON):
            equipment.pumpPower(OFF)
            nextPumpOffTime = zeroTime
            return 2


    # ------------timer set 2 -----------------
    if (pumpOnTime2 == now):
        log.log(log.ALWAYS, "PumpOnEvent2 fired")
        if (gv.pumpPower == OFF):
            equipment.pumpPower(ON)
            lastPumpOnTime = pumpOnTime2
            nextPumpOffTime = pumpOffTime2
            return 3

    if (pumpOffTime2 == now):
        log.log(log.ALWAYS, "PumpOffEvent2 fired")
        # don't turn off if in spa mode
        if (gv.systemMode != c.SPA_ON):
            equipment.pumpPower(OFF)
            nextPumpOffTime = zeroTime
            return 4



    # --------- set 3 manual or cooldown mode -------------------
    # timer 3 has no on time event
    if (pumpOffTime3 == now):
        log.log(log.ALWAYS, "PumpOffEvent3 fired")
        # if (gv.pumpPower == ON):
        equipment.pumpPower(OFF)
        lastPumpOn = zeroTime
        nextPumpOffTime = zeroTime
        # clear event to prevent a retrigger
        pumpOffTime3 = zeroTime
        return 6


    # ----------- spa off event -----------------

    if (spaOffTime == now):
        log.log(log.ALWAYS, "SpaOffEvent fired")
        equipment.heaterEnable(OFF)
        equipment.heaterPower(OFF)

        # set pump off time & clear event
        setPumpOffEvent(0, 15)
        log.log(log.ALWAYS, "PumpOffEvent3 set")
        spaOffTime = zeroTime
        lcd.message("Pump will remain on for 15 minutes for cooldown")
        time.sleep(10)
        return 5


    # if nothing happened, return 0 (future)
    return 0




def clearAllEvents():
    global pumpOnTime1, pumpOffTime1, pumpOnTime2, pumpOffTime2
    global spaOffTime, pumpOnTime3, pumpOffTime3

    pumpOnTime1   = zeroTime
    pumpOffTime1  = zeroTime
    pumpOnTime2   = zeroTime
    pumpOffTime2  = zeroTime
    pumpOnTime3   = zeroTime
    pumpOffTime3  = zeroTime

    log.log(log.INFO, "All Events Cleared")
    return



def getTimeRemaining():
    global nextPumpOffTime, spaOffTime

    t1 = timeNow()
    remainingTime = "--:--:--"
    gv.remainingTime = remainingTime


    if (gv.systemMode == c.SPA_ON):
        if (spaOffTime == 0):
            return remainingTime
    else:
        if(nextPumpOffTime == 0):
            return remainingTime

    if (gv.systemMode == c.PUMP_ON):
        remaining = nextPumpOffTime - t1
        gv.remainingTime = str(remaining)
        return str(remaining)

    elif (gv.systemMode == c.SPA_ON):
        remaining = spaOffTime - t1
        gv.remainingTime = str(remaining)
        return str(remaining)

    elif (gv.systemMode == c.COOLDOWN):
        remaining = nextPumpOffTime - t1
        gv.remainingTime = str(remaining)
        return str(remaining)

    elif (gv.systemMode == c.MANUAL):
        remaining = nextPumpOffTime - t1
        gv.remainingTime = str(remaining)
        return str(remaining)

    return remainingTime



def setTimeRemaining(offTime):
    global lastPumpOn, nextPumpOffTime

    ts = time.localtime()
    now = timedelta(hours = ts[3], minutes = ts[4])
    lastPumpOn = now
    nextPumpOffTime = timedelta(hours = ts[3], minutes = ts[4] + offTime)
    return




#-------------------------------------------------------------------------------

if __name__ == '__main__':

    init()
    checkEvents()
    print("done")

