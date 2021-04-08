from ledarray import LedArray
from menu import Menu, MenuItem
from board import Board
import time
import queue

q = queue.Queue()

ledArray = LedArray(5)
board = Board()
pins = [
    board.getPin(18)
]

def just_print(x):
    print("Just print")
    print(x)
    q.put(game)

def game():
    t = 0
    while t < 2000:
        time.sleep(0.01)
        t += 1
    print("Game over")

def re_assign(pins):
    print("Reassign")
    for pin in pins:
        pin.registerHandler(just_print)


menu = Menu(ledArray, pins, [MenuItem("Test", lambda x: re_assign(pins))])
menu.show(0)
while True:
    game = q.get()
    game()
    time.sleep(0.01)
