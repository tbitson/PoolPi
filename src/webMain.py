#!/usr/bin/python
#
#
#  webMain - primary web page for equipment control
#
#  version 1.3  23Jul20
#

import time
import datetime
import subprocess
import sys
import logging
import redis

import webControl
from threading import Thread

from flask import Flask,flash,redirect,request,render_template,url_for,session,escape


app = Flask(__name__)

#
# set env:
#  export FLASK_APP=web.py
#  export FLASK_ENV=development
# run server using: flask run --host=0.0.0.0
#
#


# module constants
OFF     = 0
ON      = 1
UNK     = -1
ERROR   = 1
NOERROR = 0
UP      = 1.0
DOWN    = -1.0

VALVE_POOL_MODE  = 0  # CW, CW
VALVE_SPA_MODE   = 1  # CCW, CCW
VALVE_FILL_MODE  = 2  # CW, CCW
VALVE_DRAIN_MODE = 3  # CCW, CW




logFileName = "/home/pi/logs/flask.log"
logFormat='%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=logFormat, filename=logFileName, level=logging.DEBUG)
logging.critical('Web start')


r = redis.Redis(host='localhost', port=6379, db=0)







# main page / default landing page
@app.route('/')
@app.route('/index.html')
def index():
    global r
    
    data = {'at':r.get('at'), 
            'st':r.get('st'),
            'sp':r.get('sp'),
            'sm':r.get('sm'),
            'pp':r.get('pp'),
            'hp':r.get('hp'),
            'he':r.get('he'),
            'vm':r.get('vm'),
            'ts':'{0:%m-%d-%y %H:%M:%S}'.format(datetime.datetime.now()),
            'tr':r.get('tr')}

    return render_template('index.html', data=data)



# status/debug page
@app.route('/status.html')
def status():
    data = {
            'at':r.get('at'), 
            'st':r.get('st'),
            'sp':r.get('sp'),
            'ct':r.get('ct'),
            'sm':r.get('sm'),
            'pp':r.get('pp'),
            'hp':r.get('hp'),
            'he':r.get('he'),
            'vm':r.get('vm'),
                        
            'te1on': r.get('te1on'),
            'te1off':r.get('te1off'),
            'te2on': r.get('te2on'),
            'te2off':r.get('te2off'),
            'te3off':r.get('te3off'),
            'lpo':   r.get('lpo'),
            'npo':   r.get('npo'),
            'tr':    r.get('tr'),

            'pjbc':r.get('pjbc'),
            'pjs': r.get('pjs'),
            
            'owsd':r.get('owsd'),
            'owcd':r.get('owcd'),
            'owad':r.get('owad'),
            'owse':r.get('owse'),
            'owce':r.get('owce'),
            'owae':r.get('owae'),
            
            'swv':r.get('swv'),
            'pjv':r.get('pjv'),
            'cpus':r.get('cpus')  }

    return render_template('status.html', data=data)


@app.route('/tools.html')
def tools():
    # placeholders, not yet used in this version
    d1 = 1
    d2 = 2
    data = {'d1':d1, 'd2':d2}
    return render_template('tools.html', data=data)


@app.route('/login')
def login():
    # placeholders, not used in this version
    return 'login'


@app.route('/logout')
def logout():
    # placeholders, not used in this version
    return 'logout'


@app.route('/logs.html')
def logs():
    # placeholders, not used in this version
    d1 = 1
    d2 = 2
    data = {'d1':d1, 'd2':d2}
    return render_template('logs.html', data=data)



#-----------------------------------------------------------------------


@app.route('/pumpOff/')
def pumpOff():
    webControl.pumpControl(OFF)
    time.sleep(0.5)
    return redirect(url_for('index'))
        
    
@app.route('/pumpOn/')
def pumpOn():
    webControl.pumpControl(ON)
    time.sleep(0.5)
    return redirect(url_for('index'))


@app.route('/spaOff/')
def spaOff():
    webControl.spaControl(OFF)
    time.sleep(0.5)
    return redirect(url_for('index'))


@app.route('/spaOn/')
def spaOn():
    webControl.spaControl(ON)
    time.sleep(0.5)
    return redirect(url_for('index'))


@app.route('/valvesPool/')
def valvesPool():
    webControl.valveControl(VALVE_POOL_MODE)
    time.sleep(0.5)
    return redirect(url_for('index'))


@app.route('/valvesSpa/')
def valvesSpa():
    webControl.valveControl(VALVE_SPA_MODE)
    time.sleep(0.5)
    return redirect(url_for('index'))


@app.route('/incTemp/')
def incTemp():
    webControl.tempControl(UP)
    time.sleep(0.5)
    return redirect(url_for('index'))


@app.route('/decTemp/')
def decTemp():
    webControl.tempControl(DOWN)
    time.sleep(0.5)
    return redirect(url_for('index'))


@app.route('/incTime/')
def incTime():
    webControl.timeAdjust(UP)
    time.sleep(0.5)
    return redirect(url_for('index'))


@app.route('/decTime/')
def decTime():
    webControl.timeAdjust(DOWN)
    time.sleep(0.5)
    return redirect(url_for('index'))


@app.route('/exit')
def exit():
    webControl.exit()
    return 'exiting program'


@app.route('/poweroff')
def powerOff():
    webControl.powerOff()
    # should never get here
    return '<h1>Powering Down...</h1>'


@app.route('/reboot')
def reboot():
    webControl.reboot()
    return '<h1>Rebooting...</h1>'


#---------------------------------------------


def status2str(mode):
    if (mode == OFF):
        return "Off"
    elif (mode == ON):
        return "On"
    else:
        return "UNK"


#---------------------------------------------


def start():
    print("start() - Running webMain without debugger")
    flaskPort=5000
    app.run(host='0.0.0.0', port=flaskPort)
    print("webMain.py exiting")
    return


#---------------------------------------------
if __name__ == '__main__':

    start()
    print("webMain.py exiting")
