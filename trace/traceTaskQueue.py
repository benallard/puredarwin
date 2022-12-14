from myhdl import *

from puredarwin.Task import TaskQueue

from puredarwin import MARSparam

def tracebench(nbwarriors):

    Warrior_i = Signal(intbv(0, min=0, max=nbwarriors))
    IPin1_i, IPin2_i = [Signal(intbv(0)[MARSparam.AddrWidth:]) for i in range(2)]
    IPout_i = Signal(intbv(0)[MARSparam.AddrWidth:])
    re_i = Signal(bool(False))
    we1_i, we2_i = [Signal(bool(False)) for i in range(2)]
    empty_i = Signal(bool(0))
    clk_i = Signal(bool(0))
    rst_n_i = Signal(bool(0))

    dut = TaskQueue(Warrior_i, IPin1_i, we1_i, IPin2_i, we2_i, IPout_i, re_i, empty_i, clk_i, rst_n_i, nbwarriors)

    @instance
    def ClkDrv():
        while True:
            clk_i.next = not clk_i
            yield delay(10)

    @instance
    def WarriorDrv():
        yield delay(10)
        while True:
            Warrior_i.next = (Warrior_i + 1) % nbwarriors
            yield delay(20)

    @instance
    def stimuli():
        rst_n_i.next = False
        yield delay(3)
        rst_n_i.next = True
        we1_i.next = True
        yield delay(20)
        yield delay(500)
        raise StopSimulation

    return dut, ClkDrv, WarriorDrv, stimuli

if __name__ == "__main__":
    tb = traceSignals(tracebench, 4)
    sim = Simulation(tb)
    sim.run()
