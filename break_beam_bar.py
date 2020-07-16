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

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial,width=64,hight=8, block_orientation=-90)

BEAM_PINS = [17,27,22,23,24]
target=None
p=None
targetlist=[1,2,3,4,5]

tpmap= {17:1,
        27:2,
        22:3,
        23:4,
        24:5}

    

def break_beam_callback(channel):
    global target,p,targetlist

    print(str(tpmap[channel]))
    if tpmap[channel]==target:
        print("hit")
        
        if p is not None:
            p.terminate()
            
  
        

    
    
def settarget(target,d):
    global p
    if target == 1:
        p0=(0,0)
        p1=(7,7)
    elif target==2:
        p0=(8,0)
        p1=(15,7)
    elif target==3:
        p0=(16,0)
        p1=(23,7)
    elif target==4:
        p0=(24,0)
        p1=(31,7)
    elif target==5:
        p0=(32,0)
        p1=(39,7)
        
    with canvas(d) as draw:
        #time.sleep(5)
        draw.rectangle([p0,p1], outline="white", fill="white")
    
    time.sleep(0.5)
    for i in range(8):
        with canvas(d) as draw:
            draw.rectangle([p0, (p1[0],p1[1]-i)],fill="white")
        time.sleep(0.5)    

    with canvas(d) as draw:
            draw.rectangle([p0, p1],fill="black")
    
    print("target:"+str(target))

    #if p is not None:
    #    p.terminate()
            
 
            
GPIO.setmode(GPIO.BCM)
for pin in BEAM_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=break_beam_callback)

starttime = time.time()
while  time.time()-starttime<60:
   target=random.choice(targetlist)   
   p = Process(target=settarget, args=(target,device,))
   p.start() 
   p.join()

for pin in BEAM_PINS:
    GPIO.remove_event_detect(pin)

GPIO.cleanup()
