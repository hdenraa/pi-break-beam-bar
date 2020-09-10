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

BEAM_PINS = [17,27,22,23,24]
target=None
p=None
targetlist=[1,2,3,4,5]
gametime=10
menuc=0
timeup = False


tpmap= {17:1,
        27:2,
        22:3,
        23:4,
        24:5}

hitcount = 0

def game_callback(channel):
    global target,p,targetlist, hitcount

    print(str(tpmap[channel]))
    if tpmap[channel]==target:
        print("hit")
        hitcount+=1
        if p is not None:
            p.terminate()

def menu_callback(channel):
    global menuc
    menuc = tpmap[channel]
 

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

def menufunc():
    global BEAM_PINS,menuc
    menuc = 0
    
    for pin in BEAM_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=menu_callback)
    
    with canvas(device) as draw:
        text(draw, (64, 0), "Start", fill="white", font=proportional(TINY_FONT))

    while True:
        time.sleep(0.1)
        if menuc == 3:
            gamefunc()
            return

def score(tm, starttime, gametime):
	global hitcount, p, timeup
	while time.time()-starttime<gametime+1:
		tm.numbers(int(gametime+1-(time.time()-starttime)), hitcount)
		time.sleep(0.5)
	timeup = True
	if p is not None:
		p.terminate()   
		        
def gamefunc():
    global BEAM_PINS,target,p,targetlist, hitcount,timeup,gametime
    timeup=False
    for pin in BEAM_PINS:
        GPIO.remove_event_detect(pin)
        
    for pin in BEAM_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=game_callback)   

    starttime = time.time()
 

    timer = threading.Thread(target=score, args=(tm, starttime, gametime))
    timer.start()

    while not timeup:
       target=random.choice(targetlist)
       p = Process(target=settarget, args=(target,device,))
       p.start()
       p.join()

    timer.join()
    
    with canvas(device) as draw:
        text(draw, (64, 0), "Game Over", fill="white", font=proportional(TINY_FONT))
    time.sleep(5)

GPIO.setmode(GPIO.BCM)





while True:    
    menufunc()
    for pin in BEAM_PINS:
        GPIO.remove_event_detect(pin)
##GPIO.cleanup()
print("Game over")
