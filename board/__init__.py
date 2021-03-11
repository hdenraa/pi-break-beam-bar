import RPi.GPIO as GPIO
class Pin:
    pinNum = None
    def __init__(self,pinNum):
        self.pinNum = pinNum
        self.hasCallback = False
        GPIO.setup(self.pinNum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pinNum, GPIO.FALLING, callback=self.handler)
        

    def registerHandler(self, handler):
        self.callback = handler
            
    def handler(self,channel):
        self.callback(channel)

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



if __name__ == "__main__":
    import time
    board = Board()
    p = board.getPin(24)
    p.registerHandler(lambda c: print(c))
    while True:
        time.sleep(0.01)
