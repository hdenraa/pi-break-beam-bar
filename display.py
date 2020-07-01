#!/usr/bin/env python

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
import time


serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)
with canvas(device) as draw:
    draw.rectangle([(0, 0), (7,7)], outline="white", fill="white")

d = canvas(device)
print(d)

time.sleep(0.5)

for i in reversed(range(8)):
    with canvas(device) as draw:
        draw.rectangle([(0,0), (7,i)],fill="white")
    time.sleep(0.5)
