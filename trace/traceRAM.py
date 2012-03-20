from random import randrange
from myhdl import *

from Core import RAM

import MARSparam

width = 8
depth = 32

def tracebench():

    dout_i = Signal(intbv(0)[width:])
    din_i = Signal(intbv(0)[width:])
    addr_i = Signal(intbv(0, min=0, max=depth))
    we_i = Signal(bool(False))
    rst_n_i = Signal(bool(0))
    clk_i = Signal(bool(0))

    dut = RAM(dout_i, din_i, addr_i, we_i, clk_i, rst_n_i, width, depth)
    
    @instance
    def ClkDrv():
        while True:
            clk_i.next = not clk_i
            yield delay(10)

    @instance
    def stimuli():
        yield delay(10)
        for p in range(3):
            for i in range (10):
                addr_i.next = randrange(depth)
                din_i.next = randrange(2**width)
                we_i.next = True
                yield delay(20)
            we_i.next = False
            #read
            for i in range(10):
                addr_i.next = randrange(depth)
                yield delay(3)
        raise StopSimulation

    return dut, ClkDrv, stimuli

if __name__ == "__main__":
    tb = traceSignals(tracebench)
    sim = Simulation(tb)
    sim.run()
