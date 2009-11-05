
from myhdl import *

import MARSparam
from MARSparam import *

from random import randrange

from MARS import MARS

def traceMARS(nbWarriors, maxTime):
    """ How does the proc reacts to a basic IMP """  

    @instance
    def test():
        rst_n_i.next = True
        yield delay(2)
        rst_n_i.next = False #reset !
        yield delay(2)
        rst_n_i.next = True
        # run

        print "reseted, let's go !"
        
        clk_i.next = False
        yield delay(5)

        # do something
        req_i.next = True

        clk_i.next = True
        yield delay(5)
        print "|"
        while not ack_i:
            clk_i.next = False
            yield delay(5)
            req_i.next = False
            print "."
            clk_i.next = True
            yield delay(5)

        if draw_i:
            print "Match is a draw"
        else:
            print "Warrior %d won !!!" % Winner_i

        raise StopSimulation
    
    Winner_i = Signal(intbv(0, min=0, max=nbWarriors))
    clk_i, rst_n_i, req_i, ack_i, draw_i = [Signal(bool()) for i in range(5)]

    dut = MARS(clk_i, rst_n_i, req_i, ack_i, draw_i, Winner_i, nbWarriors, maxTime)
    
    return dut, test

if __name__ == "__main__":
    #init(Mice=True)
    tb = traceSignals(traceMARS, 3, 300)
    sim = Simulation(tb)
    sim.run(quiet=1)
