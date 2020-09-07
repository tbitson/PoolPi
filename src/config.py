#!/usr/bin/python
#
# config.py
# configuration/constants module for poolPi
#
# Constants are in ALL_CAPS
# variables are in camelCase (see globalVars.py)
#
# CONFIG_VERSION =  "1.5.0  09-23-19"
#

import io
import os
import log



## config version number
VERS_NUM = 163
VERSION = ""

## enable simulator and/or flask
START_FLASK = True
USING_SIM   = True


## options
LOG_LEVEL = 40
DEBUG     = False


## module constants
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


## default schedule / timer settings
# event [start hour, start mins, duration mins]
event1 = [ 9, 0, 120]
event2 = [19, 0, 60]

# default ON duration
DEFAULT_DURATION = 2

## file locations
ROOT_DIR       = "/home/pi/"

# web
WEB_DIR        = ROOT_DIR + "web/"
WEB_FILE       = "index.html"
WEB_FILENAME   = WEB_DIR + WEB_FILE

# logging
LOG_DIR        = ROOT_DIR + "logs/"
LOG_FILE       = "pool.html"
LOG_FILENAME   = LOG_DIR + LOG_FILE
LOG_FILESIZE   = 2500
LOG_FILECOUNT  = 10


## RaspPi GPIO pins for primary equipment
PUMP_PIN        = 22
HEATER_PIN      = 27
HEATER_EN_PIN   = 23
VALVE1_DIR_PIN  = 17
VALVE2_DIR_PIN  = 24
SPARE_PIN       = 16
LED_PIN         = 20
LED_RTN_PIN     =  8

# buttons. and input
ONEWIRE_PIN       = 4
BUTTON_PINS       = [6, 13, 19, 26]


## serial port
BAUD = 57600
PORT_NAME = "/dev/serial0"


## pijuice i2c bus & address
PJ_ADDR = 0x14
PJ_BUS = 0x01
SHUTDOWN_ON_POWER_FAIL = False
AC_POWER = 0
BATTERY_POWER = 1


## System mode (state) definitions (future)
NUM_MODES = 7

SYS_OFF  = 0
PUMP_ON  = 1
SPA_ON   = 2
COOLDOWN = 3
FREEZE   = 4
MANUAL   = 5
STANDBY  = 6  # depricated

MODE_NAMES = ["OFF ", "PUMP", "SPA ", "COOL", "FREZ", "MAN ", "STBY"]


if (USING_SIM):
    ## 1-wire temperature stuff for simulator
    NUM_SENSORS = 3
    SPA_TEMP_SENSOR_ID        = '02161ada6aee'  #0316a15824ff'
    CONTROLLER_TEMP_SENSOR_ID = '0316a13f61ff'
    AIR_TEMP_SENSOR_ID        = '0416a0d902ff'

# the real sensors
else:
    ## 1-wire temperature stuff
    NUM_SENSORS = 3
    SPA_TEMP_SENSOR_ID        = '0416c1da95ff'
    CONTROLLER_TEMP_SENSOR_ID = '0000062aeeb9'
    AIR_TEMP_SENSOR_ID        = '0000053ccec8'


## 1-wire sensor assignments
SPA_TEMP = 0
CONTROLLER_TEMP = 1
AIR_TEMP = 2

ALLOWED_ERRORS = 10
TEMP_SENSOR_NAMES = ["Spa Temp", "Controller Temp", "Air Temp"]


# heater settings
DEFAULT_SPA_TEMP = 93.0
FREEZE_TEMP = 32.0
HEATER_LOCKOUT_TIME = 120
HEATER_DELTA_TEMP = 0.50
HEATER_MIN_TEMP = 90.0
HEATER_MAX_TEMP = 104.0

## event types (future)
EVENT_NONE       = 0
EVENT_PUMP_OFF   = 1
EVENT_PUMP_ON    = 2
EVENT_SPA_OFF    = 3
EVENT_FREEZE_OFF = 4
EVENT_FREEZE_ON  = 5

RECURRING = 1
ONCE = 2



# ----- main ------------------------------------------------
if __name__ == '__main__':


    print("done")
