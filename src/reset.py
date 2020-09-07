#!/usr/bin/python
#
# reset.py
# stand-alone program to reset all pool equipment
# to a known state quickly. Used with poolPi
#
#
# version 1.61  15Jul20
#
#
#

import gpiozero as gz
import serial
import time



# module constants
# device pins
PUMP_PIN        = 22    # brown wire
HEATER_PIN      = 27    # yellow wire
HEATER_EN_PIN   = 23    # green wire
VALVE_DIR1_PIN  = 17    # blue wire
VALVE_DIR2_PIN  = 24    # white wire
SPARE_RELAY_PIN = 16    # gray wire
LED_PIN         = 20
LED_RTN_PIN     =  8


# constants
OFF = 0
ON  = 1


#module globals



# program start
print "Running Reset  v1.61"

# set up I/O pins
pumpPower      = gz.DigitalOutputDevice(PUMP_PIN,        active_high = True, initial_value = False)
heaterPower    = gz.DigitalOutputDevice(HEATER_PIN,      active_high = True, initial_value = False)
heaterEnable   = gz.DigitalOutputDevice(HEATER_EN_PIN,   active_high = True, initial_value = False)
valveDir1      = gz.DigitalOutputDevice(VALVE_DIR1_PIN,  active_high = True, initial_value = False)
valveDir2      = gz.DigitalOutputDevice(VALVE_DIR2_PIN,  active_high = True, initial_value = False)
sparePower     = gz.DigitalOutputDevice(SPARE_RELAY_PIN, active_high = True, initial_value = False)
activityLed    = gz.DigitalOutputDevice(LED_PIN,         active_high = True, initial_value = False)
activityLedRtn = gz.DigitalOutputDevice(LED_RTN_PIN,     active_high = True, initial_value = False)

# ensure everything is off
pumpPower.off()
heaterPower.off()
heaterEnable.off()
valveDir1.off()
valveDir2.off()
sparePower.off()
activityLed.off()
activityLedRtn.off()

print ("Power is off")

# clear shutdown flag file
try:
    fp = '/home/pi/sdpp'
    if (os.path.exists(fp)):
        os.remove(fp)
except:
    pass

try:
    # open port at 57600bps with a timeout of 1 second
    port = serial.Serial("/dev/serial0", 57600, timeout=1)
    #print ("opened ", port.name)
    port.flush()

    # clear screen & home
    port.write(chr(0xFE))
    port.write(chr(0x58))
    time.sleep(1)

    port.write(chr(0xFE))
    port.write(chr(0x48))

    # set cursor on line 2
    port.write(chr(0xFE))
    port.write(chr(0x47))
    port.write(chr(2))
    port.write(chr(1))
    port.write("  Reset Complete")

    # set color to off
    port.write(chr(0xFE))
    port.write(chr(0xD0))
    port.write(chr(0x00)) # R
    port.write(chr(0x00)) # G
    port.write(chr(0x00)) # B

    # time.sleep(2)
    # port.write(chr(0xFE))
    # port.write(chr(0x58))
    port.close()

except serial.SerialException:
    print ("serial error with lcd")

print ("Reset complete")
