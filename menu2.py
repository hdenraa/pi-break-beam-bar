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
chit=0
timeup = False


tpmap= {17:1,
        27:2,
        22:3,
        23:4,
        24:5}

hitcount = 0


def beam_callback(channel):
    global chit
    chit = tpmap[channel]


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

    if p is not None:
       p.terminate()

def menufunc():
    global BEAM_PINS,chit,targetlist
    gamevar = randt_gamefunc
    currentgame = "Rand E"
    menustate = "Init"
    menudict =  {
                 "Init": ["Games","",currentgame,"Setup","Start"],
                 "Games": ["Rand T","Rand E","Seq","",""],
                 "Setup": ["Sound","Time","","",""],
                 "Start": ["","","","",""],
                 "Rand T": randt_gamefunc,
                 "Rand E": randt_gamefunc,
                 "Seq":randt_gamefunc
                 }

    chit = 0
    for pin in BEAM_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=menu_callback)

    # ~ with canvas(device) as draw:
        # ~ for mitem in range(5):
            # ~ text(draw, (32*mitem, 0), menudict[menustate][mitem], fill="white", font=proportional(TINY_FONT))

    while True:
        time.sleep(0.1)

        if menustate == "Init":
            ##print("near start")
            ##print(menudict[menustate][chit-1])
            print("In Menu")
            print(chit)
            if menudict[menustate][abs(chit-1)] == "Start":
                print("start")
                gamevar()
                chit=-1
                return


        print(menustate)
        if not callable(menudict[menustate]) and not menustate == "Games" and chit in targetlist:
           menustate=menudict[menustate][chit-1]
           chit = -1
        elif menustate == "Games" and chit in targetlist:
            if menudict[menustate][chit-1] in ["Rand T","Rand E","Seq"]:
                currentgame = menudict[menustate][chit-1]
                menustate = "Init"
                menudict[menustate][2]=currentgame
                gamevar= menudict[currentgame]
                #print(gamevar)

        chit = -1


        if not callable(menudict[menustate]):
            with canvas(device) as draw:
                for mitem in range(5):
                    text(draw, (32*mitem, 0), menudict[menustate][mitem], fill="white", font=proportional(TINY_FONT))



def score_randt(tm, starttime, gametime):
    global hitcount, p, timeup
    while time.time()-starttime<gametime+1:
        tm.numbers(int(gametime+1-(time.time()-starttime)), hitcount)
        time.sleep(0.5)
    timeup = True
    if p is not None:
        p.terminate()

def randt_gamefunc():
    global BEAM_PINS,target,p,targetlist, hitcount,timeup
    timeup=False
    gametime=10
 
    starttime = time.time()


    timer = threading.Thread(target=score_randt, args=(tm, starttime, gametime))
    timer.start()

    while not timeup:
       target=random.choice(targetlist)
       p = Process(target=settarget, args=(target,device,chit,))
       p.start()
       p.join()

    timer.join()

    with canvas(device) as draw:
        text(draw, (64, 0), "Game Over", fill="white", font=proportional(TINY_FONT))
    time.sleep(5)

for pin in BEAM_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=menu_callback)

GPIO.setmode(GPIO.BCM)





while True:
    menufunc()
    for pin in BEAM_PINS:
        GPIO.remove_event_detect(pin)
##GPIO.cleanup()
print("Game over")
