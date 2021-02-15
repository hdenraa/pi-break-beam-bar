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

tm.numbers(99,99)
 
