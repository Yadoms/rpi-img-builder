#!/usr/bin/env python
#
# Description : this daemon manage button and leds of the Yabox
#
# Note : this script must be launch as root (access to GPIO needs root rights)
#
# Usage: yabox start|stop|restart
#
# Used GPIOs :
# - 21 : INPUT(with internal pull-up) : button
# - 26 : OUTPUT : led
# - 6 : OUTPUT(INPUT with internal pull-up at power-up) : disable reset function of button
#       This output must be always at HIGH as long as CPU is running.
#       The only chance to have this output LOW is when CPU is stopped. So in this case,
#        and only this one, the button can drive RUN pin low, and restart the CPU.
#

# I/Os PINs
ButtonPin = 21
LedPin = 26
DisableReset = 6

# Button timings (ms)
ButtonDebounceDuration = 20
ButtonShortPressDuration = 100
ButtonLongPressDuration = 5000

# Number of blinks to acknoledge actions
WpsLedBlinkCount = 3
ShutdownLedBlinkCount = 10


import RPi.GPIO as GPIO
import time
import datetime
import logging
import subprocess
import sys
from threading import Timer,Thread,Event
from daemon import Daemon


class ButtonThread(Thread):
   def __init__(self, buttonDebounceDuration, buttonShortPressDuration, buttonLongPressDuration):
      Thread.__init__(self)
      self.__onButtonPressedEvent = Event()
      self.__onButtonLongPress = False
      self.__buttonDebounceDuration = datetime.timedelta(milliseconds = buttonDebounceDuration) # TODO passer en param
      self.__buttonShortPressDuration = datetime.timedelta(milliseconds = buttonShortPressDuration) # TODO passer en param
      self.__buttonLongPressDuration = datetime.timedelta(milliseconds = buttonLongPressDuration) # TODO passer en param

   def run(self):
      buttonPollingInterval = 0.02
      buttonPollingIntervalTimeDelta = datetime.timedelta(seconds = buttonPollingInterval)
      while True:
         GPIO.wait_for_edge(ButtonPin, GPIO.FALLING)
         
         releasedDuration = datetime.timedelta(0)
         totalPressedDuration = datetime.timedelta(0)
         
         while totalPressedDuration < self.__buttonLongPressDuration:
            time.sleep(buttonPollingInterval)
            if GPIO.input(ButtonPin) == 0:
               # Button is pressed
               releasedDuration = datetime.timedelta(0)
               totalPressedDuration = totalPressedDuration + buttonPollingIntervalTimeDelta
            else:
               # Button is released
               releasedDuration = releasedDuration + buttonPollingIntervalTimeDelta
       
            if releasedDuration >= self.__buttonDebounceDuration:
               break;
               
         if totalPressedDuration == self.__buttonLongPressDuration:
            # Button long pressed
            self.__onButtonLongPress = True
            self.__onButtonPressedEvent.set()
            while GPIO.input(ButtonPin) == 0:
               pass
         elif totalPressedDuration > self.__buttonShortPressDuration:
            # Button short pressed
            self.__onButtonLongPress = False
            self.__onButtonPressedEvent.set()
            
   def wait(self):
      self.__onButtonPressedEvent.wait()
      self.__onButtonPressedEvent.clear()
      return self.__onButtonLongPress


def ledBlinkOff(nbTimes):
   while nbTimes > 0:
      GPIO.output(LedPin, False)
      time.sleep(0.1)
      GPIO.output(LedPin, True)
      time.sleep(0.1)
      nbTimes = nbTimes - 1


class YaboxDaemon(Daemon):
   def run(self):
   
      logger = logging.getLogger('yabox')
      loggerHandler = logging.FileHandler('/tmp/yabox.log')
      loggerHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
      logger.addHandler(loggerHandler) 
      logger.setLevel(logging.INFO)

      logger.info("YaboxDaemon started at " + time.strftime("%c"))
      
      GPIO.setmode(GPIO.BCM)
      GPIO.setwarnings(False)

      GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.setup(LedPin, GPIO.OUT, initial=GPIO.LOW)
      GPIO.setup(DisableReset, GPIO.OUT, initial=GPIO.HIGH)

      GPIO.output(LedPin, True)

      buttonThread = ButtonThread(ButtonDebounceDuration, ButtonShortPressDuration, ButtonLongPressDuration)
      buttonThread.start()

      while True:
         logger.info('Wait for button pressed...')
         buttonLongPressed = buttonThread.wait()
         if buttonLongPressed:
            logger.info('Button long pressed ==> Shutdown...')
            ledBlinkOff(ShutdownLedBlinkCount)
            subprocess.call(['shutdown', '-h', 'now'])
         else:
            logger.info('Button short pressed ==> Try to connect WIFI via WPS...')
            ledBlinkOff(WpsLedBlinkCount)
            nbTries = 3
            connected = False
            while nbTries > 0 and not connected:
               connected = True if subprocess.call(['sh', '/opt/yabox/wps-connect.sh']) == 0 else False
               time.sleep(2)
               nbTries = nbTries - 1
            if connected:
               logger.info('Connected')
            else:
               logger.error('Fail to connect')
            
      GPIO.cleanup()
      
                        
if __name__ == "__main__":
   daemon = YaboxDaemon('/tmp/daemon-yabox.pid')
   if len(sys.argv) == 2:
      if 'start' == sys.argv[1]:
         daemon.start()
      elif 'stop' == sys.argv[1]:
         daemon.stop()
      elif 'restart' == sys.argv[1]:
         daemon.restart()
      else:
         print "Unknown command"
         sys.exit(2)
      sys.exit(0)
   else:
      print "usage: %s start|stop|restart" % sys.argv[0]
      sys.exit(2)

                
