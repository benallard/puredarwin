import unittest
from unittest import TestCase
from random import randrange

from myhdl import Signal, intbv, Simulation, delay, traceSignals, StopSimulation

from Proc import EvalOp

import MARSparam
from MARSparam import InstrWidth
class testEvalOpProperties(TestCase):

    def testAll(self):
        """ Global mapping """

        def test(Modif, Number, Ptr, Wdata, we, Rdata, clk):
            for index in range(200):
                clk.next = False
                yield delay(5)
                Modif.next =index % 8
                num = randrange(MARSparam.CORESIZE)
                Number.next = num
                read = intbv(randrange(2**MARSparam.InstrWidth))
                Rdata.next = read

                clk.next = True
                yield delay(5)
                self.assertEquals(we | intbv("000101"), intbv("000101"))
                self.assert_(Ptr >= 0, "Ptr: %d" % Ptr)
                self.assert_(Ptr < 2*MARSparam.CORESIZE+ 1, "Ptr: %d" % Ptr)
                val = [0, num,
                       read[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + num,
                       read[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + num - 1,
                       read[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + num + 1,
                       read[MARSparam.AddrWidth:0] + num,
                       read[MARSparam.AddrWidth:0] + num - 1,
                       read[MARSparam.AddrWidth:0] + num + 1]
                self.assertEquals(Ptr, val[int(Modif)])
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
