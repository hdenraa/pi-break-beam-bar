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
from multiprocessing import Process,Array,Value
import os,signal,sys
import tm1637
 #########################################################################################

class LedArray:
    serial = spi(port=0, device=0, gpio=noop())
    textList = ['']*5

    def __init__(self, numberOfBlocks, font = proportional(TINY_FONT)):
        self.device = max7219(self.serial,width=32*numberOfBlocks,hight=8, block_orientation=-90) #,blocks_arranged_in_reverse_order="inreverse")
        self.textList = ['']*numberOfBlocks
        self.font = font

    def write(self, blockNum, itext):
        self.textList[blockNum] = itext
        with canvas(self.device) as draw:
            for mitem in range(len(self.textList)):
                text(draw, (32*mitem, 0), self.textList[mitem], fill="white", font=self.font)

    def clear(self):
        self.device.clear()

    def settarget(self,target,d,timeupp,hitp):
        print("Target")
        print(target)
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

        with canvas(self.device) as draw:
            draw.rectangle([p0,p1], outline="white", fill="white")

        time.sleep(0.5)
        for i in range(32):
            if hitp.value == 1 or timeupp.value == 1:
                hitp.value = 0
                break

            with canvas(self.device) as draw:
                draw.rectangle([p0, (p1[0]-i,p1[1])],fill="white")
            time.sleep(0.0625)

        with canvas(d) as draw:
            draw.rectangle([p0, p1],fill="black")

        print("target:"+str(target))

class SevenSegment:
    def __init__(self):
        self.device = tm1637.TM1637(clk=3, dio=2)

    def write(self,val1,val2):
        self.val1 = val1
        self.val2 = val2

        self.device.numbers(val1,val2)



class Pin:
    pinNum = None
    def __init__(self,pinNum):
        self.pinNum = pinNum
        self.hasCallback = False
        GPIO.setup(self.pinNum, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def registerHandler(self, handler):
        self.deregisterHandler()
        GPIO.add_event_detect(self.pinNum, GPIO.FALLING, callback=handler)
        self.hasCallback = True

    def deregisterHandler(self):
        if self.hasCallback:
            GPIO.remove_event_detect(self.pinNum)

class Board:
    def __init__(self):
        self.pins = []
        GPIO.setmode(GPIO.BCM)

    def getPin(self, pinNum):
        pin = list(filter(lambda p: p.pinNum == pinNum, self.pins))
        if not pin:
            pin.append(Pin(pinNum))
            self.pins = self.pins + pin
        return pin[0]

class Menu:
    def __init__(self, display, pins, items):
        self.display = display
        self.pins = pins
        self.items = items
        for i in items:
            i.menu = self

    def show(self, channel):
        for p in self.pins:
            p.deregisterHandler()
        for i in range(len(self.items)):
            self.pins[i].registerHandler(self.items[i].fn)
        for i in range(len(self.items)):
            self.display.write(i, self.items[i].label)

class MenuItem:
    def __init__(self, label, fn):
        self.fn = lambda c: self.execute(fn)
        self.label = label

    def execute(self,fn):
        fn(0)
        #self.menu.show(0)



class Port:
    def __init__(self, inputs):
        self.inputs = inputs




class Game:
    def __init__(self,display, pins, sevenseg):
        print(display)
        self.display = display
        self.pins = pins
        self.sevenseg = sevenseg
        self.target= None


        self.timep = Value('i',0)
        self.timeupp = Value('i',0)
        self.hitcountp = Value('i',0)
        self.hitp = Value('i',0)

        currentgame = RandT

    def setgame(self,igame):
        self.currentgame = igame


    def resetscore():
        sevenseg.numbers(0,0)

    def setscore(self,starttime, gametime,timeupp,hitcountp):
        while time.time()-starttime<gametime+1:
            self.sevenseg.write(int(gametime+1-(time.time()-starttime)), hitcountp.value)
            time.sleep(0.5)
        timeupp.value = 1

    def game_callback(self,channel):
        tpmap= {17:5,
                27:4,
                22:3,
                23:2,
                24:1}
        if tpmap[channel]==self.target:
            print("hit")
            self.hitcountp.value+=1
            self.hitp.value=1

    def choosetarget(self):
        targetlist = [1,2,3,4,5]
        temptargetlist = targetlist.copy()
        if self.target is not None:
            temptargetlist.remove(self.target)
        self.target=random.choice(temptargetlist)

    def mainloop(self):
        while not self.timeupp.value == 1:
            self.choosetarget()
            self.hitp.value=0
            self.p = Process(target=self.display.settarget, args=(self.target,self.display.device,self.timeupp,self.hitp))
            self.p.start()
            self.p.join()

    def gameover(self):
        show_message(self.display.device,"Game over",y_offset=0,fill=None,font=self.device.font)

    def startgame(self,x):
        pass


class RandT(Game):
    name="RandT"
    def setgame(self,x):
        self.setgame(self)
        startMenu.show(0)

    def startgame(self,x):
        print("RandT started")

        gametime=10
        self.timeupp.value=0
        self.p=None


        for pin in self.pins:
            pin.deregisterHandler()
            pin.registerHandler(self.game_callback)

        starttime = time.time()


        timer = Process(target=self.setscore, args=(starttime, gametime,self.timeupp,self.hitcountp))
        timer.start()

        self.mainloop()

        timer.join()

        self.gameover()

        time.sleep(5)

        startMenu.show(0)

board = Board()

# ~ breakBeam1 = board.getPin(24)
# ~ breakBeam2 = board.getPin(23)

pins = [
    board.getPin(24),
    board.getPin(23),
    board.getPin(22),
    board.getPin(27),
    board.getPin(17)
]



# ~ breakBeam1.registerHandler(temp_callback)
# ~ breakBeam2.registerHandler(temp_callback2)

ledArray = LedArray(5)

sevenSeg = SevenSegment()

def noitem(x):
    pass

game = Game(ledArray, pins, sevenSeg)

randt = RandT(ledArray, pins, sevenSeg)

game.setgame(randt)

gameMenu = Menu(ledArray, pins, [MenuItem("RandT", randt.setgame),MenuItem("Game 2", noitem),MenuItem("", noitem),MenuItem("", noitem),MenuItem("", noitem)])

startMenu = Menu(ledArray, pins, [MenuItem("Games", gameMenu.show),MenuItem("", noitem),MenuItem(game.currentgame.name, noitem),MenuItem("", noitem),MenuItem("Start", game.currentgame.startgame)])

startMenu.show(0)


# ~ ledArray.write(2, "Hej")
# ~ ledArray.write(3, "med")
# ~ ledArray.write(4, "Hej")

print("Start")
while True:
    time.sleep(5)
