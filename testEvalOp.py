import unittest
from unittest import TestCase
from random import randrange

from myhdl import Signal, intbv, Simulation, delay, traceSignals, StopSimulation

from Proc import EvalOp

import MARSparam

class testEvalOpProperties(TestCase):

    def testAll(self):
        """ Global mapping """

        def test(Modif, Number, Ptr, Wdata, we, Rdata, clk):
            clk.next = False
            yield delay(5)
            for i in range(300):
                # setup signals
                clk.next = True
                yield delay(5)
                # do all the necessary assert
            raise StopSimulation

        Modif_i = Signal(0)
        Number_i, Ptr_i = [Signal(0) for i in range(2)]
        WData_i, RData_i = [Signal(0) for i in range(2)]
        we_i = Signal(0)
        clk_i = Signal(0)

        dut = EvalOp(Modif_i, Number_i, Ptr_i, WData_i, we_i, RData_i, clk_i)
        check = test(Modif_i, Number_i, Ptr_i, WData_i, we_i, RData_i, clk_i)

        sim = Simulation(dut, check)
        sim.run(quiet = 1)

if __name__ == "__main__":
    unittest.main();
