#!/usr/bin/env python3
from menu import Menu, MenuItem
from board import Board
import time
#import utime
import cProfile
import random
import atexit

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

    def gameover(self):
        print("in gameover")
        show_message(self.device,"Game over",y_offset=0,fill="white",font=self.font)

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
        print("game.setgame")
        print(igame)
        self.currentgame = igame


    def resetscore(self):
        self.sevenseg.write(0,0)

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
        self.display.gameover()
        self.resetscore()
        self.timep.value = 0
        self.timeupp.value = 0
        self.hitcountp.value = 0
        self.hitp.value = 0

    def startgame(self,x):
        pass


class RandT(Game):
    name="RandT"
    def setgame(self,x):
        print("randt.setgame")
        startMenu.setitem(4,MenuItem("Start",self.startgame))
        startMenu.setitem(2,MenuItem(self.name,startMenu.show))
        #self.game.setgame(self)
        #print(self)
        startMenu.show(0)

    def startgame(self,x):
        print("RandT started")

        gametime=10
        self.timeupp.value=0
        self.hitcountp.value=0
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

class RandE(Game):
    name="RandE"

    def __init__(self,display, pins, sevenseg, game):
        self.game = game
        super().__init__(display, pins, sevenseg)

    def setgame(self,x):
        print("rande.setgame")
        #self.setgame(self)
        startMenu.setitem(4,MenuItem("Start",self.startgame))
        startMenu.setitem(2,MenuItem(self.name,startMenu.show))
        #self.game.setgame(self)
        #print(self)
        startMenu.show(0)

    def setscore(self,starttime,gatetime,timeupp,hitcountp):
        while time.time()-starttime<gatetime+1:
            Print("in setscore loop")
            self.sevenseg.write(int(gametime+1-(time.time()-starttime)), 5-hitcountp.value)
            time.sleep(0.5)
        timeupp.value = 1

    def startgame(self,x):
        print("RandE started")

        gatetime=10
        gatepoints=5
        self.timeupp.value=0
        self.p=None


        for pin in self.pins:
            pin.deregisterHandler()
            pin.registerHandler(self.game_callback)

        starttime = time.time()


        timer = Process(target=self.setscore, args=(starttime, gatetime,self.timeupp,self.hitcountp))
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

rande = RandE(ledArray, pins, sevenSeg,game)

game.setgame(randt)

startMenu = Menu(ledArray, pins, [MenuItem("Games", noitem),MenuItem("", noitem),MenuItem(game.currentgame.name, noitem),MenuItem("", noitem),MenuItem("Start", game.currentgame.startgame)])

gameMenu = Menu(ledArray, pins, [MenuItem("RandT", randt.setgame),MenuItem("RandE", rande.setgame),MenuItem("", noitem),MenuItem("", noitem),MenuItem("", noitem)])

startMenu.setitem(0,MenuItem("Games", gameMenu.show))

startMenu.show(0)


# ~ ledArray.write(2, "Hej")
# ~ ledArray.write(3, "med")
# ~ ledArray.write(4, "Hej")



print("Start")
while True:
    time.sleep(5)
