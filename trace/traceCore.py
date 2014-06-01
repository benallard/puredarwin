from random import randrange
from myhdl import *

from puredarwin.Core import Core

from puredarwin import MARSparam

def tracebench():

    pc_i, raddr_i, waddr_i = [Signal(intbv(0, min=0, max=MARSparam.CORESIZE)) for i in range(3)]
    din_i, dout_i = [Signal(intbv(0)[MARSparam.InstrWidth:]) for i in range(2)]
    we_i = Signal(intbv(0)[6:])
    clk_i, rst_n_i = [Signal(bool(False)) for i in range(2)]

    dut = Core(pc_i, waddr_i, din_i, raddr_i, dout_i, we_i, clk_i, rst_n_i, maxSize=MARSparam.CORESIZE)

    @instance
    def ClkDrv():
        while True:
            clk_i.next = not clk_i
            yield delay(10)

    @instance
    def stimuli():
        yield delay(10)
        for i in range(20):
            we_i.next = randrange(2**6)
            waddr_i.next = randrange(MARSparam.CORESIZE)
            raddr_i.next = randrange(MARSparam.CORESIZE)
            din_i.next = randrange(2**MARSparam.InstrWidth)
            yield delay(20)
        raise StopSimulation

    return dut, ClkDrv, stimuli

if __name__ == "__main__":
    tb = traceSignals(tracebench)
    sim = Simulation(tb)
    sim.run()
