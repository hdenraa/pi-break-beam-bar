class Menu:
    def __init__(self, display, pins, items):
        self.display = display
        self.pins = pins
        self.items = items
        for i in items:
            i.menu = self

    def setitem(self,i,item):
        self.items[i]=item

    def show(self, channel):
        for i in range(len(self.items)):
            self.pins[i].registerHandler(self.items[i].fn)
        for i in range(len(self.items)):
            self.display.write(i, self.items[i].label)

class MenuItem:
    def __init__(self, label, fn):
        self.fn = lambda c: fn(c)
        self.label = label
