#!/usr/bin/python
#
# menu.py
# lcd menu module for poolPi
# displays the contextual menus on the lcd
# and uses the button module to read responses
#
# NOTE: Cursor home position is 1,1 not 0,0
#
#  version 1.51 04-07-20: fixed manual and
#  and dev modes
#


import time

import config as c
import globalVars as gv
import log
import lcd
import equipment
import power
import buttons
import timer
import util




# module constants
OFF     = c.OFF
ON      = c.ON
UNK     = c.UNK
ERROR   = c.ERROR
NOERROR = c.NOERROR

'''
   ---    ---    ---    ---
  | 1 |  | 2 |  | 3 |  | 4 |
   ---    ---    ---    ---
   RED    YEL    GRN    BLU
'''


BUTTON_1 = 1    # Red - far left
BUTTON_2 = 2    # Yel - middle left
BUTTON_3 = 3    # Grn - middle right
BUTTON_4 = 4    # Blu - far right




#module globals



#---- top/main menu -------------------------------------------------------

def statusDisplay():
    # to minimize flicker, draw each line rather than entire screen
    # each line must be the full lcd width to prevent stray chars
    # use lcd.printLine($, starting pos) to pad each section

    timeStr = time.strftime("%I:%M:%S", time.localtime())
    # get rid of leading zero
    if (timeStr[0] == "0"):
        timeStr = timeStr[1:8]

    lcd.setCursor(1, 1)
    lcd.printLine(timeStr, 10)

    lcd.setCursor(1, 10)
    lcd.printLine("Mode:" + c.MODE_NAMES[gv.systemMode], 10)

    lcd.setCursor(2, 1)
    lcd.printLine("Pump:" + modeToStr(gv.pumpPower), 10)

    lcd.setCursor(2,10)
    #if (gv.powerStatus == power.AC_POWER):
    if (gv.pumpPower == ON):
        lcd.printLine(timer.getTimeRemaining(), 10)
    else:
        lcd.printLine("Bat=" + str(power.getChargeLevel()) + "%", 10)

    lcd.setCursor(3, 1)
    lcd.printLine("Heat:" + modeToStr(gv.heatPower), 10)

    lcd.setCursor(3, 10)
    if (not (gv.systemMode == c.SYS_OFF)):
        lcd.printLine("Temp:" + str(gv.spaTemp), 10)
    else:
        lcd.printLine("Temp:" + str(gv.airTemp), 10)

    lcd.setCursor(4, 1)
    lcd.printLine("Menu  Temp Pump  Spa")
    return




def mainLoopButtons():

    # check for button down
    b = buttons.readButtons()
    if (b == 0):
        return

    # spa button
    if (b == BUTTON_4):
        if (gv.systemMode == c.SPA_ON):
            equipment.spaOff()
        else:
            spaMenuLoop()

    # pump button
    elif (b == BUTTON_3):
        if (gv.pumpPower == ON):
            equipment.pumpPower(OFF)
            timer.clearPumpOffEvent()
        else:
            pumpMenuLoop()

    # temp button
    elif (b == BUTTON_2):
        tempAdjLoop()

    # util menu button
    elif (b == BUTTON_1):
        utilMenuLoop()

    else:
        log.log(log.ERROR, "invalid input for mainLoopButtons")

    return


#---- spa duration menu ---------------------------------------------------------

def spaMenu(hours):
    lcd.clearScreen()
    lcd.setCursor(1,1)
    lcd.printStr("  *** SPA TIME ***  ")
    lcd.setCursor(2,1)
    lcd.printStr("Time = ")
    lcd.printStr(str(hours))
    lcd.printStr(" hours")
    lcd.setCursor(4,1)
    lcd.printLine("Back More Less Start")
    return



def spaMenuLoop():
    hours = c.DEFAULT_DURATION
    exit = False
    spaMenu(hours)

    # handle button press for spa menu
    b = 0
    while(exit == False):
        b = buttons.readButtons()

        # back button
        if (b == BUTTON_1):
            exit = True

        # start button
        elif (b == BUTTON_4):
            equipment.spaOn(hours)
            exit = True

        # less button
        elif (b == BUTTON_2):
            if (hours < 12):
                hours += 1
            spaMenu(hours)

        # more button
        elif (b == BUTTON_3):
            hours -= 1
            if (hours < 1):
                hours = 1
            spaMenu(hours)
    return



#-------pump menu ------------------------------------------------------

def pumpMenu(hours):
    lcd.clearScreen()
    lcd.setCursor(1, 1)
    lcd.printStr(" *** Pump Timer *** ")
    lcd.setCursor(2,1)
    lcd.printStr("Time = ")
    lcd.printStr(str(hours))
    lcd.printStr(" hours")
    lcd.setCursor(4,1)
    lcd.printLine("Back More Less Start")
    return



def pumpMenuLoop():
    hours = 1
    exit = False
    pumpMenu(hours)

    # handle button press for spa menu
    b = 0
    while(exit == False):
        b = buttons.readButtons()

        # back button
        if (b == BUTTON_1):
            exit = True

        # start button
        elif (b == BUTTON_4):
            # turn pump on
            timer.setPumpOffEvent(hours, 0)
            equipment.pumpPower(ON)
            gv.systemMode = c.MANUAL
            exit = True

        # less button
        elif (b == BUTTON_2):
            if (hours < 12):
                hours += 1
            pumpMenu(hours)

        # more button
        elif (b == BUTTON_3):
            if (hours > 1):
                hours -= 1
            pumpMenu(hours)
    return





#---- secondary/util menu ---------------------------------------------------------

def utilMenu():
    lcd.clearScreen()
    lcd.setCursor(1, 1)
    lcd.printLine("1: Clean Spa       ")
    lcd.setCursor(2, 1)
    lcd.printLine("3: Set Spa Temp    ")
    lcd.setCursor(3, 1)
    lcd.printLine("2: Manual Control  ")
    lcd.setCursor(4, 1)
    lcd.printLine("Exit   2    3    4  ")
    return




def utilMenuLoop():
    exit = False
    utilMenu()

    # handle button press for util menu
    while(exit == False):
        b = buttons.readButtons()

        # clean spa button
        if (b == BUTTON_4):
            cleanSpa()
            exit = True

        # spa temp button
        elif (b == BUTTON_3):
            setSpaTempLoop()
            exit = True

        # manual control button
        elif (b == BUTTON_2):
            manualControlLoop()
            utilMenu()

        # back button
        elif (b == BUTTON_1):
            exit = True

    return




#----- clean spa --------------------------------------------
def cleanSpa():
    lcd.clearScreen()
    lcd.setCursor(1,1)
    lcd.printLineCenter("Turning Pump On")
    # turn pump on
    timer.setPumpOffEvent(1, 0)
    equipment.pumpPower(ON)
    v.systemMode = c.MANUAL
    # set valves to drain spa mode
    lcd.clearScreen()
    lcd.setCursor(1,1)
    lcd.printLineCenter("Setting Valves")
    equipment.setValves(c.VALVE_DRAIN_MODE)
    time.sleep(5)
    return






#---- spa temperature menu ---------------------------------------------------------

def setSpaTempMenu():
    lcd.clearScreen()
    lcd.setCursor(1,1)
    lcd.printLineCenter("*** Spa Temp Adjust ***")
    lcd.setCursor(2,1)
    lcd.printLineCenter("Set Point = " + str(gv.spaSetPoint))
    lcd.setCursor(4,1)
    lcd.printLine("Back  +   -   Cancel")
    return



def setSpaTempLoop():
    setSpaTempMenu()
    exit = False

    # handle button press for spa menu
    b = 0
    while(exit == False):
        b = buttons.readButtons()

        # back button
        if (b == BUTTON_1):
            exit = True

        # + button
        elif (b == BUTTON_2):
            if (temp < 105):
                gv.spaSetPoint += 1.0
                setSpaTempMenu()

        # - button
        elif (b == BUTTON_3):
            if (temp > 90):
                gv.spaSetPoint -= TEMP_STEP
                setSpaTempMenu()

        # cancel
        elif (b == BUTTON_4):
            exit = True

        # end while
    return


#---- manual control menu ---------------------------------------------------------

def manualControlMenu():
    lcd.clearScreen()
    lcd.setCursor(1, 1)
    lcd.printLine("1) Pump Control")
    lcd.setCursor(2, 1)
    lcd.printLine("2) Heater Control")
    lcd.setCursor(3, 1)
    lcd.printLine("3) Valve Control")
    lcd.setCursor(4, 1)
    lcd.printLine("Exit  3     2     1 ")
    return


def manualControlLoop():
    exit = False
    manualControlMenu()

    # handle button press
    while(exit == False):
        b = buttons.readButtons()

        # option 1
        if (b == BUTTON_4):
            valveControlLoop()
            manualControlMenu()

        # option 2
        elif (b == BUTTON_3):
            heaterControlLoop()
            manualControlMenu()

        # option 3
        elif (b == BUTTON_2):
            pumpControlLoop()
            manualControlMenu()

        # Back Button
        elif (b == BUTTON_1):
            exit = True

    return
    # end manual control loop





#---- pump control menu ---------------------------------------------------------

def pumpControlMenu():
    lcd.setCursor(1, 1)
    lcd.printLine("4) Pump On         ")
    lcd.setCursor(2, 1)
    lcd.printLine("3) Pump Off        ")
    lcd.setCursor(3, 1)
    lcd.printLine("2)                 ")
    lcd.setCursor(4, 1)
    lcd.printStr("Back  2     3     4 ")
    return


def pumpControlLoop():
    exit = False
    pumpControlMenu()

    # handle button press
    while(exit == False):
        b = buttons.readButtons()

        # option 1
        if (b == BUTTON_4):
            equipment.pumpPower(ON)
            pumpControlMenu()

        # option 2
        elif (b == BUTTON_3):
            equipment.pumpPower(OFF)
            pumpControlMenu()

        # option 3
        elif (b == BUTTON_2):
            pass

        # Back Button
        elif (b == BUTTON_1):
            exit = True

    return
    # end manual control loop




#---- heater control menu ---------------------------------------------------------

def heaterControlMenu():
    lcd.setCursor(1, 1)
    lcd.printLine("4) Heater Power On  ")
    lcd.setCursor(2, 1)
    lcd.printLine("3) Heater Power Off ")
    lcd.setCursor(3, 1)
    lcd.printLine("2) Toggle Heater En ")
    lcd.setCursor(4, 1)
    lcd.printStr("Back   1     2     3 ")
    return


def heaterControlLoop():
    exit = False
    heaterControlMenu()

    # handle button press
    while(exit == False):
        b = buttons.readButtons()

        # option 1
        if (b == BUTTON_4):
            equipment.heaterPower(ON)
            heaterControlMenu()

        # option 2
        elif (b == BUTTON_3):
            equipment.heaterPower(OFF)
            heaterControlMenu()

        # option 3
        elif (b == BUTTON_2):
            if (gv.heatEnable == ON):
                equipment.heaterEnable(OFF)
            else:
                equipment.heaterEnable(ON)

            heaterControlMenu()

        # Back Button
        elif (b == BUTTON_1):
            exit = True

    return
    # end heater control loop



#---- valve control menu ---------------------------------------------------------

def valveControlMenu():
    lcd.setCursor(1, 1)
    lcd.printLine("4) Valves Pool Mode ")
    lcd.setCursor(2, 1)
    lcd.printLine("3) Valves Spa Mode  ")
    lcd.setCursor(3, 1)
    lcd.printLine("2) Valves Drain Mode ")
    lcd.setCursor(4, 1)
    lcd.printLine("Back  2    3    4 ")
    return


def valveControlLoop():
    exit = False
    valveControlMenu()

    # handle button press
    while(exit == False):
        b = buttons.readButtons()

        # option 4
        if (b == BUTTON_4):
            equipment.valveControl(c.VALVE_POOL_MODE)
            lcd.messageTimer("Moving...", 5)
            valveControlMenu()

        # option 3
        elif (b == BUTTON_3):
            equipment.valveControl(c.VALVE_SPA_MODE)
            lcd.messageTimer("Moving...", 5)
            valveControlMenu()

        # option 2
        elif (b == BUTTON_2):
            equipment.valveControl(c.VALVE_DRAIN_MODE)
            lcd.messageTimer("Moving...", 5)
            valveControlMenu()

        # Back Button 1
        if (b == BUTTON_1):
            exit = True

    return
    # end manual valve control loop




#---- dev tools menu TBD ------------------------------------------------

def devToolsMenu():
    lcd.setCursor(1, 1)
    lcd.printLine("1) Manual Control   ")
    lcd.setCursor(2, 1)
    lcd.printLine("2) Exit Program     ")
    lcd.setCursor(3, 1)
    lcd.printLine("3) Power Off        ")
    lcd.setCursor(4, 1)
    lcd.printStr("Back   1     2     3 ")
    return


def devToolsLoop():
    exit = False
    devToolsMenu()

    # handle button press
    while(exit == False):
        b = buttons.readButtons()

        # back button
        if (b == BUTTON_1):
            exit = True

        # option 1
        elif (b == BUTTON_2):
            manualControlLoop()
            exit = true

        # option 2
        elif (b == BUTTON_3):
            if(confirm("Exit ?")):
                gv.loop = False
                exit = True

        # option 3
        elif (b == BUTTON_4):
            if (confirm("Power Off ?")):
                battery.setPowerOff()
                exit = True

    # end dev loop


# -----------------------------------------------------


def confirm(message = ""):

    lcd.clearScreen()
    lcd.setCursor(1,1)
    lcd.printLine(message)
    lcd.setCursor(2,1)
    lcd.printLine("    Continue ?")
    lcd.setCursor(4,1)
    lcd.printLine("Cancel          OK")

    timeout = 0
    while (True):
        b = buttons.readButtons()

        if (b == BUTTON_1):
            return False

        elif (b == BUTTON_4):
            return True

        # check for timeout at ~30 seconds
        timeout += 1
        if (timeout > 3000):
            # timeout returns a cancel
            return False

        # wait 1/10th second, provides good button response
        time.sleep(0.1)
    # end while
    return False





def modeToStr(mode):
    if (mode == 1):
        return "ON "
    elif (mode == 0):
        return "OFF"
    else:
        return "ERROR"


# ----- main ------------------------------------------------

if __name__ == '__main__':
    log.init()
    buttons.init()
    lcd.init()
    mainLoopButtons()
    lcd.clearScreen()
