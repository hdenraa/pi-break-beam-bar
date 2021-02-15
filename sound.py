#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import pygame
pygame.init()

pygame.mixer.music.load("sound.wav")
pygame.mixer.music.play()
pygame.event.wait()

GPIO.setmode(GPIO.BOARD)

GPIO.setup(12, GPIO.OUT)

GPIO.output(12, True)
time.sleep(5)
##GPIO.output(12, False)


GPIO.cleanup()
