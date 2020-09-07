#!/usr/bin/python
#
# utility file for holding misc shit
#
#   last updated:  11-26-19
#


import io
import os
import sys


import config as c
import globalVars as gv
import log
import time
import equipment



# module constants
OFF     = c.OFF
ON      = c.ON
UNK     = c.UNK
ERROR   = c.ERROR
NOERROR = c.NOERROR

# globals



def checkCPUtemp():

    tFile = open('/sys/class/thermal/thermal_zone0/temp', 'r')
    temp = float(tFile.read())
    tempC = round(temp / 1000.0, 1)
    tFile.close()

    log.log(log.DEBUG, "CPU temp = " + str(tempC) + " degC")

    gv.cpuTemp = tempC
    return tempC




# debug tool to exit main loop
def fileExists():
    f = '/home/pi/sdpp'
    if (os.path.exists(f)):
        os.remove(f)
        return True
    else:
        return False


def shutdown():
    log.log(log.WARNING, "*** Shutting Down in 60 seconds...")
    time.sleep(2)
    os.system("sudo shutdown -h +1")
    gv.loop = False
    return


def reboot():
    log.log(log.WARNING, "*** Rebooting in 60 seconds ***")
    time.sleep(2)
    os.system("sudo shutdown -r +1")
    gv.loop = False
    return



# ----- main ------------------------------------------------
if __name__ == '__main__':
    log.init()
    equipment.init()
    count = 0
    print ("fileExists = " + str(fileExists()))
    print
    while (count < 10):
        t = checkCPUtemp()
        print("CPU = " + str(t) + " degsC")
        time.sleep(3)
        count += 1
        print()

    print("done")
