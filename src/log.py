#!/usr/bin/python
#
# interface to logger module
#
#  version 1.1 10-01-18
#
# minimum log level = 3
#

import logging
import logging.handlers
import time



# constants
CRITICAL = 50   # always log
ERROR    = 40   # always log
ALWAYS   = 35   # always log
WARNING  = 30   # always log
INFO     = 20   # option
DEBUG    = 10   # option


LOG_PATH = "/home/pi/logs/"
LOG_FILENAME = LOG_PATH + "pool.log"
LOG_FILESIZE = 1024 * 32  # 32K file
LOG_FILECOUNT = 5
LOG_LEVEL = WARNING
PRINT_LEVEL = ERROR


# module globals
logger = 0

def init():
    global logger

    # create main logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    # create rotating file handler
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=LOG_FILESIZE, backupCount=LOG_FILECOUNT)

    # set format
    f = logging.Formatter('%(process)d %(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(f)

    # add custom log level for items that should always be logged
    logging.addLevelName(45, "ALWAYS")
    # add handler
    logger.addHandler(handler)

    return



def log(level, msg):
    global logger

    if (level >= PRINT_LEVEL):
        print(level, msg)

    #msg += "<br />"
    logger.log(level, msg)
    return



def showLog():
    with open(LOG_FILENAME, 'rt') as f:
        body = f.read()
    print("Log name = " + LOG_FILENAME)
    print(body)
    print
    return



def test(num):
    print("logging %i messages..." % num)
    for i in range(num):
        log(4, "this is a logger test message # " + str(i))
        time.sleep(0.01)
    print("done")



#--------------------------------------------------

if __name__ == '__main__':


    init()
    test(200)
    showLog()
