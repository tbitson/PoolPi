#!/usr/bin/python
#
# globalVars.py
#
# global variable module for poolPi
# Constants are in ALL_CAPS
# variables are in camelCase
#
#  version 1.6     13Jun2020
#
#

import config as c


# module constants
NOERROR = c.NOERROR
ERROR = c.ERROR
OFF = c.OFF
ON  = c.ON
UNK = c.UNK

# main loop control
loop = True


# status variables
systemMode   = c.SYS_OFF
pumpPower    = UNK
heatPower    = UNK
heatEnable   = UNK
valveMode    = UNK
sparePower   = UNK

# buttons
modifierButton = False

# LCD
lcd_r = 255
lcd_g = 255
lcd_b = 255



# measurement vars
spaTemp        = 0.0
spaSetPoint    = c.DEFAULT_SPA_TEMP
cpuTemp        = 0.0
controllerTemp = 0.0
airTemp        = 0.0
charge         = 0
numEvents      = 0
remainingTime  = "--:--:--"


# 1-wire temperature stuff
sensors = {}
owInitComplete = False
spaSensorEnabled = False
cntrlSensorEnabled = False
airSensorEnabled = False
owSpaErrors = 0
owCntrlErrors = 0
owAirErrors = 0


## pijuice presence/status
pjfwVersion = "---"
powerStatus = UNK
piJuicePresent = True
pijuiceStatus = UNK

## web server stuff
webUpdate = False
