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
import os,signal,sys
import tm1637
tm = tm1637.TM1637(clk=3, dio=2)

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial,width=160,hight=8, block_orientation=-90)

BEAM_PINS = [17,27,22,23,24]
target=None
p=None
targetlist=[1,2,3,4,5]
menuc=0
timeup = False


tpmap= {17:1,
        27:2,
        22:3,
        23:4,
        24:5}

hitcount = 0

def signal_handler(sig,frame):
    if p is not None: 
        p.terminate()
    timeup = True
    sys.exit(0)

def randt_callback(channel):
    global target,p,targetlist, hitcount

    print("callback:" + str(tpmap[channel]))
    if tpmap[channel]==target:
        print("hit")
        hitcount+=1
        if p is not None: 
            p.terminate()

def rande_callback(channel):
    global target,p,targetlist, hitcount

    print("callback:" + str(tpmap[channel]))
    if tpmap[channel]==target:
        print("hit")
        hitcount+=1
        if p is not None: 
            p.terminate()
            
def test_callback(channel):
    global target,p,targetlist, hitcount

    print("callback:" + str(tpmap[channel]))
    if tpmap[channel]==target:
        print("hit")
        hitcount+=1
        if p is not None: 
            p.terminate()

def menu_callback(channel):
    global menuc
    menuc = tpmap[channel] - 1
    print(menuc)


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
    global BEAM_PINS,menuc,targetlist
    gamevar = randt_gamefunc
    currentgame = "Rand T"
    menustate = "Init"
    menudict =  {
                 "Init": ["Games","",currentgame,"Setup","Start"],
                 "Games": ["Rand T","Rand E","Seq","","Test"],
                 "Setup": ["Sound","Time","","",""],
                 "Start": ["","","","",""],
                 "Test": selftestfunc,
                 "Rand T": randt_gamefunc,
                 "Rand E": rande_gamefunc,
                 "Seq":randt_gamefunc
                 }
                 
 

    menuc = None
    for pin in BEAM_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=menu_callback)

    # ~ with canvas(device) as draw:
        # ~ for mitem in range(5):
            # ~ text(draw, (32*mitem, 0), menudict[menustate][mitem], fill="white", font=proportional(TINY_FONT))

    while True:
        time.sleep(0.1)
        if menuc is not None:
            if menudict[menustate][menuc] == "":
                time.sleep(0.1)
            elif menustate == "Init":
                ##print("near start")
                ##print(menudict[menustate][menuc-1])
                print("In Menu")
                print(menuc)
                if menudict[menustate][menuc] == "Start":
                    print("start")
                    gamevar()
                    menuc=None
                    return
            
            if not callable(menudict[menustate]) and not menustate == "Games" and menuc +1  in targetlist:
               if not menudict[menustate][menuc] == "":
                  menustate=menudict[menustate][menuc]
                  menuc = None
            elif menustate == "Games" and menuc in targetlist:
                if menudict[menustate][menuc] in ["Rand T","Rand E","Seq","Test"]:
                    currentgame = menudict[menustate][menuc]
                    menustate = "Init"
                    menudict[menustate][2]=currentgame
                    gamevar= menudict[currentgame]
                    #print(gamevar)

            menuc = None


        if not callable(menudict[menustate]):
            with canvas(device) as draw:
                for mitem in range(5):
                    text(draw, (32*mitem, 0), menudict[menustate][mitem], fill="white", font=proportional(TINY_FONT))


def selftestfunc():
    global BEAM_PINS,target,p,targetlist, hitcount,timeup
  
   
    for pin in BEAM_PINS:
        GPIO.remove_event_detect(pin)

    for pin in BEAM_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=test_callback)

    for test in range(5):
       target = test + 1
       p = Process(target=settarget, args=(test+1,device,))
       p.start()
       p.join()

    with canvas(device) as draw:
        text(draw, (64, 0), "Test done", fill="white", font=proportional(TINY_FONT))
    time.sleep(5)

def resetscore():
    tm.numbers(0,0)


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
    resetscore()
    timeup=False
    gametime=10
    for pin in BEAM_PINS:
        GPIO.remove_event_detect(pin)

    for pin in BEAM_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=randt_callback)

    starttime = time.time()


    timer = threading.Thread(target=score_randt, args=(tm, starttime, gametime))
    timer.start()

    while not timeup:
       temptargetlist = targetlist.copy()
       if target is not None:
           temptargetlist.remove(target)
       target=random.choice(temptargetlist)
       p = Process(target=settarget, args=(target,device,))
       p.start()
       p.join()

    timer.join()

    with canvas(device) as draw:
        text(draw, (64, 0), "Game Over", fill="white", font=proportional(TINY_FONT))
    time.sleep(5)

def score_rande(tm, starttime):
    global hitcount, p, timeup, totalhitcount
    gamestarttime = starttime
    timebox = 10
    while (timebox - int(time.time()-starttime)) > 0:
        if hitcount >= 5:
            hitcount = 0
            timebox -= 2
            starttime = time.time()
            print("hitcount nået")
        tm.numbers(timebox-int(time.time()-starttime),5 - hitcount)
        time.sleep(0.5)
    
    tm.numbers((int(time.time()-gamestarttime)//60), int(time.time()-gamestarttime)%60)

    # if hitcount >= 5:
    #     totalhitcount += 5
    # else:
    timeup = True


    if p is not None:
        p.terminate()





def rande_gamefunc():
    global BEAM_PINS,target,p,targetlist, hitcount,timeup
    resetscore()
    timeup=False

    for pin in BEAM_PINS:
        GPIO.remove_event_detect(pin)

    for pin in BEAM_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=rande_callback)

    starttime = time.time()


    timer = threading.Thread(target=score_rande, args=(tm, starttime))
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

signal.signal(signal.SIGINT,signal_handler)

while True:
    menufunc()
    for pin in BEAM_PINS:
        GPIO.remove_event_detect(pin)
##GPIO.cleanup()
print("Game over")
