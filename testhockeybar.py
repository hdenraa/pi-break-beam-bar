#!/usr/bin/env python3
import time
#import utime
import random
import RPi.GPIO as GPIO
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import show_message, text
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
from luma.led_matrix.device import max7219
from multiprocessing import Process
import threading
import os
import tm1637
tm = tm1637.TM1637(clk=3, dio=2)

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial,width=160,hight=8, block_orientation=-90)

device.persist = False

BEAM_PINS = [17,27,22,23,24]
target=None
p=None
targetlist=[1,2,3,4,5]
menuc=0
timeup = False

device.cleanup()



tpmap= {17:1,
        27:2,
        22:3,
        23:4,
        24:5}

def menu_callback(channel):
    global menuc
    menuc = tpmap[channel] - 1
    print("menuc:" + str(menuc))


def settarget(target,d):
    global p
    if target == 1:
        p0=(0,0)
        p1=(31,7)
    elif target==2:
        p0=(32,0)
        p1=(63,7)
    elif target==3:
        p0=(64,0)
        p1=(95,7)
    elif target==4:
        p0=(96,0)
        p1=(127,7)
    elif target==5:
        p0=(128,0)
        p1=(159,7)

    with canvas(d) as draw:
        #time.sleep(5)
        draw.rectangle([p0,p1], outline="white", fill="white")

    time.sleep(0.5)
    for i in range(32):
        with canvas(d) as draw:
            draw.rectangle([p0, (p1[0]-i,p1[1])],fill="white")
        time.sleep(0.0625)

    with canvas(d) as draw:
            draw.rectangle([p0, p1],fill="black")

    print("target:"+str(target))

    #if p is not None:
    #    p.terminate()


GPIO.setmode(GPIO.BCM)


for pin in BEAM_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=menu_callback)

for t in range(5):
	settarget(t+1,device)
        
while True:
	time.sleep(0.1)
   
##GPIO.cleanup()
print("Game over")
