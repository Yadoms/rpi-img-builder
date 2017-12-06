#!/usr/bin/env python
#
# Description : this script manage button and leds of the Yabox
#
# Note : this script must be launch as root (access to GPIO needs root rights)
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
ButtonLongPressDuration = 2000


import RPi.GPIO as GPIO
import time
import datetime
import subprocess
from threading import Timer,Thread,Event


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


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LedPin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(DisableReset, GPIO.OUT, initial=GPIO.HIGH)

GPIO.output(LedPin, True)

buttonThread = ButtonThread(ButtonDebounceDuration, ButtonShortPressDuration, ButtonLongPressDuration)
buttonThread.start()

while True:
   print 'Wait for button pressed...'
   buttonLongPressed = buttonThread.wait()
   if buttonLongPressed:
      print 'Button long pressed ==> Shutdown...'
      ledBlinkOff(5)
      subprocess.call(['shutdown', '-h', 'now'])
   else:
      print 'Button short pressed ==> Try to connect WIFI via WPS...'
      ledBlinkOff(2)
      nbTries = 3
      connected = False
      while nbTries > 0 and not connected:
         connected = True if subprocess.call('./wps-connect') == 0 else False
         time.sleep(2)
         nbTries = nbTries - 1
      print '[OK] Connected' if connected else '[ERROR] Fail to connect'
      
GPIO.cleanup()
