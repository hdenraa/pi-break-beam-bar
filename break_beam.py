#!/usr/bin/env python3

import RPi.GPIO as GPIO

BEAM_PINS = [17,27,22,23,24]

def break_beam_callback(channel):
    if GPIO.input(channel):
        print("beam unbroken " + str(channel))
    else:
        print("beam broken " + str(channel))

GPIO.setmode(GPIO.BCM)
for pin in BEAM_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=break_beam_callback)

message = input("Press enter to quit\n\n")
GPIO.cleanup()
