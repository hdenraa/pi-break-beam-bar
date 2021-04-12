#!/usr/bin/env python3
from menu import Menu, MenuItem
from board import Board
import time
import atexit
#import utime
import cProfile
import random
import atexit
from ledarray import LedArray
from multiprocessing import Process,Array,Value
import os,signal,sys
import tm1637
from test import scrolling as test_scrolling

 #########################################################################################
# pr = cProfile.Profile()
# pr.enable()
# def exit_handler():
#     pr.disable()
#     pr.print_stats(sort='time')


# def sigint_handler(sig, frame):
#     exit_handler()
#     os._exit(0)


# signal.signal(signal.SIGINT, sigint_handler)


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
        self.targetp = Value('i',0)

        self.currentgame = RandT

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
        tpmap= {18:5,
                27:4,
                22:3,
                23:2,
                24:1
                }
        print("Gamecallback")
        print(self.target)
        print(self.hitcountp.value)
        print(tpmap[channel])
        if tpmap[channel]==self.targetp.value:
            print("hit")
            self.hitcountp.value+=1
            self.hitp.value=1

    def choosetarget(self,itargetp):
        targetlist = [1,2,3,4,5]
        temptargetlist = targetlist.copy()
        if self.target is not None:
            temptargetlist.remove(self.target)
        itargetp.value=random.choice(temptargetlist)
        self.target=itargetp.value
        print("choosetarget")
        print(self.target)

    def mainloop(self,itargetp):
        while not self.timeupp.value == 1:
            self.choosetarget(itargetp)
            self.hitp.value=0
            self.p = Process(target=self.display.settarget, args=(itargetp.value,self.display.device,self.timeupp,self.hitp))
            self.p.start()
            self.p.join()

    def gameover(self):
        #self.display.gameover()
        self.resetscore()
        self.timep.value = 0
        self.timeupp.value = 0
        self.hitcountp.value = 0
        self.hitp.value = 0

    def startgame(self,x):
        print("startgame")
        pass


class RandT(Game):
    name="RandT"
    def setgame(self,x):
        print("randt.setgame")

        startMenu.setitem(4,MenuItem("Start",self.startgame))
        startMenu.setitem(2,MenuItem(self.name,noitem))
        #self.game.setgame(self)
        #print(self)
        startMenu.show(0)


    def startgame(self,x):
        global gamep
        print("RandT started")
        
        for i in range(len(self.pins)):
            print("register fn randt")
            self.pins[i].registerHandler(self.game_callback)

        gamep = Process(target=self.startgameforreal,args=(self.pins,self.game_callback,self.targetp))
        gamep.start()

    def startgameforreal(self,ipins,igame_callback,itargetp):
        gametime=10
        self.timeupp.value=0
        self.hitcountp.value=0
        self.p=None
        starttime = time.time()
        
        # ~ for i in range(len(ipins)):
            # ~ print("register fn randt")
            # ~ self.pins[i].reRegisterHandler(igame_callback)

        timer = Process(target=self.setscore, args=(starttime, gametime,self.timeupp,self.hitcountp))
        timer.start()

        self.mainloop(itargetp)

        timer.join()

        self.gameover()

        
        # ~ for i in range(len(ipins)):
            # ~ print("reregister menu")
            # ~ self.pins[i].reRegisterHandler(self.pins[i].pincallback)



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
            print("in setscore loop")
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
    board.getPin(24), # games
    board.getPin(23),
    board.getPin(22),
    board.getPin(27), # test
    board.getPin(18) # start
]



# ~ breakBeam1.registerHandler(temp_callback)
# ~ breakBeam2.registerHandler(temp_callback2)

gamep = None

ledArray = LedArray(5)

sevenSeg = SevenSegment()

def noitem(x):
    pass

game = Game(ledArray, pins, sevenSeg)

randt = RandT(ledArray, pins, sevenSeg)

rande = RandE(ledArray, pins, sevenSeg,game)




def test(_):
    test_scrolling(0)
    


startMenu = Menu(ledArray, pins, [MenuItem("Games", noitem),
                                  MenuItem("", noitem),
                                  MenuItem(game.currentgame.name, noitem),
                                  MenuItem("Test", test),
                                  MenuItem("Start", game.currentgame.startgame)])

randt.setgame(randt)

gameMenu = Menu(ledArray, pins, [MenuItem("", noitem),MenuItem("RandT", randt.setgame),MenuItem("RandE", rande.setgame), MenuItem("", noitem), MenuItem("", noitem)])

startMenu.setitem(1, MenuItem("Games", gameMenu.show))

startMenu.show(0)


# ~ ledArray.write(2, "Hej")
# ~ ledArray.write(3, "med")
# ~ ledArray.write(4, "Hej")



print("Before signal.pause()")
while True:
    time.sleep(0.5)
    if gamep and gamep.is_alive():
        gamep.join()
        gamep.terminate()
        startMenu.show(0)
