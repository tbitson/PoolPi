import datetime
import redis
import globalVars as gv
import config as cfg
import log
import timer
import equipment as equip
import owTemp as ow
import power



## module constants
OFF     = 0
ON      = 1
UNK     = -1
ERROR   = 1
NOERROR = 0
CCW     = 1
CW      = 0

VALVE_POOL_MODE  = 0  # CW, CW
VALVE_SPA_MODE   = 1  # CCW, CCW
VALVE_FILL_MODE  = 2  # CW, CCW
VALVE_DRAIN_MODE = 3  # CCW, CW



# globals
r = 0   #redis.Redis(host='localhost', port=6379, db=0)



def init():
    global r

    r = redis.Redis(host='localhost', port=6379, db=0)
    log.log(log.ALWAYS, "redis init")
    return



def setStatus():
    global r

    r.set('at',gv.airTemp)
    r.set('st',gv.spaTemp)
    r.set('sp',gv.spaSetPoint)
    r.set('sm',cfg.MODE_NAMES[gv.systemMode])
    r.set('pp',gv.pumpPower)
    r.set('hp',gv.heatPower)
    r.set('he',gv.heatEnable)
    r.set('vm',gv.valveMode)
    r.set('tr',timer.getTimeRemaining())
    #printStatus()
    print("Redis Status Updated")
    return


def setInfo():
    global r

    ts ='{0:%m-%d-%y %H:%M:%S}'.format(datetime.datetime.now())
    batteryCharge = str(power.getChargeLevel()) + "%"
    powerMode = str(power.getPowerState())

    try:
        bashCommand = "uptime"
        uptime = subprocess.check_output(['bash','-c', bashCommand])
        uptime = "current time = " + uptime
        log.log(log.DEBUG, uptime)
    except:
        uptime ="error"

    r.set('te1on',str(timer.pumpOnTime1))
    r.set('te1off',str(timer.pumpOffTime1))
    r.set('te2on',str(timer.pumpOnTime2))
    r.set('te2off',str(timer.pumpOffTime2))
    r.set('te3off',str(timer.pumpOffTime3))
    r.set('tsot',str(timer.spaOffTime))
    r.set('lpo',str(timer.lastPumpOn))
    r.set('npo',str(timer.nextPumpOffTime))

    r.set('pjbc',gv.charge)
    r.set('pjs',powerMode2str(powerMode))

    r.set('ttr',"True")
    r.set('cput',gv.controllerTemp)

    r.set('owsd',ow.getDeviceID(0))
    r.set('owcd',ow.getDeviceID(1))
    r.set('owad',ow.getDeviceID(2))
    r.set('owse',str(gv.owSpaErrors))
    r.set('owce',str(gv.owCntrlErrors))
    r.set('owae',str(gv.owAirErrors))


    r.set('pjv', gv.pjfwVersion)
    r.set('pjbc',gv.charge)
    r.set('pjs', gv.powerStatus)

    r.set('swv',cfg.VERSION)
    r.set('cpus',uptime)
    print("Redis Debug Updated")
    return






def printStatus():
  global r

  print('st = ' + r.get('st'))
  print('at = ' + r.get('at'))
  print('sp = ' + r.get('sp'))
  print('sm = ' + r.get('sm'))
  print('pp = ' + r.get('pp'))
  print('hp = ' + r.get('hp'))
  print('he = ' + r.get('he'))  
  print('vm = ' + r.get('vm'))
  print('tr = ' + r.get('tr'))
  print()
  return



  # --- helpers ------------------------------------------


def status2str(mode):
    if (mode == OFF):
        return "Off"
    elif (mode == ON):
        return "On"
    else:
        return "UNK"




def powerMode2str(mode):
    if (mode == power.AC_POWER):
        return "AC Power"
    elif (mode == power.BATTERY_POWER):
        return "Battery Power"
    else:
        return "Unknown"

  
  #-------------------------------------------------

if __name__ == '__main__':

    log.init()
    print("redis main")
    init()
    setStatus()
    printStatus()
    print("done")
