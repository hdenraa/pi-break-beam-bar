#!/usr/bin/env python3
import time
#import utime
import random
import atexit
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

def exit_handler():
    print("exit_handler")
    # GPIO.cleanup()
    device.cleanup()
    
atexit.register(exit_handler)

def signal_handler(sig,frame):
    print("signal_handler")
    # GPIO.cleanup()
    # device.cleanup()
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

game_setup = [
                 {"label":"Rand E",
                  "options": [{"label": "Sound",
                             "value":5,
                             "default":5,
                             "options":[5, 10, 15, 20]},
                            {"label": "time",
                                "value": 20,
                                "default": 10,
                                "options": [10,20, 30]
                            }]},
                 {"label": "Rand T",
                     "options":
                         [{"label": "Sound",
                             "value":5,
                             "default":5,
                             "options":[5, 10, 15, 20]},
                            {"label": "time",
                             "value": 20,
                             "default": 10,
                             "options": [10,20,30]
                            }]}]

game_setup_path = []
game_setup_options = None
game_setup_event = None

def setup_callback(channel):
    global game_setup_path, game_setup_event, game_setup
    
    current_level = game_setup
    for i in game_setup_path:
        print(game_setup_path)
        current_level = current_level[i]
    game_setup_path.append(tpmap[channel] - 1)
    if isinstance(current_level, list):
        if isinstance(current_level[0], map):
            game_setup_action = {"label": "NewLevel",
                                 "options": current_level.options}
        elif isinstance(current_level[0], int):
            game_setup_action = {"label": "PickOption",
                                 "options": current_level.options}
        elif isinstance(current_level, int):
            game_setup_action = {"label": "SetValue",
                                 "options": current_level.options}


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

menudict = None
currentgame = None
gamevar = None

def game_select(igamevar,icurrentgame):
    global gamevar, currentgame, menudict
    gamevar = igamevar
    currentgame = icurrentgame
    menudict["Start"] = gamevar
    menudict["Init"][2] = currentgame
    print("seq_handler")
    print(currentgame)
    print(gamevar)

def menufunc():
    global BEAM_PINS,menuc,targetlist,currentgame,gamevar, menudict
    print("New menu")
    menustate = "Init"
    gamevar = randt_gamefunc
    currentgame = "Rand T"
    menudict =  {
                 "Init": ["Games","Test",currentgame,"Setup","Start"],
                 "Games": ["Rand T","Rand E","Seq","",""],
                 "Setup": lambda: setupfunc(currentgame),
                 "Start": gamevar,
                 "Test": lambda: game_select(selftestfunc,"Test"),
                 "Rand T": lambda: game_select(randt_gamefunc,"Rand T"),
                 "Rand E": lambda: game_select(rande_gamefunc,"Rand E"),
                 "Seq": lambda: game_select(rande_gamefunc,"Seq")
                 }



    menuc = None
    for pin in BEAM_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=menu_callback)

    # ~ with canvas(device) as draw:
        # ~ for mitem in range(5):
            # ~ text(draw, (32*mitem, 0), menudict[menustate][mitem], fill="white", font=proportional(TINY_FONT))
    prevmenu = []
    while True:
        time.sleep(0.1)
        if menuc is not None:
            print("menudict[menustate]" + str(menudict[menustate]))
            if callable(menudict[menustate]):
                print("before call")
                menudict[menustate]()
                menuc=None
                if not menudict[menustate].__name__=="<lambda>": # Start new menu after game is called
                    for pin in BEAM_PINS:
                        GPIO.remove_event_detect(pin)
                    return
                else:
                    print(gamevar)

                print(currentgame)
                menustate="Init"

            else:
                menustate=menudict[menustate][menuc]
                if not callable(menudict[menustate]):
                    menuc = None


        if not callable(menudict[menustate]):
           if not menudict[menustate] == prevmenu:
              with canvas(device) as draw:
                 for mitem in range(5):
                    text(draw, (32*mitem, 0), menudict[menustate][mitem], fill="white", font=proportional(TINY_FONT))
              prevmenu = menudict[menustate]
        time.sleep(0.1)
class gameprops(map):
    pass

def setupfunc(game):
    global game_setup_path, game_setup_event, game_setup
    
    selected = None
    for i in range(len(game_setup)):
        if game_setup[i]["label"] == game:
            selected = game_setup[i]
            game_setup_path = [i]

    game_setup_event = {"label": "NewLevel",
                        "options": selected["options"]}

    for pin in BEAM_PINS:
        GPIO.remove_event_detect(pin)
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=setup_callback)

    while True:
        if game_setup_event["label"] == "NewLevel":
            with canvas(device) as draw:
                for i in range(len(game_setup_event["options"])):
                    text(draw, (32*i, 0), game_setup_event["options"][i]["label"], fill="white", font=proportional(TINY_FONT))
        time.sleep(0.1)



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
    print("randt_gamefunc started")
    global BEAM_PINS,target,p,targetlist, hitcount,timeup
    #resetscore()
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
    print("rande started")
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
GPIO.cleanup()
print("Game over")

##except:
##   print("Error")
    
##finally:
##    GPIO.celanup()
