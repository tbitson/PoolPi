#!/usr/bin/python
#
# buttons.py
# buttons module for poolPi
# reads the front panel buttons and responds to
# user input
#
#
# version 1.4.1   12-29-18  added button modifier capability
#      detect if RED and another button is pressed
#      for now, if RED and BLUE buttons are detected simultaniously,
#      a reboot() is called
#
#  Button Ref:
#   Button 1 = GPIO Pin  6 Red / Modifier
#   Button 2 = GPIO Pin 13 Yellow
#   Button 3 = GPIO Pin 19 Green
#   Button 4 = GPIO Pin 26 Blue
#

import time
import gpiozero as gz
import log
import config
import lcd
import menu
from subprocess import check_call
import globalVars as gv


# constants
ERROR = 1
NOERR = 0



buttons = [0, 0, 0, 0]
altFlag = False

#Aliases not used in this version yet:
Button_1 = buttons[0]
Button_2 = buttons[1]
Button_3 = buttons[2]
Button_4 = buttons[3]

RED = 0
YEL = 1
GRN = 2
BLU = 3

Button_RED = buttons[RED]
Button_YEL = buttons[YEL]
Button_GRN = buttons[GRN]
Button_BLU = buttons[BLU]



def init():
    global buttons

    for i in range(4):
        # set for input, pull-up on, 200ms debounce, 2 sec held time
        buttons[i] = gz.Button(config.BUTTON_PINS[i], pull_up = True, bounce_time = 0.2, hold_time = 2.0, hold_repeat=False)
        log.log(log.DEBUG, "button[" + str(i) + "] init")

        # can this be done without screwing up other stuff?
        # detect button press using a faux interrupt
        # buttons[i].when_pressed = menu.mainLoopButtons


    # alternate shutdown option - hold down button connected to gpio 26 for 5 seconds
    #shutdown_btn = gz.Button(26, hold_time=5)
    #shutdown_btn.when_held = shutdown

    log.log(log.ALWAYS, "Buttons Initialized")
    return NOERR



# depricated - use readButtons
def get():
    return readButtons()


def readButtons():
    global buttons, altFlag

    # clear modifier flag
    gv.buttonModifier = False

    # buttons are pulled up, so active low
    for val in range(4):
        if (buttons[val].is_pressed):
            lcd.blink()

            # if its not the red button, check if red button is also down
            if (not (val == Button_RED)):
                altFlag = buttons[RED].is_pressed

            # wait for button up
            while (buttons[val].is_pressed):
                delay_ms(1)

            if (altFlag == False):
                log.log(log.ALWAYS, "Button %d pressed" %val)
                return val + 1
            else:
                log.log(log.ALWAYS, "Button %d pressed with Alt" %val)
                gv.buttonModifier = True
                # reboot if red & blue buttons are down
                if (val == Button_BLU):
                    util.reboot()
                return (val + 1)

    return 0



'''
todo - doesnt seem to work on Pi
def delay_ns(delay):
    start = time.perf_counter_ns()
    while ((time.perf_counter_ns() - start) > delay):
        pass
    return time.perf_counter_ns() - start
'''


def delay_ms(delay):
    start = time.time() * 1000.0
    while ((time.time() * 1000.0 - start) < delay):
        pass
    return time.time() * 1000.0 - start


#---------------------------------------------------------------------------


if __name__ == '__main__':

    log.init()
    init()

    lcd.init()
    lcd.setCursor(1,1)
    lcd.printStr("Button Test")

    print
    print ("Press a button to test. Button 4 to end")

    val = 0
    loop = True
    while (loop):
        val = readButtons()
        if (val > 0):
            lcd.setCursor(2,1)
            lcd.printStr("Button " + str(val) + "  ")
            print ("Button " + str(val) + " is pressed")
            if (val == 4):
                loop = False
                time.sleep(2)

    lcd.clearScreen()
    lcd.closePort()
