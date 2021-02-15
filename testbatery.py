#!/usr/bin/env python3
import time
#import utime
import random
import RPi.GPIO as GPIO
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from multiprocessing import Process
import os
import tm1637
tm = tm1637.TM1637(clk=3, dio=2)
bf = open("batterytime.txt","w")
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial,width=64,hight=8, block_orientation=-90)
BEAM_PINS = [17,27,22,23,24]

def break_beam_callback(channel):
    global target,p,targetlist, hitcount

    print(str(tpmap[channel]))
    if tpmap[channel]==target:
        print("hit")
        hitcount+=1
        if p is not None:
            p.terminate()


def settarget(target,d):
    global p
    p0=(0,0)
    p1=(31,7)
  
    with canvas(d) as draw:
        #time.sleep(5)
        draw.rectangle([p0,p1], outline="white", fill="white")


 


GPIO.setmode(GPIO.BCM)
for pin in BEAM_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=break_beam_callback)

tm.numbers(99, 99)

starttime = filetime = time.time()
bf.write(str(starttime)+"\n")
bf.close()
while True:
   p = Process(target=settarget, args=(1,device,))
   p.start()
   p.join()
   if time.time()-filetime>600:
	   bf = open("batterytime.txt","a")
	   bf.write(str(time.time())+"\n")
	   bf.close()
	   filetime=time.time()

for pin in BEAM_PINS:
    GPIO.remove_event_detect(pin)

GPIO.cleanup()
