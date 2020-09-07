#!/usr/bin/python
#
# poolPi - RaspberryPi based pool and spa controller
#
# A programmable swimming pool timer/heater controller for the raspberry pi.
#
#  1.6.0 - addded capability to control valves independantly
#  1.6.1 - bug fix for spa web control logic
#  1.6.2 - fixed timer events so they don't turn off if in spa mode
#
# todo: fix pijuiuce status

VERSION = "PoolPi 1.7.0"
DATE    = "23Jul2020"


import sys
import time
import socket
from threading import Thread

import config as cfg
import globalVars as gv
import log

import power
import equipment
import lcd
import menu
import buttons
import timer
import owTemp as ow
import util
import redispy
import webMain





# module constants
OFF     = cfg.OFF
ON      = cfg.ON
UNK     = cfg.UNK
ERROR   = cfg.ERROR
NOERROR = cfg.NOERROR


#module globals
gv.loop = True

# ---------------------------------------------------


def setup():
    print ("starting Poolpi...")

    log.init()

    log.log(log.ALWAYS, "***********************************")
    log.log(log.ALWAYS, "Starting PoolPi " + VERSION + "  " + DATE)
    log.log(log.ALWAYS, "***********************************")
    cfg.VERSION = VERSION

    # init pijuice to monitor power status
    if (power.init() == ERROR):
        gv.piJuicePresent = False;

    # init equipment control
    if (equipment.init() == ERROR):
        return ERROR

    # init serial and lcd
    if (lcd.init() == ERROR):
        return ERROR

    lcd.setCursor(1,1)
    lcd.printLineCenter(VERSION)
    lcd.setCursor(2,1)
    lcd.printLineCenter(DATE)

    # init buttons
    buttons.init()

    # init event timer
    timer.init()

    # init redis
    redispy.init()

    # start temp sensor thread
    ow.init()
    if (ow.start() == ERROR):
        return ERROR

    log.log(log.ALWAYS, "setup() complete")
    return NOERROR


#-------------------------------------------------

def mainLoop():

    log.log(log.ALWAYS, "poolPi running main loop...")
    lastSecs = 0

    # main loop
    while(gv.loop):
        secs = int(time.mktime(time.localtime()))

        # fast loop (millisecs)
        # respond to button presses quickly
        menu.mainLoopButtons()

        if (gv.webUpdate == True):
            ipc.update()

        # 1 second loop
        if (secs != lastSecs):
            timer.checkEvents()
            power.checkPowerStatus()
            menu.statusDisplay()
            equipment.toggleLED()
            redispy.setStatus()

            # 5 second loop
            if (secs % 5 == 0):
                redispy.setInfo()


            # 10 second loop (move to 60 ?)
            if (secs % 10 == 0):
                if (gv.systemMode == cfg.SPA_ON):
                    ow.thermostat()

            # 60 second loop
            if (secs % 60 == 0):
                util.checkCPUtemp()
                ow.checkForFreeze()

                # dim lcd at night
                if (checkTime(21, 0)):
                   lcd.setBrightness(64)
                elif (checkTime(6, 0)):
                   lcd.setBrightness(255)

                # at midnight, reset 1-wire errors
                if (checkTime(0, 0)):
                   ow.resetErrors()

            # dev use - allows shutdown from console
            # by creating the file 'sdpp' in pi home
            if (util.fileExists()):
                log.log(log.CRITICAL, "*** Exit Loop Detected ***")
                gv.loop = False

        lastSecs = secs
        # make sure processor gets to rest (cpu goes to 100% otherwise ??)
        time.sleep(0.25)

    # end of main loop
    log.log(log.CRITICAL, "exiting loop")
    return



def exitLoop():
    gv.loop = False
    return


def getVersion():
    return VERSION


def checkTime(hours, minutes):
    if (time.localtime()[3] == hours and time.localtime()[4] == minutes):
        return True
    else:
        return False


# -- start mail loop and threads ---------------------------------

def start():
    try:
        if (setup() == NOERROR):
            if(cfg.START_FLASK):
                # start flask as thread
                print("Starting Flask as thread...")
                thread = Thread(target=webMain.start)
                thread.start()
                log.log(log.ALWAYS, "Flask thread started")

            # wait for 1-wire thread to init
            secs = 0
            log.log(log.ALWAYS, "waiting on 1-wire init")
            while (gv.owInitComplete == False):
                time.sleep(1)
                secs = secs + 1
                if (secs > 60):
                    log.log(log.CRITICAL, "Timeout waiting for 1-wire Bus Init")
                    gv.loop = False
                    equipment.shutdown()
                    return

            # start main loop
            gv.loop = True
            mainLoop()
        else:
            print("Error during startup - check logs")
            equipment.shutdown()
            return

    except KeyboardInterrupt:
        gv.loop = False
        log.log(log.CRITICAL, "Keyboard Interrupt detected, exiting");
        equipment.shutdown()

    return


# ----- main ------------------------------------------------

if __name__ == '__main__':

    # program entry point
    # print("Starting main...")
    start()
    # we don't come back here until quitting
    print("goodby!")
