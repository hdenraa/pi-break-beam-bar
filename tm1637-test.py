import tm1637
tm = tm1637.TM1637(clk=3, dio=2)
tm.write([127, 255, 127, 127])
