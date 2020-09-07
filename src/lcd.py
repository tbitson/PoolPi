#!/usr/bin/python
#
# lcd.py
# LC Display module for poolPi
# Displays system status and user
# interface menus on the front panel LCD
# via the Pi serial port
#
#
# version 1.3  04-25-19
#
#
#


import serial
import sys
import time

import config as cfg
import globalVars as gv
import log


# module constants
OFF     = cfg.OFF
ON      = cfg.ON
UNK     = cfg.UNK
ERROR   = cfg.ERROR
NOERROR = cfg.NOERROR
DEBUG_PRINT = False


# module globals
port = 0


#### LCD commands from data sheet ("matrix orbital" cmd set)
# Communication commands
MATRIX_START_MSG = 0xFE
MATRIX_BAUDRATE = 0x39

# text commands
MATRIX_AUTOSCROLL_ON       = 0x51
MATRIX_AUTOSCROLL_OFF      = 0x52
MATRIX_CLEAR               = 0x58
MATRIX_CHANGESPLASH        = 0x40
MATRIX_AUTOWRAPLINE_ON     = 0x43
MATRIX_AUTOWRAPLINE_OFF    = 0x44
MATRIX_SETCURSOR_POSITION  = 0x47
MATRIX_HOME                = 0x48
MATRIX_MOVECURSOR_BACK     = 0x4C
MATRIX_MOVECURSOR_FORWARD  = 0x4D
MATRIX_UNDERLINECURSOR_ON  = 0x4A
MATRIX_UNDERLINECURSOR_OFF = 0x4B
MATRIX_BLOCKCURSOR_ON      = 0x53
MATRIX_BLOCKCURSOR_OFF     = 0x54

# special chars
MATRIX_CUSTOM_CHARACTER    = 0x4E
MATRIX_SAVECUSTOMCHARBANK  = 0xC1
MATRIX_LOADCUSTOMCHARBANK  = 0xC0

# display functions
MATRIX_DISPLAY_ON          = 0x42
MATRIX_DISPLAY_OFF         = 0x46
MATRIX_SET_BRIGHTNESS      = 0x99
MATRIX_SETSAVE_BRIGHTNESS  = 0x98
MATRIX_SET_CONTRAST        = 0x50
MATRIX_SETSAVE_CONTRAST    = 0x91

# adafruit specific
MATRIX_RGBBACKLIGHT        = 0xD0
MATRIX_SETSIZE             = 0xD1
MATRIX_TESTBAUD            = 0xD2

# GPIO commands
MATRIX_GPO_OFF             = 0x56
MATRIX_GPO_ON              = 0x57
MATRIX_GPO_START_ONOFF     = 0xC3

# config for this LCD
DEFAULT_CONTRAST           = 0xFF
LCD_WIDTH                  = 20
LCD_HEIGHT                 = 4



def lcdCmd(cmdlist):
    global port

    for i in range(0, len(cmdlist)):
         port.write(chr(cmdlist[i]))
    return



def init():
    global port

    log.log(log.INFO, "opening serial port")

    try:
        # open port at 57600bps with a timeout of 2 seconds
        port = serial.Serial(cfg.PORT_NAME, cfg.BAUD, timeout=2)

    except Exception:
        log.log(log.ERROR, "error opening port")
        return ERROR

    log.log(log.ALWAYS, "opened " + str(port.name))
    time.sleep(0.5)

    # stopped working in latest update
    #port.flush()

    # set screen size to 20 x 4
    lcdCmd([MATRIX_START_MSG, MATRIX_SETSIZE, LCD_WIDTH, LCD_HEIGHT])

    # cursor off
    lcdCmd([MATRIX_START_MSG, MATRIX_UNDERLINECURSOR_OFF])

    # clear screen & home
    clearScreen()
    time.sleep(0.5)

    # set contrast
    setContrast(DEFAULT_CONTRAST)

    # turn on backlight & set color
    setBacklight(ON)
    setColor(gv.lcd_r, gv.lcd_g, gv.lcd_b)

    # set brightness
    setBrightness(0xFF)

    # clear gpio pins
    for i in range(4):
        setGPIO(i, OFF)

    return NOERROR



# print str no formatting
def printStr(s):
    global port

    port.write(s)
    return


# print str with trailing spaces to fill line
# width = lcd width to use for adding spaces
def printLine(s, width=LCD_WIDTH):
    global port

    # add padding to the end
    while (len(s) < width):
        s = s + " "

    port.write(s)
    return


# print str centered
def printLineCenter(s, width=LCD_WIDTH):
    global port

    # add spaces to beginning
    for i in range((width - len(s)) / 2):
        s = " " + s

    printLine(s, width)
    return


# print int
def printInt(i):
    global port
    port.write(str(i))
    return


# print float
def printFloat(f):
    global port
    port.write('{:.1f}'.format(f))
    return




# display message for x seconds
def messageTimer(s1, timer=10):
    clearScreen()
    setCursor(2, 1)
    printStr(s1)
    time.sleep(timer)
    clearScreen()
    return



# display message
def message(s1, s2=""):
    clearScreen()
    setCursor(1, 1)
    printStr(s1)
    setCursor(2, 1)
    printStr(s2)
    return


def clearScreen():
    lcdCmd([MATRIX_START_MSG, MATRIX_CLEAR])
    lcdCmd([MATRIX_START_MSG, MATRIX_HOME])
    time.sleep(0.5)
    return



def clearLine(line):
    global port

    setCursor(line, 1)
    port.write(b"                    ")
    setCursor(line, 1)
    return



def setBacklight(state):
    if (state == ON):
        lcdCmd([MATRIX_START_MSG, MATRIX_DISPLAY_ON, 0x00])
    elif (state == OFF):
        lcdCmd([MATRIX_START_MSG, MATRIX_DISPLAY_OFF])
    else:
        log.log(log.ERROR, "Error - LCD Backlight value undefined")
    return


def setCursor(row, col):
    lcdCmd([MATRIX_START_MSG, MATRIX_SETCURSOR_POSITION, col, row])
    return


def setContrast(value):
    lcdCmd([MATRIX_START_MSG, MATRIX_SET_CONTRAST, value])
    return


def setColor(r, g, b):
    lcdCmd([MATRIX_START_MSG, MATRIX_RGBBACKLIGHT, r, g, b])
    return


def setBrightness(b):
    lcdCmd([MATRIX_START_MSG, MATRIX_SET_BRIGHTNESS, b])
    return


def blink():
	setBacklight(OFF)
	time.sleep(0.1)
	setBacklight(ON)
	return


def setGPIO(gpio, value):

    if (gpio < 0 or gpio > 3):
        log.log(log.ERROR, "setGPIO(): invalid pin: " + str(gpio))
        return

    # output inverted!
    if (value == ON):
        lcdCmd([MATRIX_START_MSG, MATRIX_GPO_OFF, gpio])

    elif (value == OFF):
        lcdCmd([MATRIX_START_MSG, MATRIX_GPO_ON, gpio])

    return



def closePort():
    global port
    try:
        port.close()
        log.log(log.INFO, "port closed")

    except serial.SerialException:
        log.log(log.ERROR, "error closing serial port")
    return




# ----- main ------------------------------------------------
if __name__ == '__main__':

    print ("Starting Test...")
    log.init()
    init()
    printStr("      LCD Test      ")
    time.sleep(2)

    blink()
    time.sleep(1)

    clearScreen()
    setCursor(1, 1)
    printStr("line 1,1")
    time.sleep(1)

    setCursor(2, 10)
    printInt(7734)
    time.sleep(1)

    setCursor(3,1)
    printFloat(3.14159)
    time.sleep(1)

    setCursor(4, 1)
    printLine("Offset 3", 3)
    time.sleep(1)

    clearScreen()
    printStr("Backlight off")
    time.sleep(1)
    setBacklight(OFF)

    clearScreen()
    time.sleep(1)
    printStr("Backlight on")
    setBacklight(ON)
    time.sleep(1)

    clearScreen()
    printStr("Red")
    setColor(255, 0, 0)
    time.sleep(1)

    clearLine(1)
    printStr("Green")
    setColor(0, 255, 0)
    time.sleep(1)

    clearLine(1)
    printStr("Blue")
    setColor(0, 0, 255)
    time.sleep(1)

    setColor(255, 255, 255)
    time.sleep(1)

    clearLine(1)
    printStr("Blink")
    for i in range(3):
        blink()
        time.sleep(1)


    for i in range(4):
        clearLine(1)
        printStr("GPIO %d ON" % i)
        setGPIO(i, ON)
        time.sleep(1)
        clearLine(1)
        printStr("GPIO %d OFF" % i)
        setGPIO(i, OFF)
        time.sleep(1)

    setColor(128, 0, 128)
    clearScreen()

    printStr("complete")
    time.sleep(2)
    clearScreen()

    closePort()
    print("Port Closed")
