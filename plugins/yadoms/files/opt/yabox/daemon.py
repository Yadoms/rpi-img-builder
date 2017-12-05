#!/usr/bin/env python
#
# Description : this script manage button and leds of the Yabox
#
# Note : this script must be launch as root (access to GPIO needs root rights)
#
# Used GPIOs :
# - 21 : INPUT(with internal pull-up) : button
# - 20 : OUTPUT : led rouge
# - 26 : OUTPUT : led verte
#

# I/Os PINs
ButtonPin = 21
LedRedPin = 20
LedGreenPin = 26

# Button timings (ms)
ButtonDebounceDuration = 20
ButtonShortPressDuration = 100
ButtonLongPressDuration = 2000


import RPi.GPIO as GPIO
import time
import datetime
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




GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LedRedPin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LedGreenPin, GPIO.OUT, initial=GPIO.LOW)

GPIO.output(LedRedPin, False)
GPIO.output(LedGreenPin, False)

buttonThread = ButtonThread(ButtonDebounceDuration, ButtonShortPressDuration, ButtonLongPressDuration)
buttonThread.start()

while True:
   buttonLongPressed = buttonThread.wait()
   if buttonLongPressed:
      # Long pressed ==> Shutdown
      pass #TODO
   else:
      # Short pressed ==> WPS
      pass #TODO
   
GPIO.cleanup()
