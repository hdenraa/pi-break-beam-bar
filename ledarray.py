from luma.core.interface.serial import spi, noop
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
from luma.core.legacy import show_message, text
from luma.led_matrix.device import max7219
from luma.core.render import canvas

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


if __name__ == "__main__":
    import time
    import cProfile
    import signal
    import os
    pr = cProfile.Profile()
    pr.enable()
    def exit_handler():
        pr.disable()
        pr.print_stats(sort='time')


    def sigint_handler(sig, frame):
        exit_handler()
        os._exit(0)


    signal.signal(signal.SIGINT, sigint_handler)
    la = LedArray(5)
    la.write(0, "Hest")
    signal.pause()
