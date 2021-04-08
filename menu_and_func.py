from ledarray import LedArray
from menu import Menu, MenuItem
from board import Board
import time

ledArray = LedArray(5)
board = Board()
pins = [
    board.getPin(18)
]

def just_print(x):
    print("Just print")
    print(x)

def re_assign(pins):
    print("Reassign")
    for pin in pins:
        pin.registerHandler(just_print)

menu = Menu(ledArray, pins, [MenuItem("Test", lambda x: re_assign(pins))])
menu.show(0)
while True:
    time.sleep(0.01)
